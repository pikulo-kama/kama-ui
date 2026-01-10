from typing import TYPE_CHECKING

from kamatr.manager import TextResourceManager
from kamatr.provider import TextResourceProvider
from kui.core._service import AppService

if TYPE_CHECKING:
    from kui.core.app import KamaApplicationContext


class TextResourceService(AppService, TextResourceManager):

    def __init__(self, context: "KamaApplicationContext", provider: TextResourceProvider = None):
        AppService.__init__(self, context)
        TextResourceManager.__init__(self, provider)

    @TextResourceManager.locale.getter
    def locale(self) -> str:
        return super().locale or self.application.config.default_locale
