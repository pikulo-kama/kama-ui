from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from kui.core.app import KamaApplication, KamaApplicationContext


class AppService:

    def __init__(self, context: "KamaApplicationContext"):
        self.__context = context

    @property
    def application(self) -> "KamaApplication":
        return self.__context.application
