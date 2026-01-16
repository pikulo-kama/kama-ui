import os
import re
from importlib.abc import Traversable
from typing import TYPE_CHECKING

from PyQt6.QtCore import Qt
from kui.core._service import AppService
from kui.core.style import ColorMode, StyleResolver
from kutil.file import read_file, save_file
from kui.style.type import KamaComposedColor, KamaFont, DynamicImage
from kutil.logger import get_logger
from kutil.number import is_float

if TYPE_CHECKING:
    from kui.core.app import KamaApplicationContext


_logger = get_logger(__name__)


class StyleBuilder(AppService):
    """
    Service responsible for loading QSS files and resolving style tokens.
    """

    def __init__(self, context: "KamaApplicationContext"):
        """
        Initializes the StyleBuilder with an empty registry of resolvers.
        """

        super().__init__(context)
        self.__resolvers: dict[str, StyleResolver] = {}

    def add_resolver(self, resolver: StyleResolver):
        """
        Registers a new StyleResolver and associates it with a token name.
        """

        resolver_name = resolver.__class__.__name__.replace("Resolver", "").lower()
        resolver.application = self.application
        self.__resolvers[resolver_name] = resolver

    def load_stylesheet(self, directory: Traversable):
        """
        Load all stylesheets recursively using Traversable API.
        Works for both standard OS paths and bundled resources.
        """

        style_string = ""

        if not os.path.exists(str(directory)):
            return style_string

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

        resolved_values = []

        for match in re.finditer(r"(\w+?(?=\())\((.*?(?=\)))\)", style_string):
            value = match.group(0)
            token = match.group(1)
            args_string = match.group(2)
            resolver = self.__resolvers.get(token)

            if resolver is None:
                _logger.error("Resolver for token '%s' was not found.", token)
                continue

            if value in resolved_values:
                continue

            raw_args = [arg.strip() for arg in args_string.split(",")]
            args = []

            for argument in raw_args:
                if argument.isdigit():
                    args.append(int(argument))

                elif is_float(argument):
                    args.append(float(argument))

                else:
                    args.append(argument[1:-1])

            resolved_value = resolver.resolve(*args)
            style_string = style_string.replace(value, resolved_value)
            resolved_values.append(value)

        return style_string


class StyleManagerService(AppService):
    """
    Main service for managing application-wide themes, fonts, and colors.
    """

    def __init__(self, context: "KamaApplicationContext"):
        """
        Initializes the StyleManager with registries for colors, fonts, and dynamic images.
        """

        super().__init__(context)

        self.__color_mode = None
        self.__dynamic_images: list[DynamicImage] = []
        self.__style_builder = StyleBuilder(context)

        self.__fonts: dict[str, KamaFont] = {}
        self.__colors: dict[str, KamaComposedColor] = {}

    @property
    def color_mode(self):
        """
        Returns the current color mode, falling back to system settings if not explicitly set.
        """

        if self.__color_mode is not None:
            return self.__color_mode

        return self.__get_system_color_mode()

    @color_mode.setter
    def color_mode(self, color_mode: str):
        """
        Manually sets the application color mode (e.g., 'light' or 'dark').
        """
        self.__color_mode = color_mode

    def get_color(self, color_code: str):
        """
        Retrieves the appropriate color from a composed color object based on the current mode.
        """

        color = self.__colors.get(color_code)

        if not color:
            return None

        if self.color_mode == ColorMode.Light:
            return color.light_color

        return color.dark_color

    @property
    def fonts(self):
        """
        Returns the dictionary of registered fonts.
        """
        return self.__fonts

    @property
    def builder(self):
        """
        Returns the StyleBuilder instance associated with this service.
        """
        return self.__style_builder

    def add_font(self, font: KamaFont):
        """
        Adds a font definition to the manager.
        """
        self.__fonts[font.font_code] = font

    def add_color(self, color: KamaComposedColor):
        """
        Adds a composed color definition (light/dark pair) to the manager.
        """
        self.__colors[color.color_code] = color

    def add_dynamic_image(self, image: DynamicImage):
        """
        Registers an image for dynamic color processing.
        """
        self.__dynamic_images.append(image)

    def create_dynamic_images(self):
        """
        Used to create dynamic resources.
        Mainly this applies to SVG elements
        that are just an XML files where we can
        replace colors.

        This is needed in the first place to avoid
        creating duplicate resources where the only
        difference is color.
        """

        for image in self.__dynamic_images:
            current_color = image.color_code
            resolved_color = self.get_color(image.color_code)

            if resolved_color is not None:
                current_color = resolved_color

            image_path = self.application.discovery.images(image.image_path, include_temporary=False)
            image_content = read_file(image_path)

            if current_color is not None:
                image_content = image_content.replace("currentColor", current_color.color_hex)

            temp_image_path = self.application.discovery.temp_images(image.image_name)
            save_file(temp_image_path, image_content)

    def __get_system_color_mode(self):
        """
        Used to get current color mode.
        """

        mode = ColorMode.Light
        color_scheme = self.application.window.qt_application.styleHints().colorScheme()  # noqa

        if color_scheme == Qt.ColorScheme.Dark:
            mode = ColorMode.Dark

        return mode
