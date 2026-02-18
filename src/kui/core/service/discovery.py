from typing import TYPE_CHECKING
import os.path
from kui.util.file import get_project_dir
from kui.core._service import AppService

if TYPE_CHECKING:
    from kui.core.app import KamaApplicationContext


class ProjectDiscoveryService(AppService):
    """
    Service responsible for locating and managing project and system directories.
    """

    def __init__(self, context: "KamaApplicationContext"):
        """
        Initializes the service and ensures necessary application data directories exist.
        """

        super().__init__(context)

        directories = [
            self.AppData,
            self.Output,
            self.TempImages,
            self.Logback,
            self.Logs,
        ]

        for directory in directories:
            if not os.path.exists(directory):
                os.mkdir(directory)

    @property
    def ProjectRoot(self):  # noqa
        """
        Returns the absolute path to the project's root directory.
        """
        return get_project_dir()

    @property
    def AppData(self):  # noqa
        """
        Returns the path to the application's data folder within the user's profile.
        """

        app_data_directory = os.getenv("APPDATA") or ""
        return os.path.join(app_data_directory, self.application.config.name)

    @property
    def Resources(self):  # noqa
        """
        Returns the path to the static Resources directory.
        """
        return os.path.join(self.ProjectRoot, "Resources")

    @property
    def Styles(self):  # noqa
        """
        Returns the path to the Styles directory within Resources.
        """
        return os.path.join(self.Resources, "Styles")

    @property
    def Images(self):  # noqa
        """
        Returns the path to the static Images directory within Resources.
        """
        return os.path.join(self.Resources, "Images")

    @property
    def Locales(self):  # noqa
        """
        Returns the path to the static Images directory within Resources.
        """
        return os.path.join(self.Resources, "Locales")

    @property
    def Layouts(self):  # noqa
        """
        Returns the path to the static Images directory within Resources.
        """
        return os.path.join(self.Resources, "Layouts")

    @property
    def Output(self):  # noqa
        """
        Returns the path to the application's Output directory.
        """
        return os.path.join(self.AppData, "Output")

    @property
    def Logback(self):  # noqa
        """
        Returns the path to the application's Logback directory.
        """
        return os.path.join(self.AppData, "Logback")

    @property
    def Logs(self):  # noqa
        """
        Returns the path to the application's Logs directory.
        """
        return os.path.join(self.AppData, "Logs")

    @property
    def TempImages(self):  # noqa
        """
        Returns the path to the temporary Images directory in AppData.
        """
        return os.path.join(self.AppData, "Images")

    def package(self, *paths: str):
        """
        Constructs a dot-notated Python package path starting from the base package.
        """

        paths = list(paths)
        paths.insert(0, self.application.config.base_package)

        return ".".join(paths)

    def project(self, *paths: str):
        """
        Constructs a path relative to the project root.
        """
        return os.path.join(self.ProjectRoot, *paths)

    def app_data(self, *paths: str):
        """
        Constructs a path relative to the application data directory.
        """
        return os.path.join(self.AppData, *paths)

    def resources(self, *paths: str):
        return os.path.join(self.Resources, *paths)

    def images(self, *paths: str, include_temporary: bool = True):
        """
        Resolves an image path, prioritizing temporary AppData images if they exist.
        """

        temp_resource_path = self.temp_images(*paths)

        if include_temporary and os.path.exists(temp_resource_path):
            return temp_resource_path

        return os.path.join(self.Images, *paths)

    def styles(self, *paths: str):
        """
        Constructs a path relative to the Styles directory.
        """
        return os.path.join(self.Styles, *paths)

    def locales(self, *paths: str):
        """
        Constructs a path relative to the Styles directory.
        """
        return os.path.join(self.Locales, *paths)

    def layouts(self, *paths: str):
        """
        Constructs a path relative to the Styles directory.
        """
        return os.path.join(self.Layouts, *paths)

    def logback(self, *paths: str):
        """
        Constructs a path relative to the Logback directory.
        """
        return os.path.join(self.Logback, *paths)

    def logs(self, *paths: str):
        """
        Constructs a path relative to the Logs directory.
        """
        return os.path.join(self.Logs, *paths)

    def output(self, *paths: str):
        """
        Constructs a path relative to the Output directory.
        """
        return os.path.join(self.Output, *paths)

    def temp_images(self, *paths: str):
        """
        Constructs a path relative to the temporary AppData Images directory.
        """
        return os.path.join(self.TempImages, *paths)
