from kui.core.style import StyleResolver


class FontResolver(StyleResolver):

    def resolve(self, font_code: str):
        font = self.application.style.fonts.get(font_code)
        return font.qss
