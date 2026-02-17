import os

from kamatr.resource import TextTranslation, TextResource
from kui.core._service import AppService
from kui.core.metadata import WidgetMetadata, RefreshEventMetadata
from kui.core.provider import Section
from kui.holder.xml import XMLHolder, XMLTag
from kui.holder.yaml import YamlHolder
from kui.style.type import KamaComposedColor, KamaColor, KamaFont, DynamicImage
from kui.util.file import get_files_from_directory
from kutil.file import remove_extension_from_path
from kutil.file_type import SVG


class ResourceReader(AppService):
    layout_mapping = {
        "horizontal": "KamaHBoxLayout",
        "vertical": "KamaVBoxLayout",
        "grid": "KamaGridLayout"
    }

    def read(self):

        self.application.style.clear()
        self.application.window.manager.clear()

        self.read_layouts()
        self.read_text_resources()
        self.read_colors()
        self.read_fonts()
        self.read_dynamic_images()

    def read_layouts(self):
        section_data = get_files_from_directory(
            self.application.discovery.layouts(),
            recursive=True,
            extension=".kml"
        )

        for section_xml in section_data:
            section_metadata = XMLHolder(section_xml).root

            if section_metadata.name != "KamaSection":
                raise RuntimeError("KamaSection should be root tag of the layout.")

            if not section_metadata.has("name"):
                raise RuntimeError("KamaSection tag doesn't have name property.")

            section = Section(
                section_id=section_metadata.get("name"),
                section_label=section_metadata.get("label"),
                section_icon=section_metadata.get("icon")
            )

            metadata = self.__get_metadata(section_metadata.children, section.section_id)
            self.application.window.manager.add_section(section, metadata)

    def read_text_resources(self):
        all_translations = {}

        for locale_file in os.listdir(self.application.discovery.Locales):
            locale_name = remove_extension_from_path(locale_file)
            resources = YamlHolder(self.application.discovery.locales(locale_file)).to_flat_json(join_char="_")

            for key, value in resources.items():
                translations = all_translations.get(key, [])
                translations.append(TextTranslation(locale=locale_name, text=value))
                all_translations[key] = translations

        for key, translations in all_translations.items():
            text_resource = TextResource(key, translations)
            self.application.translations.add(text_resource)

    def read_colors(self):
        colors_file_name = self.application.discovery.resources("colors")
        colors = YamlHolder(colors_file_name).to_json()
        color_map = {}

        for theme, theme_colors in colors.items():
            for color_code, color_hex in theme_colors.items():
                variations = color_map.get(color_code, {})
                variations[theme] = color_hex
                color_map[color_code] = variations

        for color_code, variations in color_map.items():
            variations = {theme: KamaColor(color_hex) for theme, color_hex in variations.items()}
            self.application.style.add_color(
                KamaComposedColor(
                    color_code=color_code,
                    variations=variations
                )
            )

    def read_fonts(self):
        fonts_file_name = self.application.discovery.resources("fonts")
        fonts = YamlHolder(fonts_file_name).to_json()

        for font_code, font_properties in fonts.items():
            font_family = font_properties.get("family")
            font_size = font_properties.get("size", 14)
            font_weight = font_properties.get("weight", 400)

            self.application.style.add_font(
                KamaFont(
                    font_code=font_code,
                    font_family=font_family,
                    font_size=font_size,
                    font_weight=font_weight
                )
            )

    def read_dynamic_images(self):
        images_file_name = self.application.discovery.resources("images")
        images: dict[str, dict] = YamlHolder(images_file_name).to_json()

        for image_name, image_properties in images.items():
            image_path = image_properties.get("path", image_name)
            image_color = image_properties.get("color")

            self.application.style.add_dynamic_image(
                DynamicImage(
                    image_name=SVG.add_extension(image_name),
                    image_path=SVG.add_extension(image_path),
                    color_code=image_color
                )
            )

    def __get_metadata(self, tags: list[XMLTag], section_id: str) -> list[WidgetMetadata]:

        metadata = []
        order_id = 0

        for tag in tags:
            parent_id = tag.parent.get("id")

            if tag.name == "Template":
                self.__process_template(tag)
                continue

            widget_id = tag.get("id")
            layout = tag.get("layout")
            classes = tag.get("class", "").split()
            controller_args = {}

            events = tag.get("refresh_events", "").split()
            recursive_events = tag.get("recursive_refresh_events", "").split()

            events_meta = {event: RefreshEventMetadata(True) for event in recursive_events}
            all_events = events + recursive_events

            order_id += 1

            if widget_id is None:
                widget_id = f"{tag.name}_{order_id}"

                if parent_id is not None:
                    widget_id = f"{parent_id}_{widget_id}"

                tag.set("id", widget_id)

            if layout in self.layout_mapping:
                layout = self.layout_mapping.get(layout)

            for arg_key, arg_value in tag.properties.items():
                if not arg_key.startswith("arg_"):
                    continue

                arg_key = arg_key[4:]

                if arg_key.startswith("list_"):
                    arg_key = arg_key[5:]
                    arg_value = arg_value.split()

                controller_args[arg_key] = arg_value

            meta = WidgetMetadata(
                widget_id=widget_id,
                section_id=section_id,
                widget_type=tag.name,
                layout_type=layout,
                grid_columns=tag.get("cols"),
                parent_widget_id=parent_id,
                controller=tag.get("controller"),
                controller_args=controller_args,
                order_id=order_id,
                spacing=tag.get("spacing"),
                width=tag.get("width"),
                height=tag.get("height"),
                margin_left=tag.get("ml"),
                margin_top=tag.get("mt"),
                margin_right=tag.get("mr"),
                margin_bottom=tag.get("mb"),
                alignment_string=tag.get("alignment"),
                content=tag.content,
                tooltip=tag.get("tooltip"),
                stylesheet=tag.get("stylesheet", ""),
                refresh_events=all_events,
                refresh_events_meta=events_meta,
                classes=classes
            )

            metadata.append(meta)
            metadata.extend(self.__get_metadata(tag.children, section_id))

        return metadata

    def __process_template(self, template_tag: XMLTag):
        parent_widget_id = template_tag.parent.get("id")

        for template_area in template_tag.children:
            area_section_id = f"{parent_widget_id}__template_{template_area.name.lower()}"
            area_metadata = self.__get_metadata(template_area.children, area_section_id)

            self.application.window.manager.add_section(Section(area_section_id), area_metadata)
