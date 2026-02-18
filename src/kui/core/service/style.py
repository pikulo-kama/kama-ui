import re
from functools import cached_property
from typing import TYPE_CHECKING
from dataclasses import dataclass
from copy import deepcopy

from PyQt6.QtCore import Qt
from kutil.file_type import KSS

from kui.core._service import AppService
from kui.core.style import ColorMode, StyleResolver
from kutil.file import read_file, save_file
from kui.style.type import KamaComposedColor, KamaFont, DynamicImage
from kutil.logger import get_logger
from kutil.number import is_float

from kui.util.file import get_files_from_directory

if TYPE_CHECKING:
    from kui.core.app import KamaApplicationContext

_logger = get_logger(__name__)


@dataclass
class StyleProperty:
    name: str
    value: str

    @property
    def qss(self):
        return f"{self.name}: {self.value};"


class StyleBlock:

    def __init__(self, selector: str, properties: list[StyleProperty]):
        self.__selector = re.sub(r"\.([a-zA-Z0-9_-]+)", r"[cls-\1='true']", selector.strip())
        self.__properties = properties

    @cached_property
    def selector(self) -> str:
        return self.__selector

    @property
    def properties(self) -> list[StyleProperty]:
        return self.__properties

    @property
    def qss(self) -> str:
        properties_style = ""

        for prop in self.__properties:
            properties_style += f"\t{prop.qss}\n"

        return f"{self.selector} {{\n{properties_style}}}\n\n"

    def __add__(self, other):
        if isinstance(other, str):
            return self.__str__() + other

        return None

    def __str__(self):
        return self.qss


class StyleBuilder(AppService):
    """
    Service responsible for loading QSS files and resolving style tokens.
    """

    __BLOCK_REGEX = r"(?m)^[ \t]*([^{;]+?)\s*\{((?:[^{}]|\{(?:[^{}]|\{[^{}]*\})*\})*)\}"
    __PROPERTY_REGEX = r"([\w-]+)\s*:\s*([^;]+)"

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

    def load_stylesheet(self, directory: str) -> list[StyleBlock]:
        """
        Load all stylesheets recursively using Traversable API.
        Works for both standard OS paths and bundled resources.
        """

        style_files: list[str] = get_files_from_directory(directory, recursive=True, extension=KSS.extension)
        style_blocks: list[StyleBlock] = []

        for style_string in style_files:
            entry_blocks = self.__parse_qss(style_string)

            for block in entry_blocks:
                for prop in block.properties:
                    prop.value = self.resolve(prop.value)

                style_blocks.append(block)

        return style_blocks

    def __parse_qss(self, stylesheet: str, parent_selector: str = "") -> list[StyleBlock]:
        string_blocks = self.__read_blocks(stylesheet)
        blocks = []

        for block, selector, content, props in string_blocks:
            selector = selector.replace("&", parent_selector)

            blocks.append(StyleBlock(selector, [StyleProperty(name, value) for name, value in props]))
            blocks.extend(self.__parse_qss(content, selector))

        return blocks

    @staticmethod
    def __read_blocks(stylesheet: str):
        blocks = []
        properties = []

        depth = 0

        selector_start = 0
        content_start = -1

        property_key_start = -1
        property_key_end = -1
        property_value_start = -1
        property_found = False

        for current_char_index, char in enumerate(stylesheet):
            next_char_index = current_char_index + 1

            # Process properties.
            if depth == 1:
                if char == ":" and not property_found:
                    property_key_end = current_char_index
                    property_value_start = next_char_index

                    property_found = True

                elif char == ";":
                    property_key = stylesheet[property_key_start:property_key_end].strip()
                    property_value = stylesheet[property_value_start:current_char_index].strip()
                    properties.append((property_key, property_value))

                    property_key_start = next_char_index
                    property_found = False

            # Assume that after each property on first level
            # goes nested style block.
            if depth == 0 and char == ";":
                selector_start = next_char_index

            if char == "{":

                # When we step into first level block
                # then mark character as beginning of block
                # as well as beginning of first property key.
                if depth == 0:
                    content_start = current_char_index
                    property_key_start = next_char_index

                depth += 1
                # Reset property identification flag once we get
                # deeper into block stylesheet, since it may mess up
                # consequent properties by treating block selectors with :
                # as properties.
                property_found = False

            elif char == "}":
                depth -= 1

                if depth == 0:
                    block = stylesheet[selector_start:next_char_index].strip()
                    selector = stylesheet[selector_start:content_start].strip()
                    content = stylesheet[content_start + 1:current_char_index].strip()

                    blocks.append((block, selector, content, deepcopy(properties)))
                    properties.clear()

                    # Change starting position of next block.
                    # We will assume that it goes right after this one.
                    selector_start = next_char_index

        return blocks

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

    def clear(self):
        self.__dynamic_images.clear()
        self.__fonts.clear()
        self.__colors.clear()

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

        color_hex = color.get(self.color_mode)

        if color_hex is None:
            color_hex = color.get(ColorMode.Dark)

        return color_hex

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
