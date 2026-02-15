import sys
from pathlib import Path


def get_project_dir() -> Path:
    """
    Determines the root directory of the project using frozen detection or marker search.

    Returns:
        Path: The absolute path to the project root directory.
    """

    # 1. Check if the app is running as a compiled bundle (.exe)
    if getattr(sys, "frozen", False):
        # If frozen, sys.executable is the path to the actual .exe file.
        # PyInstaller specific: _MEIPASS holds the temporary extraction path.
        if hasattr(sys, "_MEIPASS"):
            return Path(sys._MEIPASS)  # noqa

        return Path(sys.executable).parent

    # 2. If running as a normal script, use the marker-based search
    # Starting from the script entry point
    start_path = Path(sys.argv[0]).resolve()

    if not start_path.exists():
        start_path = Path.cwd().resolve()

    root_markers = {"kamaconfig.yaml", "kamaconfig.yml"}

    # Recursively check parent directories for the config file
    for parent in [start_path] + list(start_path.parents):
        for marker in root_markers:
            marker_path = parent / marker

            if marker_path.exists():
                return parent

    # Fallback to current working directory
    return Path.cwd().resolve()


def get_files_from_directory(path: str | Path, recursive: bool = False, extension: str = None):
    path = Path(path)
    content: list[str] = []

    if not path.exists():
        return content

    for entry in path.iterdir():
        if entry.is_dir():
            if recursive:
                content.extend(get_files_from_directory(entry))
            continue

        if extension is not None and not entry.name.endswith(extension):
            continue

        content.append(entry.read_text(encoding="utf-8"))

    return content
