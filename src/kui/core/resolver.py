import re

from kui.resolver import get_core_resolvers
from kutil.logger import get_logger

_logger = get_logger(__name__)


def resolve_content(content: str, resolvers: dict[str, "ContentResolver"] = None):
    """
    Recursively resolves special tokens within a string and returns the final
    object or formatted string.

    Tokens follow the pattern 'name{value, key: value}'. This function identifies
    the appropriate ContentResolver based on the token name and executes its
    resolve logic.

    Args:
        content (str): The string containing potential tokens to resolve.
        resolvers (dict): Dictionary of contextual resolvers
                                to supplement global ones.

    Returns:
        Any: The fully resolved content, which could be a string, QPixmap,
             or other object types.
    """

    if resolvers is None:
        resolvers = get_core_resolvers()

    while True:

        if not isinstance(content, str):
            return content

        match = re.compile(r"(\w+)\{(.*)}").search(content)

        # If no token has been found then
        # treat it as regular string.
        if not match:
            _logger.debug("No token found in string '%s'. Content is resolved.", content)
            return content

        full_token = match.group(0)
        token_name = match.group(1)
        properties: list = match.group(2).split(",")

        # Recursively check for nested tokens.
        parameter = resolve_content(properties.pop(0), resolvers)
        args = []
        kw = {}

        # Collect token properties.
        for prop in properties:
            prop_parts = prop.split(":")
            key = resolve_content(prop_parts[0].strip(), resolvers)

            if len(prop_parts) == 1:
                args.append(key)

            elif len(prop_parts) == 2:
                value = resolve_content(prop_parts[1].strip(), resolvers)

                if value.isdigit():
                    value = int(value)

                kw[key] = value

        resolver_name = f"{token_name.lower()}resolver"
        resolver: ContentResolver = resolvers.get(resolver_name)

        _logger.debug("Resolving content using %s.", resolver.__class__.__name__)
        _logger.debug("param=%s, args=%s, kw=%s", parameter, args, kw)
        resolved_content = resolver.resolve(parameter, *args, **kw) or ""

        # This will allow to have tokenised values together with other text.
        if isinstance(resolved_content, str):
            resolved_content = content.replace(full_token, resolved_content)

        content = resolved_content


class ContentResolver:
    """
    Base class for token resolution logic.

    Subclasses must implement the resolve method to transform a token's
    primary value and parameters into actual application objects or text.
    """

    def resolve(self, value: str, *args, **kw):  # pragma: no cover
        """
        Processes a token's components to return a resolved value.

        Args:
            value (str): The primary value found inside the token braces.
            *args: Positional properties extracted from the token.
            **kw: Key-value properties extracted from the token.

        Returns:
            Any: The resolved content.
        """
        pass
