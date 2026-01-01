import re
from typing import Final, TYPE_CHECKING, Optional

from kutil.logger import get_logger
from importlib.abc import Traversable

if TYPE_CHECKING:
    from kui.core.app import KamaApplication

_logger = get_logger(__name__)


class ColorMode:
    """
    Represents application color modes.
    """

    Light: Final = "light"
    Dark: Final = "dark"


class StyleResolver:

    def __init__(self, regex: str):
        self.__application: Optional["KamaApplication"] = None
        self.__regex = regex

    @property
    def application(self) -> "KamaApplication":
        return self.__application

    @application.setter
    def application(self, application: "KamaApplication"):
        self.__application = application

    @property
    def regex(self):
        return self.__regex

    def resolve(self, match) -> str:
        return ""


class StyleBuilder:

    def __init__(self, application: "KamaApplication"):
        self.__application = application
        self.__resolvers: list[StyleResolver] = []

    def add_resolver(self, resolver: StyleResolver):
        resolver.application = self.__application
        self.__resolvers.append(resolver)

    def load_stylesheet(self, directory: Traversable):
        """
        Load all stylesheets recursively using Traversable API.
        Works for both standard OS paths and bundled resources.
        """

        style_string = ""

        for entry in directory.iterdir():
            if entry.is_dir():
                style_string += self.load_stylesheet(entry)

            elif entry.name.endswith(".qss"):
                style_string += entry.read_text(encoding="utf-8")

        return self.resolve(style_string)

    def resolve(self, style_string: str):
        """
        Used to resolve color/font
        properties in string.
        """

        for resolver in self.__resolvers:
            style_string = re.sub(
                resolver.regex,
                resolver.resolve,
                style_string
            )

        return style_string
