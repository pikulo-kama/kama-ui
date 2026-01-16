from kui.core.style import StyleResolver


class FontResolver(StyleResolver):
    """
    Resolver for converting font codes into valid QSS font declarations.
    """

    def resolve(self, font_code: str):
        """
        Retrieves the QSS font string for the specified font code.

        Args:
            font_code (str): The identifier of the font to resolve.

        Returns:
            str: The resolved QSS font string (e.g., '12px "Roboto"').
        """

        font = self.application.style.fonts.get(font_code)
        return font.qss
