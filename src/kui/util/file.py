import os
import sys
from importlib import resources
from kui.core.constants import Directory


def get_project_root_package(target_package: str = None) -> str:
    """
    Returns the name of the package where the main script is located.
    If run as 'python -m savegem.app.main', it returns 'savegem.app'.
    """

    root_package = _get_root_package()

    if root_package is None:
        return "standalone"

    return f"{root_package}.{target_package}"


def resolve_config(config_name: str):
    """
    Used to resolve file in '{PROJECT_ROOT}/config' directory.
    """
    return os.path.join(Directory().Config, config_name)


def resolve_resource(resource_name: str, include_temporary=True):
    """
    Used to resolve file in '{PROJECT_ROOT}/resource' directory.
    """

    temp_resource_path = os.path.join(Directory().TempResources, resource_name)

    if include_temporary and os.path.exists(temp_resource_path):
        return temp_resource_path

    return os.path.join(Directory().Resources, resource_name)


def resolve_temp_file(file_name: str):
    """
    Used to resolve file in '{APP_DATA}/SaveGem/output' directory.
    """
    return os.path.join(Directory().Output, file_name)


def resolve_temp_resource(file_name: str):
    """
    Used to resolve file in '{APP_DATA}/Output/Resources' directory.
    """
    return os.path.join(Directory().TempResources, file_name)


def resolve_application_data(file_name: str):
    package_path = str(resources.files(_get_root_package()))
    return os.path.join(package_path, file_name)


def resolve_app_data(file_name: str):
    """
    Used to resolve file in '{APP_DATA}' directory.
    """
    return os.path.join(Directory().AppDataRoot, file_name)


def resolve_log(file_name: str):
    """
    Used to resolve file in '{APP_DATA}/logs' directory.
    """
    return os.path.join(Directory().Logs, file_name)


def resolve_logback(file_name: str):
    """
    Used to resolve logging configuration file.
    """
    return os.path.join(Directory().Logback, file_name)


def resolve_project_data(file_name: str):
    """
    Used to resolve file in '{PROJECT_ROOT}' directory.
    """
    return os.path.join(Directory().ProjectRoot, file_name)


def _get_root_package():
    main_module = sys.modules.get('__main__')

    if main_module and hasattr(main_module, '__package__') and main_module.__package__:
        return main_module.__package__

    return None
