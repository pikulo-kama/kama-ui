from typing import TYPE_CHECKING
from kui.core._service import AppService
from kui.core.provider import MetadataProvider, ControllerSectionProvider

if TYPE_CHECKING:
    from kui.core.app import KamaApplicationContext


class DataProviderService(AppService):

    def __init__(self, context: "KamaApplicationContext"):
        super().__init__(context)
        self.__metadata_provider = MetadataProvider()
        self.__section_provider = ControllerSectionProvider()

    @property
    def metadata(self) -> MetadataProvider:
        return self.__metadata_provider

    @metadata.setter
    def metadata(self, provider: MetadataProvider):
        self.__metadata_provider = provider

    @property
    def section(self) -> ControllerSectionProvider:
        return self.__section_provider

    @section.setter
    def section(self, provider: ControllerSectionProvider):
        self.__section_provider = provider
