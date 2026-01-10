from kui.core.app import KamaApplication
from kui.core.resolver import ContentResolver
from kutil.logger import get_logger

_logger = get_logger(__name__)


class DataResolver(ContentResolver):
    """
    A specialized ContentResolver that retrieves dynamic values from the global
    data holder object.

    This resolver is typically used to inject application state data into UI
    components via tokens like 'data{user_name}'. It ensures type safety by
    only returning values that are explicitly of string type.
    """

    def resolve(self, key: str, *args, **kw):
        """
        Looks up the provided key in the global data holder and returns its
        string representation.

        Args:
            key (str): The identifier for the data to be retrieved.
            *args: Unused positional arguments.
            **kw: Unused keyword arguments.

        Returns:
            str: The resolved string value or an empty string if the data
                 is missing or not a string.
        """

        application = KamaApplication()
        data = application.data.get(key)
        default_value = None

        if len(args) > 0:
            default_value = args[0]

        if data is None:
            data = default_value

        if isinstance(data, int) or isinstance(data, float):
            data = str(data)

        if not isinstance(data, str):
            return None

        _logger.debug("Resolved %s to %s", key, data)
        return data
