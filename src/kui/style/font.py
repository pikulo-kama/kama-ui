from kui.core.style import StyleResolver


class FontResolver(StyleResolver):

    def __init__(self):
        super().__init__(r"font\(['\"]([^'\"]+)['\"]\)")

    def resolve(self, match):
        font_code = match.group(1)
        font = self.application.style.fonts.get(font_code)

        return font.qss
