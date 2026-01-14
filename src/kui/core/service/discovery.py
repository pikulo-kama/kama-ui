from typing import TYPE_CHECKING
import os.path
from kui.util.file import get_project_dir
from kui.core._service import AppService

if TYPE_CHECKING:
    from kui.core.app import KamaApplicationContext


class ProjectDiscoveryService(AppService):

    def __init__(self, context: "KamaApplicationContext"):
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
        return get_project_dir()

    @property
    def AppData(self):  # noqa
        app_data_directory = os.getenv("APPDATA") or ""
        return os.path.join(app_data_directory, self.application.config.name)

    @property
    def Resources(self):  # noqa
        return os.path.join(self.ProjectRoot, "Resources")

    @property
    def Data(self):  # noqa
        return os.path.join(self.Resources, "Data")

    @property
    def Styles(self):  # noqa
        return os.path.join(self.Resources, "Styles")

    @property
    def Images(self):  # noqa
        return os.path.join(self.Resources, "Images")

    @property
    def Output(self):  # noqa
        return os.path.join(self.AppData, "Output")

    @property
    def Logback(self):  # noqa
        return os.path.join(self.AppData, "Logback")

    @property
    def Logs(self):  # noqa
        return os.path.join(self.AppData, "Logs")

    @property
    def TempImages(self):  # noqa
        return os.path.join(self.AppData, "Images")

    def package(self, *paths: str):
        paths = list(paths)
        paths.insert(0, self.application.config.base_package)

        return ".".join(paths)

    def project(self, *paths: str):
        return os.path.join(self.ProjectRoot, *paths)

    def app_data(self, *paths: str):
        return os.path.join(self.AppData, *paths)

    def data(self, *paths: str):
        return os.path.join(self.Data, *paths)

    def images(self, *paths: str, include_temporary: bool = True):
        temp_resource_path = self.temp_images(*paths)

        if include_temporary and os.path.exists(temp_resource_path):
            return temp_resource_path

        return os.path.join(self.Images, *paths)

    def styles(self, *paths: str):
        return os.path.join(self.Styles, *paths)

    def logback(self, *paths: str):
        return os.path.join(self.Logback, *paths)

    def logs(self, *paths: str):
        return os.path.join(self.Logs, *paths)

    def output(self, *paths: str):
        return os.path.join(self.Output, *paths)

    def temp_images(self, *paths: str):
        return os.path.join(self.TempImages, *paths)
