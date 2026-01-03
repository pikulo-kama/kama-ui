import os
from typing import TYPE_CHECKING, Any

from kui.core._service import AppService
from kui.core.yaml_holder import YamlHolder
from kui.util.file import get_project_dir

if TYPE_CHECKING:
    from kui.core.app import KamaApplication


class AppConfig(AppService, YamlHolder):

    def __init__(self, application: "KamaApplication"):
        AppService.__init__(self, application)
        YamlHolder.__init__(self, os.path.join(get_project_dir(), "kamaconfig"))

    def get(self, property_name: str, default_value: Any = None):
        value = super().get(property_name, default_value)

        if not isinstance(value, str):
            return value

        if "{AppDataDirectory}" in value:
            path = value.replace("{AppDataDirectory}", "")
            value = self.application.discovery.app_data(path)

        if "{base}" in value:
            value = value.replace("{base}", self.get("application.base-package", ""))

        return value
