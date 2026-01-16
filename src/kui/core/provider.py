import dataclasses
import json

from kui.core.filter import KamaFilter
from kui.core.metadata import WidgetMetadata


@dataclasses.dataclass
class Section:
    """
    Data container representing a high-level application section.

    Attributes:
        section_id (str): Unique identifier for the section.
        section_label (str): The display name or translation key for the section.
        section_icon (str): The icon identifier associated with the section.
    """
    section_id: str
    section_label: str
    section_icon: str


class MetadataProvider:
    """
    Base provider for retrieving widget configuration metadata.
    """

    def provide(self, filter: KamaFilter) -> list[WidgetMetadata]:  # noqa
        """
        Retrieves a list of widget metadata matching the specified filter.

        Args:
            filter (KamaFilter): The filter object containing query criteria.

        Returns:
            list[WidgetMetadata]: A list of metadata objects.
        """
        return []

    @staticmethod
    def _parse_stylesheet(stylesheet_json: str):
        """
        Converts a JSON-formatted stylesheet string into a standard QSS string.

        Args:
            stylesheet_json (str): A JSON string representing style properties.

        Returns:
            str: A formatted QSS string (e.g., "color: red;").
        """

        stylesheet_map = json.loads(stylesheet_json)
        stylesheet_string = ""

        for key, value in stylesheet_map.items():
            stylesheet_string += f"{key}: {value};\n"

        return stylesheet_string


class ControllerSectionProvider:
    """
    Base provider for retrieving application section definitions.
    """

    def provide(self, filter: KamaFilter) -> list[Section]:  # noqa
        """
        Retrieves a list of section objects matching the specified filter.

        Args:
            filter (KamaFilter): The filter object containing query criteria.

        Returns:
            list[Section]: A list of section data objects.
        """
        return []
