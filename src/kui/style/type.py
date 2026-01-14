import dataclasses


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


@dataclasses.dataclass
class KamaFont:
    font_code: str
    font_size: int
    font_family: str
    font_weight: int = 400

    @property
    def qss(self):
        return f"{self.font_size}px '{self.font_family}'; font-weight: {self.font_weight}"


@dataclasses.dataclass
class DynamicImage:
    image_name: str
    image_path: str
    color_code: str
