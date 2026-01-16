from typing import TYPE_CHECKING

from kamatr.manager import TextResourceManager
from kamatr.provider import TextResourceProvider
from kui.core._service import AppService

if TYPE_CHECKING:
    from kui.core.app import KamaApplicationContext


class TextResourceService(AppService, TextResourceManager):
    """
    Service responsible for managing localized text and translation resources.
    """

    def __init__(self, context: "KamaApplicationContext", provider: TextResourceProvider = None):
        """
        Initializes the service and the underlying text resource manager.
        """

        AppService.__init__(self, context)
        TextResourceManager.__init__(self, provider)

    @TextResourceManager.locale.getter
    def locale(self) -> str:
        """
        Returns the active locale, falling back to the application default if not set.
        """
        return super().locale or self.application.config.default_locale
