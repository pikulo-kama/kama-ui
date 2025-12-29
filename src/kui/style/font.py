import dataclasses
from kui.core.style import StyleResolver


@dataclasses.dataclass
class KamaFont:
    font_code: str
    font_size: int
    font_family: str
    font_weight: int = 400

    @property
    def qss(self):
        return f"{self.font_size}px '{self.font_family}'; font-weight: {self.font_weight}"


class FontResolver(StyleResolver):

    def __init__(self):
        super().__init__(r"font\(['\"]([^'\"]+)['\"]\)")

    def resolve(self, match):
        font_code = match.group(1)
        font = self.application.fonts.get(font_code)

        return font.qss
