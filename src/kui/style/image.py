import os
from kui.core.style import StyleResolver


class ImageResolver(StyleResolver):
    """
    Resolver for converting image identifiers into valid QSS URL strings.
    """

    def resolve(self, image_name: str):
        """
        Retrieves the absolute path of an image and formats it for QSS.

        Args:
            image_name (str): The filename or identifier of the image.

        Returns:
            str: A QSS-compatible URL string, e.g., "url('C:/Project/Images/icon.png')".
        """

        image_path = self.application.discovery.images(image_name)
        return f"url('{image_path.replace(os.path.sep, "/")}')"
