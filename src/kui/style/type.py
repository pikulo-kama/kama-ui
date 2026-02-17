import dataclasses


@dataclasses.dataclass
class KamaColor:
    """
    Represents a single hex color and provides conversion utilities.

    Attributes:
        color_hex (str): The color value in hexadecimal format (e.g., '#RRGGBB').
    """

    color_hex: str

    def rgba(self, alpha: str):
        """
        Converts the hex color to an RGBA string with a custom alpha value.

        Args:
            alpha (str): The transparency value (0 to 1).

        Returns:
            str: The formatted rgba() string for QSS.
        """

        red = int(self.color_hex[1:3], 16)
        green = int(self.color_hex[3:5], 16)
        blue = int(self.color_hex[5:7], 16)

        return f"rgba({red}, {green}, {blue}, {alpha})"


@dataclasses.dataclass
class KamaComposedColor:
    """
    Groups a light and dark version of a color under a single identifier.

    Attributes:
        color_code (str): The unique identifier for this composed color.
        variations (dict[str, KamaColor]): Mapping of themes and their colors.
    """

    color_code: str
    variations: dict[str, KamaColor]

    def get(self, theme: str):
        return self.variations.get(theme)


@dataclasses.dataclass
class KamaFont:
    """
    Represents font settings and handles QSS formatting.

    Attributes:
        font_code (str): The unique identifier for this font style.
        font_size (int): The font size in pixels.
        font_family (str): The name of the font family.
        font_weight (int): The font weight (Default: 400).
    """

    font_code: str
    font_size: int
    font_family: str
    font_weight: int = 400

    @property
    def qss(self):
        """
        Generates the QSS string for this font configuration.

        Returns:
            str: A CSS-compatible font declaration.
        """
        return f"{self.font_size}px '{self.font_family}'; font-weight: {self.font_weight}"


@dataclasses.dataclass
class DynamicImage:
    """
    Represents an image resource that supports dynamic color injection.

    Attributes:
        image_name (str): The name to give the generated temporary image.
        image_path (str): The path to the source SVG file.
        color_code (str): The color code to apply to the 'currentColor' placeholder.
    """

    image_name: str
    image_path: str
    color_code: str
