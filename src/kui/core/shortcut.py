from typing import Any
from kui.core.app import KamaApplication


def tr(text_resource_key: str, *args):
    return KamaApplication().translations.get(text_resource_key, *args)


def dynamic_data(object_name: str):
    return KamaApplication().data.get(object_name)


def add_dynamic_data(object_name: str, value: Any):
    KamaApplication().data.add(object_name, value)


def prop(property_name: str, default_value: Any = None):
    return KamaApplication().config.get(property_name, default_value)


def resolve_project_file(*paths: str):
    """
    Used to resolve file in '{PROJECT_ROOT}' directory.
    """
    return KamaApplication().discovery.project(*paths)


def resolve_data(*paths: str):
    """
    Used to resolve file in '{PROJECT_ROOT}/Config' directory.
    """
    return KamaApplication().discovery.data(*paths)


def resolve_image(*paths: str, include_temporary: bool = True):
    """
    Used to resolve file in '{PROJECT_ROOT}/Resource' directory.
    """
    return KamaApplication().discovery.images(*paths, include_temporary=include_temporary)


def resolve_temp_file(*paths: str):
    """
    Used to resolve file in '{APP_DATA}/{app_name}/Output' directory.
    """
    return KamaApplication().discovery.output(*paths)


def resolve_temp_image(*paths: str):
    """
    Used to resolve file in '{APP_DATA}/{app_name}/Output/Resources' directory.
    """
    return KamaApplication().discovery.temp_images(*paths)


def resolve_app_data(*paths: str):
    """
    Used to resolve file in '{APP_DATA}/{app_name}' directory.
    """
    return KamaApplication().discovery.app_data(*paths)


def resolve_log(*paths: str):
    """
    Used to resolve file in '{APP_DATA}/{app_name}/Logs' directory.
    """
    return KamaApplication().discovery.logs(*paths)


def resolve_logback(*paths: str):
    """
    Used to resolve logging configuration file.
    File is located in '{AppData}/{app_name}/Logback'
    """
    return KamaApplication().discovery.logback(*paths)
