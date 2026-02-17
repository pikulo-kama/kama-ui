from dataclasses import dataclass
import json
from typing import TYPE_CHECKING

from kui.core.filter import KamaFilter
from kui.core.metadata import WidgetMetadata

if TYPE_CHECKING:
    from kui.core.app import KamaApplication


@dataclass
class Section:
    """
    Data container representing a high-level application section.

    Attributes:
        section_id (str): Unique identifier for the section.
        section_label (str): The display name or translation key for the section.
        section_icon (str): The icon identifier associated with the section.
    """

    section_id: str
    section_label: str = None
    section_icon: str = None


class MetadataProvider:
    """
    Base provider for retrieving widget configuration metadata.
    """

    def __init__(self):
        self.__application = None

    @property
    def application(self) -> "KamaApplication":
        return self.__application

    @application.setter
    def application(self, application: "KamaApplication"):
        self.__application = application

    def provide(self, query: KamaFilter) -> list[WidgetMetadata]:
        """
        Retrieves a list of widget metadata matching the specified filter.

        Args:
            query (KamaFilter): The filter object containing query criteria.

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


class SectionProvider:
    """
    Base provider for retrieving application section definitions.
    """

    def __init__(self):
        self.__application = None

    @property
    def application(self) -> "KamaApplication":
        return self.__application

    @application.setter
    def application(self, application: "KamaApplication"):
        self.__application = application

    def provide(self, query: KamaFilter) -> list[Section]:
        """
        Retrieves a list of section objects matching the specified filter.

        Args:
            query (KamaFilter): The filter object containing query criteria.

        Returns:
            list[Section]: A list of section data objects.
        """
        return []


class KMLLayoutProvider(MetadataProvider):

    def provide(self, query: KamaFilter) -> list[WidgetMetadata]:
        return self.application.window.manager.metadata.get(query.get("section"), [])


class KMLSectionProvider(SectionProvider):

    def provide(self, query: KamaFilter) -> list[Section]:
        return [self.application.window.manager.sections.get(query.get("section_id"), None)]
