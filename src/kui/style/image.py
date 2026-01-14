import os
from kui.core.style import StyleResolver


class ImageResolver(StyleResolver):

    def resolve(self, image_name: str):
        image_path = self.application.discovery.images(image_name)
        return f"url('{image_path.replace(os.path.sep, "/")}')"
