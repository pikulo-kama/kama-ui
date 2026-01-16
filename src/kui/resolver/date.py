from datetime import datetime
from kutil.logger import get_logger
from kui.core.resolver import ContentResolver


_logger = get_logger(__name__)


class DateResolver(ContentResolver):
    """
    Resolver used to handle date-related tokens in widget content.
    """

    def resolve(self, key: str, *args, **kw):
        """
        Resolves the provided key into a current date component.

        Args:
            key (str): The token to resolve (e.g., 'year').
            *args: Variable arguments (unused).
            **kw: Keyword arguments (unused).

        Returns:
            Any: The resolved date component (e.g., current year as int)
                or None if the key is not recognized.
        """

        if key == "year":
            return datetime.now().year

        return None
