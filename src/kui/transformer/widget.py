import json
from kui.core.transformer import ProviderDataTransformer


class JSONWidgetDataTransformer(ProviderDataTransformer):

    def nest(self, data: list[dict]):
        nested_data = self.__nest_tree(data)
        formatted_data = self.__format_tree(nested_data)
        return self.__assign_templates(formatted_data)

    def flatten(self, data: list[dict]):
        formatted_data = []

        for root_widget in data:
            for widget in self.__flatten_tree(root_widget, root_widget):
                formatted_data.append(widget)

                for template_widget in self.__parse_template(widget):
                    formatted_data.append(template_widget)

        return formatted_data

    def __flatten_tree(self, root_widget, parent):
        """
        Used to go through widget tree
        and format it back into flat structure.
        """

        widgets = []

        parent["section"] = root_widget.get("section")
        children = parent.get("children", [])

        if "stylesheet" in parent:
            parent["stylesheet"] = json.dumps(parent.get("stylesheet"), indent=4)

        if "children" in parent:
            del parent["children"]

        widgets.append(parent)

        order = 0
        for widget in children:
            order += 1
            widget["order_id"] = order
            widget["parent"] = parent["id"]

            for child_widget in self.__flatten_tree(root_widget, widget):
                widgets.append(child_widget)

        return widgets

    def __parse_template(self, widget: dict):

        template = widget.get("template", {})
        data = []

        for template_section in template.keys():
            section = template.get(template_section, [])
            data += self.__format_template_section(template_section, widget, section)

        if "template" in widget:
            del widget["template"]

        return data

    def __format_template_section(self, section_name: str, widget: dict, section: list[dict]):
        section_id = f"{widget["id"]}__template_{section_name}"
        order = 0

        for segment in section:
            order += 1
            segment["order_id"] = order
            segment["section"] = section_id

        return self.flatten(section)

    def __nest_tree(self, widget_data, parent_id=None):
        """
        Used to recursively collect widgets based on
        parent widget and return a tree structure.
        """

        widgets = []

        for widget in widget_data:
            section_id = widget.get("section")
            widget_id = widget.get("id")
            widget_parent_id = widget.get("parent")
            widget_unique_id = f"{section_id}.{widget_id}"
            widget_unique_parent_id = f"{section_id}.{widget_parent_id}"
            events = widget.get("events", [])

            refresh_events = []
            recursive_refresh_events = []

            # Collect widget events.
            for event in events:
                event_id = event.get("refresh_event_id")
                is_recursive = event.get("refresh_children") == 1

                if is_recursive:
                    recursive_refresh_events.append(event_id)
                else:
                    refresh_events.append(event_id)

            if "events" in widget:
                del widget["events"]

            if len(refresh_events) > 0:
                widget["refresh_events"] = refresh_events

            if len(recursive_refresh_events) > 0:
                widget["recursive_refresh_events"] = recursive_refresh_events

            if widget_unique_parent_id == parent_id or (parent_id is None and widget_parent_id is None):
                children = self.__nest_tree(widget_data, parent_id=widget_unique_id)
                widget["children"] = children

                widgets.append(widget)

        return widgets

    def __format_tree(self, data: list[dict]):
        """
        Used to recursively go through widget tree
        and cleanup/format some of its properties.
        """

        data.sort(key=lambda w: w.get("order_id", 0))

        for widget in data:

            section_id = widget.get("section")
            parent_widget_id = widget.get("parent")
            stylesheet = widget.get("stylesheet")

            # Only show section ID on root widgets.
            if parent_widget_id is not None and section_id is not None:
                del widget["section"]

            # Remove parent widget id.
            if parent_widget_id is not None:
                del widget["parent"]

            # Remove order id.
            if "order_id" in widget:
                del widget["order_id"]

            if stylesheet is not None:
                widget["stylesheet"] = json.loads(stylesheet)

            children = widget.get("children", [])
            formatted_children = self.__format_tree(children)
            widget["children"] = formatted_children

            # No need to show empty children object.
            if len(children) == 0:
                del widget["children"]

        return data

    @staticmethod
    def __assign_templates(data: list[dict]):

        def link_template(segment: dict, target_widget_id: str, area_name: str, widgets: list[dict]):

            for widget in widgets:
                if target_widget_id == widget.get("id"):
                    del segment["section"]

                    template = widget.get("template", {})
                    template_area = template.get(area_name, [])
                    template_area.append(segment)
                    template[area_name] = template_area
                    widget["template"] = template
                    break

                link_template(segment, target_widget_id, area_name, widget.get("children", []))

        template_segments = [segment for segment in data if "__template" in segment.get("section")]

        for segment in template_segments:
            section_id = segment.get("section")
            parent_widget_id, segment_code = section_id.split("__")
            segment_name = segment_code.split("_")[1]

            link_template(segment, parent_widget_id, segment_name, data)
            data.remove(segment)

        return data
