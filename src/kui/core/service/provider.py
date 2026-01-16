from typing import TYPE_CHECKING
from kui.core._service import AppService
from kui.core.provider import MetadataProvider, ControllerSectionProvider

if TYPE_CHECKING:
    from kui.core.app import KamaApplicationContext


class DataProviderService(AppService):
    """
    Service responsible for providing access to metadata and section data providers.
    """

    def __init__(self, context: "KamaApplicationContext"):
        """
        Initializes the service with default metadata and section providers.
        """

        super().__init__(context)
        self.__metadata_provider = MetadataProvider()
        self.__section_provider = ControllerSectionProvider()

    @property
    def metadata(self) -> MetadataProvider:
        """
        Returns the current metadata provider instance.
        """
        return self.__metadata_provider

    @metadata.setter
    def metadata(self, provider: MetadataProvider):
        """
        Sets a new metadata provider instance.
        """
        self.__metadata_provider = provider

    @property
    def section(self) -> ControllerSectionProvider:
        """
        Returns the current section provider instance.
        """
        return self.__section_provider

    @section.setter
    def section(self, provider: ControllerSectionProvider):
        """
        Sets a new section provider instance.
        """
        self.__section_provider = provider
