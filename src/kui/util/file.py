import sys
import time
from pathlib import Path

from kutil.file import save_file


def get_project_dir() -> Path:
    """
    Returns the root directory of the application.
    Works for:
    1. Standard Python scripts (searching for markers).
    2. Compiled .exe files (PyInstaller/Nuitka).
    """

    # todo: remove
    log = ""

    # 1. Check if the app is running as a compiled bundle (.exe)
    if getattr(sys, "frozen", False):
        log += str(Path(sys.executable).parent) + "\n"
        # If frozen, sys.executable is the path to the actual .exe file
        if hasattr(sys, "_MEIPASS"):
            log += str(Path(sys._MEIPASS)) + "\n"
            save_file("C:\\Users\\djara\\AppData\\Roaming\\SaveGem\\test.txt", log)
            return Path(sys._MEIPASS)
        save_file("C:\\Users\\djara\\AppData\\Roaming\\SaveGem\\test.txt", log)
        return Path(sys.executable).parent

    # 2. If running as a normal script, use the marker-based search
    # Starting from the script entry point
    start_path = Path(sys.argv[0]).resolve()
    log += "start_path" + str(start_path) + "\n"

    if not start_path.exists():
        start_path = Path.cwd().resolve()

    log += "start_path_after" + str(start_path) + "\n"

    root_markers = {"kamaconfig.yaml", "kamaconfig.yml"}

    for parent in [start_path] + list(start_path.parents):
        for marker in root_markers:
            marker_path = parent / marker

            if marker_path.exists():
                log += "found" + str(parent) + "\n"
                save_file("C:\\Users\\djara\\AppData\\Roaming\\SaveGem\\test.txt", log)
                return parent

    # Fallback to current working directory
    log += "fallback" + str(Path.cwd().resolve()) + "\n"
    save_file("C:\\Users\\djara\\AppData\\Roaming\\SaveGem\\test.txt", log)
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
    """
    Returns the Path to the main entry point of the application.
    Works for standard Python scripts and frozen executables (PyInstaller).
    """

    # 1. Handle Frozen Executables (e.g., PyInstaller)
    if getattr(sys, 'frozen', False):
        # sys.executable is the path to the actual .exe or binary
        return Path(sys.executable).resolve()

    # 2. Handle Standard Scripts
    main_module = sys.modules.get('__main__')
    if main_module and hasattr(main_module, '__file__'):
        return Path(main_module.__file__).resolve()

    # 3. Fallback to argv[0] if __main__ is ambiguous
    if sys.argv and sys.argv[0]:
        return Path(sys.argv[0]).resolve()

    raise RuntimeError("Can't determine path of entry point.")


def get_root_package() -> str:
    """
    Determines the root package name by climbing up from the entry point
    until it finds the top-most directory containing an __init__.py file.
    """
    log = ""
    # 1. Get the starting directory
    entry_file = get_entry_point()
    current_dir = entry_file.parent if entry_file.is_file() else entry_file

    root_pkg_path = None


    log += "1 " + str(sys._MEIPASS) + "\n"
    save_file("C:\\Users\\djara\\AppData\\Roaming\\SaveGem\\test2.txt", log)
    time.sleep(10000)

    # 2. Climb up as long as we are inside a package (__init__.py exists)
    # This works for nested packages like 'my_org.my_project.app'
    temp_dir = current_dir
    while (temp_dir / "__init__.py").exists():
        root_pkg_path = temp_dir
        # Move up one level
        parent = temp_dir.parent
        if parent == temp_dir:  # Reached filesystem root
            break
        temp_dir = parent

    # 3. If we found a package boundary, reconstruct the dot-notation name
    if root_pkg_path:
        # Calculate the relative path from the root package to our entry dir
        # and convert it to dots (e.g., 'org/app' -> 'org.app')
        relative = current_dir.relative_to(root_pkg_path.parent)
        log += "2 " + ".".join(relative.parts) + "\n"
        save_file("C:\\Users\\djara\\AppData\\Roaming\\SaveGem\\test2.txt", log)

        return ".".join(relative.parts)

    # 4. Fallback: If no __init__.py is found, the folder itself is the "package"
    log += "3 " + str(current_dir.name) + "\n"
    save_file("C:\\Users\\djara\\AppData\\Roaming\\SaveGem\\test2.txt", log)
    return current_dir.name
