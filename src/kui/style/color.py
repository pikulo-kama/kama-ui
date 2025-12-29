import dataclasses

from kui.core.style import StyleResolver


@dataclasses.dataclass
class KamaColor:
    color_hex: str

    def rgba(self, alpha: str):
        red = int(self.color_hex[1:3], 16)
        green = int(self.color_hex[3:5], 16)
        blue = int(self.color_hex[5:7], 16)

        return f"rgba({red}, {green}, {blue}, {alpha})"


@dataclasses.dataclass
class KamaComposedColor:
    color_code: str
    light_color: KamaColor
    dark_color: KamaColor

class ColorResolver(StyleResolver):

    def __init__(self):
        super().__init__(r"color\(['\"]([^'\"]+)['\"]\)")

    def resolve(self, match):
        color_code = match.group(1)
        color = self.application.get_color(color_code)

        return color.color_hex


class RgbaColorResolver(StyleResolver):

    def __init__(self):
        super().__init__(r"rgba\(\s*['\"]([^'\"]+)['\"]\s*,\s*([^)]+)\s*\)")

    def resolve(self, match):
        color_code = match.group(1)
        alpha = match.group(2)
        color = self.application.get_color(color_code)

        return color.rgba(alpha)
