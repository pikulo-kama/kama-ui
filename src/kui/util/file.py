import sys
from pathlib import Path


def resolve_root_package(*package_list: str) -> str:
    """
    Returns the name of the package where the main script is located.
    If run as 'python -m savegem.app.main', it returns 'savegem.app'.
    """

    package_list = list(package_list)
    package_list.insert(0, get_root_package())

    return ".".join(package_list)


def get_entrypoint_path():
    if getattr(sys, 'frozen', False):
        return Path(sys.executable).resolve()

    # Fallback to sys.argv[0] if __main__ lacks __file__
    main_module = sys.modules.get("__main__")
    main_file = getattr(main_module, "__file__", sys.argv[0])

    return Path(main_file).resolve()

def get_root_package():
    main_module = sys.modules.get('__main__')
    root_package = getattr(main_module, "__package__")

    if root_package:
        return root_package

    parts = []
    entry_path = get_entrypoint_path()
    current = entry_path.parent

    while (current / "__init__.py").exists():
        parts.append(current.name)
        current = current.parent

    return ".".join(reversed(parts))
