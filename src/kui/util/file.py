import os
import sys
from importlib import resources
from pathlib import Path

from kui.core.constants import Directory


def resolve_root_package(*package_list: str) -> str:
    """
    Returns the name of the package where the main script is located.
    If run as 'python -m savegem.app.main', it returns 'savegem.app'.
    """

    package_list = list(package_list)
    package_list.insert(0, get_root_package())

    return ".".join(package_list)


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
    package_path = str(resources.files(get_root_package()))
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

def get_entrypoint_path():
    if getattr(sys, 'frozen', False):
        return Path(sys.executable).resolve()

    # Fallback to sys.argv[0] if __main__ lacks __file__
    main_module = sys.modules.get("__main__")
    main_file = getattr(main_module, "__file__", sys.argv[0])

    return Path(main_file).resolve()

def get_root_package():
    main_module = sys.modules.get('__main__')
    root_package = getattr(main_module, "__package__", "")

    if len(root_package) > 0:
        return root_package

    parts = []
    entry_path = get_entrypoint_path()
    current = entry_path.parent

    while (current / "__init__.py").exists():
        parts.append(current.name)
        current = current.parent

    return ".".join(reversed(parts))
