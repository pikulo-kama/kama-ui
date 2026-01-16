import dataclasses
import json

from kui.core.filter import KamaFilter
from kui.core.metadata import WidgetMetadata


@dataclasses.dataclass
class Section:
    section_id: str
    section_label: str
    section_icon: str


class MetadataProvider:
    def provide(self, filter: KamaFilter) -> list[WidgetMetadata]:  # noqa
        return []

    @staticmethod
    def _parse_stylesheet(stylesheet_json: str):

        stylesheet_map = json.loads(stylesheet_json)
        stylesheet_string = ""

        for key, value in stylesheet_map.items():
            stylesheet_string += f"{key}: {value};\n"

        return stylesheet_string


class ControllerSectionProvider:
    def provide(self, filter: KamaFilter) -> list[Section]:  # noqa
        return []
