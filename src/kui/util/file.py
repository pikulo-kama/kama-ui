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
    entry_file = None

    # 1. Check if the entry point already knows its package
    if hasattr(main_module, '__package__') and main_module.__package__:
        return main_module.__package__

    # 2. Get the physical path of the entry point
    # In PyInstaller, this will be the path to the EXE or the injected script
    if hasattr(sys, 'frozen'):
        entry_file = Path(sys.executable if sys.frozen else sys.argv[0]).resolve()

    elif hasattr(main_module, "__file__"):
        entry_file = Path(main_module.__file__).resolve()

    if not entry_file:
        raise RuntimeError("Can't determine path to entry point.")

    # 3. Match the physical path against loaded modules
    # This is the "magic" part: we look for which loaded module
    # matches the directory of our entry point.

    for name, module in sys.modules.items():
        if hasattr(module, '__file__') and module.__file__:
            module_path = Path(module.__file__).resolve()

            if module_path.parent == entry_file.parent and '.' in name:
                return name

    raise RuntimeError("Can't determine application root package.")
