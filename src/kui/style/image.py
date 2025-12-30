import dataclasses
import os
from kui.core.style import StyleResolver


@dataclasses.dataclass
class DynamicResource:
    resource_name: str
    resource_path: str
    color_code: str


class ImageResolver(StyleResolver):

    def __init__(self):
        super().__init__(r"image\(['\"]([^'\"]+)['\"]\)")

    def resolve(self, match):
        image_name = match.group(1)
        image_path = self.application.discovery.resources(image_name)

        return f"url('{image_path.replace(os.path.sep, "/")}')"
