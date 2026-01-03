from kui.core.style import StyleResolver


class ColorResolver(StyleResolver):

    def resolve(self, color_code: str):
        color = self.application.style.get_color(color_code)
        return color.color_hex


class RgbaResolver(StyleResolver):

    def resolve(self, color_code: str, alpha: float):
        color = self.application.style.get_color(color_code)
        return color.rgba(alpha)
