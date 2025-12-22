import os

from kui.core.style import StyleResolver
from kui.util.file import resolve_resource


class ImageResolver(StyleResolver):

    def __init__(self):
        super().__init__(r"image\(['\"]([^'\"]+)['\"]\)")

    def resolve(self, match):
        image_name = match.group(1)
        image_path = resolve_resource(image_name)

        return f"url('{image_path.replace(os.path.sep, "/")}')"
