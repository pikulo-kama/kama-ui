from typing import TYPE_CHECKING
import dataclasses
import json

if TYPE_CHECKING:
    from kui.core.controller import WidgetController


@dataclasses.dataclass
class Section:
    section_id: str
    section_label: str
    section_icon: str


class MetadataProvider:
    def provide(self, section_id: str) -> list[WidgetMetadata]:  # noqa
        return []

    @staticmethod
    def _parse_stylesheet(stylesheet_json: str):

        stylesheet_map = json.loads(stylesheet_json)
        stylesheet_string = ""

        for key, value in stylesheet_map.items():
            stylesheet_string += f"{key}: {value};\n"

        return stylesheet_string


class ControllerSectionProvider:
    def provide(self, controller: "WidgetController") -> list[Section]:  # noqa
        return []
