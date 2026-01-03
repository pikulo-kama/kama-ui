from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from kui.core.app import KamaApplication


class AppService:

    def __init__(self, application: "KamaApplication"):
        self.__application = application

    @property
    def application(self) -> "KamaApplication":
        return self.__application
