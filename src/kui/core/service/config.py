import os
from typing import TYPE_CHECKING, Any

from kui.core._service import AppService
from kui.core.yaml_holder import YamlHolder
from kui.util.file import get_project_dir
from kutil.file_type import SVG

if TYPE_CHECKING:
    from kui.core.app import KamaApplicationContext


class AppConfigService(AppService, YamlHolder):

    def __init__(self, context: "KamaApplicationContext"):
        AppService.__init__(self, context)
        YamlHolder.__init__(self, os.path.join(get_project_dir(), "kamaconfig"))

    @property
    def name(self):
        return self.get("application.name", "KamaUI")

    @property
    def author(self):
        return self.get("application.author", "KamaUI")

    @property
    def icon(self):
        return self.get("application.icon", SVG.add_extension("application"))

    @property
    def default_locale(self):
        return self.get("application.locale", "en_US")

    @property
    def base_package(self):
        return self.get("application.base-package")

    @property
    def component_package(self):
        return self.get("application.component-package")

    @property
    def controller_package(self):
        return self.get("application.controller-package")

    @property
    def resolver_package(self):
        return self.get("application.resolver-package")

    @property
    def startup_package(self):
        return self.get("application.startup-package")

    def get(self, property_name: str, default_value: Any = ""):
        value = super().get(property_name, default_value)

        if not isinstance(value, str):
            return value

        if "{AppDataDirectory}" in value:
            path = value.replace("{AppDataDirectory}", "")
            value = self.application.discovery.app_data(path)

        if "{base}" in value:
            value = value.replace("{base}", self.base_package)

        return value
