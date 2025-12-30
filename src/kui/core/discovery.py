import os.path
from typing import TYPE_CHECKING, Final
from kutil.file import get_runtime_root

if TYPE_CHECKING:
    from kui.core.app import KamaApplication


class ProjectDiscovery:

    Config: Final[str] = "Config"
    Resources: Final[str] = "Resources"
    Styles: Final[str] = "Styles"
    Output: Final[str] = "Output"
    Logback: Final[str] = "Logback"
    Logs: Final[str] = "Logs"

    def __init__(self, application: "KamaApplication"):
        self.__application = application

    @classmethod
    def project(cls, *paths: str):
        return os.path.join(get_runtime_root(), *paths)

    def app_data(self, *paths: str):
        app_data_directory = os.getenv("APPDATA") or ""
        app_name = self.__application.name

        return os.path.join(app_data_directory, app_name, *paths)

    def config(self, *paths: str):
        return os.path.join(self.project(), self.Config, *paths)

    def resources(self, *paths: str, include_temporary: bool = True):
        temp_resource_path = self.temp_resources(*paths)

        if include_temporary and os.path.exists(temp_resource_path):
            return temp_resource_path

        return os.path.join(self.project(), self.Resources, *paths)

    def styles(self, *paths: str):
        return os.path.join(self.project(), self.Styles, *paths)

    def logback(self, *paths: str):
        return os.path.join(self.app_data(), self.Logback, *paths)

    def logs(self, *paths: str):
        return os.path.join(self.app_data(), self.Logs, *paths)

    def output(self, *paths: str):
        return os.path.join(self.app_data(), self.Output, *paths)

    def temp_resources(self, *paths: str):
        return os.path.join(self.output(), self.Resources, *paths)
