from kui.core.style import StyleResolver
from kui.style.type import KamaColor


class ColorResolver(StyleResolver):
    """
    Resolver for converting color codes into hex strings.
    """

    def resolve(self, color_code: str):
        """
        Retrieves the hex string for the specified color code.

        Args:
            color_code (str): The identifier of the color to resolve.

        Returns:
            str: The resolved hex color string.
        """

        color = self.application.style.get_color(color_code)

        if color is None:
            color = KamaColor("#000000")

        return color.color_hex


class RgbaResolver(StyleResolver):
    """
    Resolver for converting color codes into RGBA strings with custom transparency.
    """

    def resolve(self, color_code: str, alpha: str):
        """
        Retrieves an RGBA representation of a color code with a specific alpha value.

        Args:
            color_code (str): The identifier of the color to resolve.
            alpha (float): The transparency level from 0.0 to 1.0.

        Returns:
            str: The resolved RGBA or transparency-aware color string.
        """

        color = self.application.style.get_color(color_code)

        if color is None:
            color = KamaColor("#000000")

        return color.rgba(alpha)
