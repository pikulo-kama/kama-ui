from typing import Final, TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from kui.core.app import KamaApplication


class ColorMode:
    """
    Represents application color modes.
    """

    Light: Final = "light"
    Dark: Final = "dark"


class StyleResolver:

    def __init__(self):
        self.__application: Optional["KamaApplication"] = None

    @property
    def application(self) -> "KamaApplication":
        return self.__application

    @application.setter
    def application(self, application: "KamaApplication"):
        self.__application = application

    def resolve(self, *args) -> str:
        return ""
