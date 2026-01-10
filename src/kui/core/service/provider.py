import dataclasses
from typing import TYPE_CHECKING

from kui.core._service import AppService
from kui.core.metadata import WidgetMetadata

if TYPE_CHECKING:
    from kui.core.controller import WidgetController
    from kui.core.app import KamaApplicationContext


@dataclasses.dataclass
class Section:
    section_id: str
    section_label: str
    section_icon: str


class MetadataProvider:
    def provide(self, section_id: str) -> list[WidgetMetadata]:  # noqa
        return []


class ControllerSectionProvider:
    def provide(self, controller: "WidgetController") -> list[Section]:  # noqa
        return []


class DataProviderService(AppService):

    def __init__(self, context: "KamaApplicationContext"):
        super().__init__(context)
        self.__metadata_provider = MetadataProvider()
        self.__section_provider = ControllerSectionProvider()

    @property
    def metadata(self):
        return self.__metadata_provider

    @metadata.setter
    def metadata(self, provider: MetadataProvider):
        self.__metadata_provider = provider

    @property
    def section(self):
        return self.__section_provider

    @section.setter
    def section(self, provider: ControllerSectionProvider):
        self.__section_provider = provider
