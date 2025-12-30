import sys
from pathlib import Path

from kutil.file import save_file


def get_project_dir() -> Path:
    """
    Returns the root directory of the application.
    Works for:
    1. Standard Python scripts (searching for markers).
    2. Compiled .exe files (PyInstaller/Nuitka).
    """

    # 1. Check if the app is running as a compiled bundle (.exe)
    if getattr(sys, "frozen", False):
        # If frozen, sys.executable is the path to the actual .exe file
        return Path(sys.executable).parent

    # 2. If running as a normal script, use the marker-based search
    # Starting from the script entry point
    start_path = Path(sys.argv[0]).resolve()

    if not start_path.exists():
        start_path = Path.cwd().resolve()

    root_markers = {"kamaconfig.yaml", "kamaconfig.yml"}

    for parent in [start_path] + list(start_path.parents):
        for marker in root_markers:
            marker_path = parent / marker

            if marker_path.exists():
                return parent

    # Fallback to current working directory
    return Path.cwd().resolve()


def resolve_root_package(*package_list: str) -> str:
    """
    Returns the name of the package where the main script is located.
    If run as 'python -m savegem.app.main', it returns 'savegem.app'.
    """

    package_list = list(package_list)
    package_list.insert(0, get_root_package())

    return ".".join(package_list)


def get_entry_point() -> Path:
    main_module = sys.modules.get('__main__')

    if hasattr(sys, 'frozen'):
        return Path(sys.executable if sys.frozen else sys.argv[0]).resolve()

    if hasattr(main_module, "__file__"):
        return Path(main_module.__file__).resolve()

    raise RuntimeError("Can't determine path of entry point.")


def get_root_package():
    entry_file = get_entry_point()
    main_module = sys.modules.get('__main__')

    # 1. Check if the entry point already knows its package
    if hasattr(main_module, '__package__') and main_module.__package__:
        return main_module.__package__

    # 3. Match the physical path against loaded modules
    # This is the "magic" part: we look for which loaded module
    # matches the directory of our entry point.

    # Todo: debugging
    data: dict = {"entry_file": entry_file.name}
    module_name = None

    for name, module in sys.modules.items():
        if hasattr(module, '__file__') and module.__file__:
            module_path = Path(module.__file__).resolve()
            data[name] = module_path.name

            if module_path.parent == entry_file.parent and '.' in name:
                module_name = name
                break

    if module_name is None:
        raise RuntimeError("Can't determine application root package.")

    save_file("C:\\Users\\djara\\AppData\\Roaming\\SaveGem\\test.json", data, as_json=True)
    return module_name
