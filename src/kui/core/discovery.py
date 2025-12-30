import os.path
from typing import TYPE_CHECKING
from kui.util.file import get_project_dir

if TYPE_CHECKING:
    from kui.core.app import KamaApplication


class ProjectDiscovery:

    def __init__(self, application: "KamaApplication"):
        self.__application = application

    @property
    def ProjectRoot(self):  # noqa
        return get_project_dir()

    @property
    def AppData(self):  # noqa
        app_data_directory = os.getenv("APPDATA") or ""
        app_name = self.__application.name

        return os.path.join(app_data_directory, app_name)

    @property
    def Config(self):  # noqa
        return os.path.join(self.ProjectRoot, "Config")

    @property
    def Styles(self):  # noqa
        return os.path.join(self.ProjectRoot, "Styles")

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
    def Resources(self):  # noqa
        return os.path.join(self.ProjectRoot, "Resources")

    @property
    def TempResources(self):  # noqa
        return os.path.join(self.Output, "Resources")

    def project(self, *paths: str):
        return os.path.join(self.ProjectRoot, *paths)

    def app_data(self, *paths: str):
        return os.path.join(self.AppData, *paths)

    def config(self, *paths: str):
        return os.path.join(self.Config, *paths)

    def resources(self, *paths: str, include_temporary: bool = True):
        temp_resource_path = self.temp_resources(*paths)

        if include_temporary and os.path.exists(temp_resource_path):
            return temp_resource_path

        return os.path.join(self.Resources, *paths)

    def styles(self, *paths: str):
        return os.path.join(self.Styles, *paths)

    def logback(self, *paths: str):
        return os.path.join(self.Logback, *paths)

    def logs(self, *paths: str):
        return os.path.join(self.Logs, *paths)

    def output(self, *paths: str):
        return os.path.join(self.Output, *paths)

    def temp_resources(self, *paths: str):
        return os.path.join(self.TempResources, *paths)
