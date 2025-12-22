from kui.core.app import KamaApplication
from kui.core.style import StyleResolver


class ColorResolver(StyleResolver):

    def __init__(self):
        super().__init__(r"color\(['\"]([^'\"]+)['\"]\)")

    def resolve(self, match):
        color_code = match.group(1)
        app = KamaApplication.instance()
        color = app.get_color(color_code)

        return color.color_hex


class RgbaColorResolver(StyleResolver):

    def __init__(self):
        super().__init__(r"rgba\(\s*['\"]([^'\"]+)['\"]\s*,\s*([^)]+)\s*\)")

    def resolve(self, match):
        color_code = match.group(1)
        alpha = match.group(2)

        app = KamaApplication.instance()
        color = app.get_color(color_code)

        return color.rgba(alpha)
