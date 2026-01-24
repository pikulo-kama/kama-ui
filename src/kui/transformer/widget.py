import json
from kui.core.transformer import ProviderDataTransformer


class WidgetMetadataTransformer:
    """
    Utility class for normalizing widget metadata structures.

    This transformer maps shorthand or external key names to a standardized
    internal schema. It is typically used during data ingestion to ensure
    consistency across widget-based UI components.
    """

    _KEY_MAPPINGS = {
        "id": "widget_id",
        "type": "widget_type",
        "layout": "layout_type",
        "section": "section_id",
        "parent": "parent_widget_id",
        "style_id": "style_object_name",
        "alignment": "alignment_string",
        "args": "controller_args"
    }

    def transform(self, widgets: list[dict]) -> list[dict]:
        """
        Standardizes keys within a list of widget dictionaries.

        This method iterates through each widget and renames keys based on the
        internal `_KEY_MAPPINGS`. If a key from the mapping is found in a
        widget, it is 'popped' (removed) and re-inserted under its new name.

        Args:
            widgets (list[dict]): A list of dictionaries containing widget
                configuration data.

        Returns:
            list[dict]: The list of modified dictionaries. Note that this
                operation modifies the dictionaries in-place.
        """

        for widget in widgets:
            self.transform_single(widget)

        return widgets

    def transform_single(self, widget: dict) -> dict:
        """
        Standardizes the keys of a single widget dictionary.

        Maps external or shorthand keys to internal schema names defined in
        `_KEY_MAPPINGS`. This operation modifies the input dictionary in-place.

        Args:
            widget (dict): The dictionary containing widget metadata to be transformed.

        Returns:
            dict: The updated dictionary with standardized keys.
        """

        for key, target_key in self._KEY_MAPPINGS.items():
            if key in widget:
                widget[target_key] = widget.pop(key)

        return widget


class JSONWidgetDataTransformer(ProviderDataTransformer):
    """
    Advanced transformer for widget metadata.
    Handles complex nesting, template sections, and event segregation.
    """

    def nest(self, data: list[dict]):
        """
        Transforms flat database records into a nested, template-aware widget tree.

        Args:
            data (list[dict]): Flat list of widget records from a data source.

        Returns:
            list[dict]: A hierarchical tree of widgets with integrated templates.
        """

        nested_data = self.__nest_tree(data)
        formatted_data = self.__format_tree(nested_data)
        return self.__assign_templates(formatted_data)

    def flatten(self, data: list[dict]):
        """
        Flattens a hierarchical widget tree into a format suitable for database storage.

        Args:
            data (list[dict]): The nested widget tree.

        Returns:
            list[dict]: A flat list of dictionaries with parent-child relationships.
        """

        formatted_data = []

        for root_widget in data:
            for widget in self.__flatten_tree(root_widget, root_widget):
                formatted_data.append(widget)

                for template_widget in self.__parse_template(widget):
                    formatted_data.append(template_widget)

        return formatted_data

    def __flatten_tree(self, root_widget, parent):
        """
        Recursively flattens a hierarchical tree of widget dictionaries into a flat list.

        This method traverses a nested widget structure, normalizes individual widget
        attributes, and converts the parent-child nesting into a flat list where
        relationships are maintained via IDs.

        Args:
            root_widget (dict): The top-level reference widget, used to inherit
                global properties like 'section'.
            parent (dict): The current widget being processed in the recursion.

        Returns:
            list: A list of dictionaries, where each dictionary represents a single
                widget with its 'children' removed and metadata (order, parent ID) added.

        Notes:
            - **Defaulting:** If a widget lacks a 'type', it defaults to 'KWidget'.
            - **Serialization:** 'stylesheet' and 'args' fields are converted from
              JSON objects to indented strings.
            - **Relationship Mapping:** The 'children' key is removed from each
              dictionary, and child widgets are assigned a 'parent' ID and an
              incremental 'order_id'.
        """

        widgets = []

        parent["section"] = root_widget.get("section")
        children = parent.get("children", [])
        widget_type_id = parent.get("type")

        # If widget type is not populated - use
        # KWidget as default one.
        if widget_type_id is None:
            parent["type"] = "KWidget"

        # Remove children from final object.
        if "children" in parent:
            del parent["children"]

        # Transform stylesheet and controller
        # arguments JSON into string.
        if "stylesheet" in parent:
            parent["stylesheet"] = json.dumps(parent.get("stylesheet"), indent=4)

        if "args" in parent:
            parent["args"] = json.dumps(parent.get("args"), indent=4)

        widgets.append(parent)

        # Populate order ID and parent widget.
        # Process children of widget.
        order = 0
        for widget in children:
            order += 1
            widget["order_id"] = order
            widget["parent"] = parent["id"]

            for child_widget in self.__flatten_tree(root_widget, widget):
                widgets.append(child_widget)

        return widgets

    def __parse_template(self, widget: dict):
        """
        Parses the 'template' attribute of a widget into a structured data list.

        This method iterates through all sections defined within a widget's template,
        processes them using a formatting helper, and aggregates the results into
        a single flat list. Once parsing is complete, it removes the template
        definition from the original widget object to prevent data redundancy.

        Args:
            widget (dict): The widget dictionary containing a "template" key.
                The template should be a dictionary where keys represent section
                names and values represent section content.

        Returns:
            list: A consolidated list of formatted data objects returned by
                `__format_template_section`.

        Side Effects:
            - Modifies the input `widget` by deleting the "template" key.
        """

        template = widget.get("template", {})
        data = []

        # Process all template sections
        # (header, body, footer)
        for template_section in template.keys():
            section = template.get(template_section, [])
            data += self.__format_template_section(template_section, widget, section)

        # Remove template object after processing.
        if "template" in widget:
            del widget["template"]

        return data

    def __format_template_section(self, section_name: str, widget: dict, section: list[dict]):
        """
        Normalizes and flattens a specific section of a widget's template.

        This method generates a unique identifier for the section, assigns sequence
        ordering to each segment within that section, and ensures each segment
        references its specific section ID. It then delegates the final flattening
        to the 'flatten' method.

        Args:
            section_name (str): The name/key of the template section being processed.
            widget (dict): The parent widget dictionary, used to derive the section's
                unique ID.
            section (list[dict]): A list of segment dictionaries belonging to
                the specified template section.

        Returns:
            list: The result of `self.flatten(section)`, typically a list of
                processed/flattened segment dictionaries.
        """

        section_id = f"{widget["id"]}__template_{section_name}"
        order = 0

        # Populate order ID and
        # section for all root segments
        # of template section.
        for segment in section:
            order += 1
            segment["order_id"] = order
            segment["section"] = section_id

        return self.flatten(section)

    def __nest_tree(self, widget_data, parent_id=None):
        """
        Recursively reconstructs a hierarchical tree structure from a flat list of widgets.

        This method identifies parent-child relationships using composite IDs (section + widget ID).
        It also processes event logic, separating standard refresh events from recursive
        refresh events, and nests child widgets under their respective parents.

        Args:
            widget_data (list[dict]): The flat list of all widget dictionaries to be processed.
            parent_id (str, optional): The unique composite ID of the current parent
                being processed (format: 'section_id.widget_id'). Defaults to None for
                the root level.

        Returns:
            list[dict]: A nested list of widget dictionaries where children are stored
                under the 'children' key of their respective parent.

        Notes:
            - **Composite IDs:** Relationships are determined by matching `section.parent`
              to the provided `parent_id`.
            - **Event Processing:** The 'events' list is consumed and split into
              'refresh_events' and 'recursive_refresh_events' based on the 'refresh_children' flag.
            - **Recursion:** For every widget identified as a child of the current scope,
               the method calls itself to find that widget's own descendants.
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
        Recursively post-processes and cleans up a nested widget tree.

        This method prepares the tree for final output by sorting widgets by their
        original order, deserializing configuration strings (JSON) back into
        objects, and removing internal metadata such as IDs and temporary
        parent references.

        Args:
            data (list[dict]): A list of widget dictionaries (the tree or a
                subtree) to be formatted.

        Returns:
            list[dict]: The cleaned and sorted list of widgets, with processed
                children.

        Notes:
            - **Sorting:** Widgets are sorted based on 'order_id' at every depth level.
            - **Data Restoral:** 'stylesheet' and 'args' are converted from JSON strings
              back into Python dictionaries.
            - **Redundancy Removal:** - 'section' is removed from all but the root widgets.
                - 'parent' and 'order_id' are deleted after they have served their
                  purpose for sorting/nesting.
                - 'type' is removed if it matches the default 'KWidget'.
                - 'children' is deleted if the list is empty.
        """

        data.sort(key=lambda w: w.get("order_id", 0))

        for widget in data:

            section_id = widget.get("section")
            parent_widget_id = widget.get("parent")
            stylesheet = widget.get("stylesheet")
            controller_args = widget.get("args")
            widget_type_id = widget.get("type")

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

            if controller_args is not None:
                widget["args"] = json.loads(controller_args)

            if widget_type_id == "KWidget":
                del widget["type"]

            children = widget.get("children", [])
            formatted_children = self.__format_tree(children)
            widget["children"] = formatted_children

            # No need to show empty children object.
            if len(children) == 0:
                del widget["children"]

        return data

    @staticmethod
    def __assign_templates(data: list[dict]):
        """
        Re-integrates template segments back into their respective parent widgets.

        This method identifies widgets that are marked as template parts (based on
        their 'section' ID), extracts them from the flat list, and uses a recursive
        helper to place them inside the 'template' dictionary of the correct
        target widget.

        Args:
            data (list[dict]): The list of widgets and template segments.

        Returns:
            list[dict]: The cleaned list of widgets with template segments
                moved into the 'template' property of their parents.

        Notes:
            - **Identification:** Segments are identified by the presence of
              '__template' in their 'section' string.
            - **Parsing:** The 'section' ID (e.g., "widget123__template_header") is
              parsed to extract the parent ID ("widget123") and the area name ("header").
        """

        def link_template(segment: dict, target_widget_id: str, area_name: str, widgets: list[dict]):
            """
            Recursively searches the widget tree to find a target parent and
            attach a template segment.

            Args:
                segment (dict): The template segment to move.
                target_widget_id (str): The ID of the widget the segment belongs to.
                area_name (str): The specific area within the template (e.g., 'body', 'footer').
                widgets (list[dict]): The current list of widgets to search through.
            """

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
