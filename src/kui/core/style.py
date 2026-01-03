import re
from typing import Final, TYPE_CHECKING, Optional

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QApplication
from kutil.file import read_file, save_file
from kutil.logger import get_logger
from importlib.abc import Traversable
from kui.core._service import AppService
from kui.style.type import KamaComposedColor, KamaFont, DynamicResource

if TYPE_CHECKING:
    from kui.core.app import KamaApplication

_logger = get_logger(__name__)


class ColorMode:
    """
    Represents application color modes.
    """

    Light: Final = "light"
    Dark: Final = "dark"


class StyleManager(AppService):

    def __init__(self, application: "KamaApplication"):
        super().__init__(application)

        self.__color_mode = None
        self.__dynamic_resources: list[DynamicResource] = []
        self.__style_builder = StyleBuilder(application)

        self.__fonts: dict[str, KamaFont] = {}
        self.__colors: dict[str, KamaComposedColor] = {}

    @property
    def color_mode(self):
        if self.__color_mode is not None:
            return self.__color_mode

        return self.__get_system_color_mode()

    @color_mode.setter
    def color_mode(self, color_mode: str):
        self.__color_mode = color_mode

    def get_color(self, color_code: str):
        color = self.__colors.get(color_code)

        if not color:
            return None

        if self.color_mode == ColorMode.Light:
            return color.light_color

        return color.dark_color

    @property
    def fonts(self):
        return self.__fonts

    @property
    def builder(self):
        return self.__style_builder

    def add_font(self, font: KamaFont):
        self.__fonts[font.font_code] = font

    def add_color(self, color: KamaComposedColor):
        self.__colors[color.color_code] = color

    def add_dynamic_resource(self, resource: DynamicResource):
        self.__dynamic_resources.append(resource)

    def create_dynamic_resources(self):
        """
        Used to create dynamic resources.
        Mainly this applies to SVG elements
        that are just an XML files where we can
        replace colors.

        This is needed in the first place to avoid
        creating duplicate resources where the only
        difference is color.
        """

        for resource in self.__dynamic_resources:
            current_color = resource.color_code
            resolved_color = self.get_color(resource.color_code)

            if resolved_color is not None:
                current_color = resolved_color

            resource_path = self.application.discovery.resources(resource.resource_path, include_temporary=False)
            resource_content = read_file(resource_path)

            if current_color is not None:
                resource_content = resource_content.replace("currentColor", current_color.color_hex)

            temp_resource_path = self.application.discovery.temp_resources(resource.resource_name)
            save_file(temp_resource_path, resource_content)

    @staticmethod
    def __get_system_color_mode():
        """
        Used to get current color mode.
        """

        mode = ColorMode.Light
        application = QApplication.instance()

        if application is None:
            return mode

        color_scheme = application.styleHints().colorScheme()  # noqa

        if color_scheme == Qt.ColorScheme.Dark:
            mode = ColorMode.Dark

        return mode

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


class StyleBuilder(AppService):

    def __init__(self, application: "KamaApplication"):
        super().__init__(application)
        self.__resolvers: list[StyleResolver] = []

    def add_resolver(self, resolver: StyleResolver):
        resolver.application = self.application
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
