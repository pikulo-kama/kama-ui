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

    @property
    def project_root(self):
        return get_runtime_root()

    @property
    def app_data_root(self):
        app_data_directory = os.getenv("APPDATA") or ""
        app_name = self.__application.config.get("name", "KamaUI")

        return os.path.join(app_data_directory, app_name)

    def get_config_directory(self, *path: str):
        return os.path.join(self.project_root, self.Config, *path)

    def get_resources_directory(self, *path: str):
        return os.path.join(self.project_root, self.Resources, *path)

    def get_styles_directory(self, *path: str):
        return os.path.join(self.project_root, self.Styles, *path)

    def get_logback_directory(self, *path: str):
        return os.path.join(self.app_data_root, self.Logback, *path)

    def get_logs_directory(self, *path: str):
        return os.path.join(self.app_data_root, self.Logs, *path)

    def get_output_directory(self, *path: str):
        return os.path.join(self.app_data_root, self.Output, *path)

    def get_temp_resources_directory(self, *path: str):
        return os.path.join(self.get_output_directory(), self.Resources, *path)
