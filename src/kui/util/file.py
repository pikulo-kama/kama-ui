import sys
from pathlib import Path


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
        if hasattr(sys, "_MEIPASS"):
            return Path(sys._MEIPASS)  # noqa

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
