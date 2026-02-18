from typing import Any
from kui.core.app import KamaApplication


def tr(text_resource_key: str, *args):
    """
    Retrieves a localized string based on the provided key.

    Args:
        text_resource_key (str): The translation key to look up.
        *args: Variable arguments for string formatting.

    Returns:
        str: The translated and formatted string.
    """
    return KamaApplication().translations.get(text_resource_key, *args)


def dynamic_data(object_name: str):
    """
    Retrieves temporary data from the dynamic data holder.

    Args:
        object_name (str): The unique name of the stored object.

    Returns:
        Any: The data object if found, otherwise None.
    """
    return KamaApplication().data.get(object_name)


def add_dynamic_data(object_name: str, value: Any):
    """
    Adds an object to the dynamic data holder for intermediate storage.

    Args:
        object_name (str): The name to associate with the value.
        value (Any): The data to be stored.
    """
    KamaApplication().data.add(object_name, value)


def prop(property_name: str, default_value: Any = None):
    """
    Retrieves a property value from the application configuration.

    Args:
        property_name (str): The dot-notated configuration key.
        default_value (Any, optional): Fallback value if the property is missing.

    Returns:
        Any: The configuration value.
    """
    return KamaApplication().config.get(property_name, default_value)


def resolve_project_file(*paths: str):
    """
    Used to resolve file in '{PROJECT_ROOT}' directory.

    Args:
        *paths (str): Sub-path segments to join.

    Returns:
        str: The absolute path within the project root.
    """
    return KamaApplication().discovery.project(*paths)


def resolve_image(*paths: str, include_temporary: bool = True):
    """
    Used to resolve file in '{PROJECT_ROOT}/Resource' directory.

    Args:
        *paths (str): Sub-path segments to join.
        include_temporary (bool): Whether to check for dynamic/cached images first.

    Returns:
        str: The absolute path to the image file.
    """
    return KamaApplication().discovery.images(*paths, include_temporary=include_temporary)


def resolve_temp_file(*paths: str):
    """
    Used to resolve file in '{APP_DATA}/{app_name}/Output' directory.

    Args:
        *paths (str): Sub-path segments to join.

    Returns:
        str: The absolute path to the output directory.
    """
    return KamaApplication().discovery.output(*paths)


def resolve_temp_image(*paths: str):
    """
    Used to resolve file in '{APP_DATA}/{app_name}/Output/Resources' directory.

    Args:
        *paths (str): Sub-path segments to join.

    Returns:
        str: The absolute path to the temporary 'Images' directory.
    """
    return KamaApplication().discovery.temp_images(*paths)


def resolve_app_data(*paths: str):
    """
    Used to resolve file in '{APP_DATA}/{app_name}' directory.

    Args:
        *paths (str): Sub-path segments to join.

    Returns:
        str: The absolute path to the application data root.
    """
    return KamaApplication().discovery.app_data(*paths)


def resolve_log(*paths: str):
    """
    Used to resolve file in '{APP_DATA}/{app_name}/Logs' directory.

    Args:
        *paths (str): Sub-path segments to join.

    Returns:
        str: The absolute path to the 'Logs' directory.
    """
    return KamaApplication().discovery.logs(*paths)


def resolve_logback(*paths: str):
    """
    Used to resolve logging configuration file.
    File is located in '{AppData}/{app_name}/Logback'

    Args:
        *paths (str): Sub-path segments to join.

    Returns:
        str: The absolute path to the logback configuration.
    """
    return KamaApplication().discovery.logback(*paths)
