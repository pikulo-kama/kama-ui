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
    """
    Base class for resolving custom tokens in stylesheets.
    """

    def __init__(self):
        """
        Initializes the resolver with an empty application reference.
        """
        self.__application: Optional["KamaApplication"] = None

    @property
    def application(self) -> "KamaApplication":
        """
        Returns the KamaApplication instance.

        Returns:
            KamaApplication: The global application instance.
        """
        return self.__application

    @application.setter
    def application(self, application: "KamaApplication"):
        """
        Sets the KamaApplication instance.

        Args:
            application (KamaApplication): The global application instance.
        """
        self.__application = application

    def resolve(self, *args) -> str:
        """
        Resolves style tokens into a valid QSS string.

        Args:
            *args: Variable arguments passed from the style token.

        Returns:
            str: The resolved style value.
        """
        return ""
