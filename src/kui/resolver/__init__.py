from kui.util.file import resolve_application_data
from kutil.logger import get_logger
from kutil.reflection import get_members
from kui.core.resolver import ContentResolver


_logger = get_logger(__name__)
__resolvers: dict[str, "ContentResolver"] = {}


def get_core_resolvers():
    """
    Returns a global registry of available ContentResolver instances.

    If the registry is empty, it uses reflection to scan the package
    for subclasses of ContentResolver and initializes them.

    Returns:
        dict[str, ContentResolver]: A dictionary mapping lowercase resolver
                                     class names to their instances.
    """

    global __resolvers

    if len(__resolvers) == 0:
        for member_name, member in get_members(__package__, ContentResolver):
            _logger.debug("Loading core content resolver with name %s", member_name)
            __resolvers[member_name.lower()] = member()

        for member_name, member in get_members(resolve_application_data("resolver"), ContentResolver):
            _logger.debug("Loading custom content resolver with name %s", member_name)
            __resolvers[member_name.lower()] = member()

    return __resolvers
