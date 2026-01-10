import dataclasses
import sys
from importlib.metadata import entry_points
from typing import cast

from PyQt6.QtWidgets import QApplication
from kui.core.service.tr import TextResourceService
from kutil.meta import SingletonMeta
from kutil.reflection import get_members

from kui.core._service import AppService
from kui.core.service.config import AppConfigService
from kui.core.service.discovery import ProjectDiscoveryService
from kui.core.service.data import DataHolderService
from kui.core.service.provider import DataProviderService
from kui.core.service.startup import StartupService, KamaStartupWorker
from kui.core.service.style import StyleManagerService
from kui.core.window import KamaWindow
from kui.style.color import ColorResolver, RgbaResolver
from kui.style.font import FontResolver
from kui.style.image import ImageResolver


@dataclasses.dataclass
class KamaApplicationContext:
    application: "KamaApplication"


class KamaApplication(metaclass=SingletonMeta):

    window_type = KamaWindow

    app_config_service_type = AppConfigService
    discovery_service_type = ProjectDiscoveryService
    style_manager_service_type = StyleManagerService
    startup_service_type = StartupService
    data_provider_service_type = DataProviderService
    text_resource_service_type = TextResourceService
    data_holder_service_type = DataHolderService

    def __init__(self):
        self.__application = QApplication(sys.argv)
        self.__services: dict[str, AppService] = {}

    def set_stylesheet(self, stylesheet: str):
        self.__application.setStyleSheet(stylesheet)

    @property
    def provider(self) -> DataProviderService:
        service = self.get_app_service("data_provider", self.data_provider_service_type)
        return cast(DataProviderService, service)

    @property
    def discovery(self) -> ProjectDiscoveryService:
        service = self.get_app_service("project_discovery", self.discovery_service_type)
        return cast(ProjectDiscoveryService, service)

    @property
    def style(self) -> StyleManagerService:
        service = self.get_app_service("style_manager", self.style_manager_service_type)
        return cast(StyleManagerService, service)

    @property
    def window(self) -> KamaWindow:
        service = self.get_app_service("window", self.window_type)
        return cast(KamaWindow, service)

    @property
    def config(self) -> AppConfigService:
        service = self.get_app_service("config", self.app_config_service_type)
        return cast(AppConfigService, service)

    @property
    def startup(self) -> StartupService:
        service = self.get_app_service("startup", self.startup_service_type)
        return cast(StartupService, service)

    @property
    def translations(self) -> TextResourceService:
        service = self.get_app_service("text_resource", self.text_resource_service_type)
        return cast(TextResourceService, service)

    @property
    def data(self) -> DataHolderService:
        service = self.get_app_service("dynamic_data_holder", self.data_holder_service_type)
        return cast(DataHolderService, service)

    def exec(self):
        self.__discover_plugins()

        self.window.manager.load_components()
        self.window.manager.load_controllers()

        self.style.builder.add_resolver(ColorResolver())
        self.style.builder.add_resolver(RgbaResolver())
        self.style.builder.add_resolver(FontResolver())
        self.style.builder.add_resolver(ImageResolver())

        self.__collect_startup_tasks()
        self.startup.start()

        return self.__application.exec()

    def get_app_service(self, service_name: str, service_type = None):
        if service_name in self.__services.keys():
            return self.__services.get(service_name)

        if service_type is None:
            raise RuntimeError("Can't initialize application service without type.")

        context = KamaApplicationContext(self)
        service = service_type(context)

        self.__services[service_name] = service
        return service

    def __collect_startup_tasks(self):
        for member_name, member in get_members(self.config.startup_package, KamaStartupWorker):
            task: KamaStartupWorker = member()
            self.startup.add_task(task)

    @staticmethod
    def __discover_plugins():
        for plugin in entry_points(group="kama_ui.plugins"):
            plugin.load()
