import dataclasses
from importlib.metadata import entry_points
from typing import cast, Type

from kui.core.service.reader import ResourceReader
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
    """
    Contextual wrapper used to pass the application instance to services.
    """
    application: "KamaApplication"


class KamaApplication(metaclass=SingletonMeta):
    """
    The main application class that coordinates services, windows, and plugins.
    """

    window_type = KamaWindow

    app_config_service_type = AppConfigService
    discovery_service_type = ProjectDiscoveryService
    style_manager_service_type = StyleManagerService
    startup_service_type = StartupService
    data_provider_service_type = DataProviderService
    text_resource_service_type = TextResourceService
    data_holder_service_type = DataHolderService
    resource_reader_service_type = ResourceReader

    def __init__(self):
        """
        Initializes the service storage dictionary.
        """
        self.__services: dict[str, AppService] = {}

    @staticmethod
    def post_init():
        """
        Loads external plugins registered via entry points.
        """

        for plugin in entry_points(group="kama_ui.plugins"):
            plugin.load()

    def exec(self):
        """
        Begins the application execution sequence, including service setup and window display.
        """

        self.resources.read()

        self.window.manager.load_components()
        self.window.manager.load_controllers()

        self.style.builder.add_resolver(ColorResolver())
        self.style.builder.add_resolver(RgbaResolver())
        self.style.builder.add_resolver(FontResolver())
        self.style.builder.add_resolver(ImageResolver())

        for member_name, member in get_members(self.config.startup_package, KamaStartupWorker):
            task: KamaStartupWorker = member()
            self.startup.add_task(task)

        self.startup.start()
        self.window.exec()

    @property
    def window(self) -> KamaWindow:
        """
        Accesses the main application window service.
        """

        service = self.get_app_service("window", self.window_type)
        return cast(KamaWindow, service)

    @property
    def provider(self) -> DataProviderService:
        """
        Accesses the data provider service.
        """

        service = self.get_app_service("data_provider", self.data_provider_service_type)
        return cast(DataProviderService, service)

    @property
    def resources(self) -> ResourceReader:
        service = self.get_app_service("resource_reader", self.resource_reader_service_type)
        return cast(ResourceReader, service)

    @property
    def style(self) -> StyleManagerService:
        """
        Accesses the style manager service.
        """

        service = self.get_app_service("style_manager", self.style_manager_service_type)
        return cast(StyleManagerService, service)

    @property
    def discovery(self) -> ProjectDiscoveryService:
        """
        Accesses the project discovery service.
        """

        service = self.get_app_service("project_discovery", self.discovery_service_type)
        return cast(ProjectDiscoveryService, service)

    @property
    def config(self) -> AppConfigService:
        """
        Accesses the application configuration service.
        """

        service = self.get_app_service("config", self.app_config_service_type)
        return cast(AppConfigService, service)

    @property
    def startup(self) -> StartupService:
        """
        Accesses the startup orchestration service.
        """

        service = self.get_app_service("startup", self.startup_service_type)
        return cast(StartupService, service)

    @property
    def translations(self) -> TextResourceService:
        """
        Accesses the text resource and translation service.
        """

        service = self.get_app_service("text_resource", self.text_resource_service_type)
        return cast(TextResourceService, service)

    @property
    def data(self) -> DataHolderService:
        """
        Accesses the dynamic data holder service.
        """

        service = self.get_app_service("dynamic_data_holder", self.data_holder_service_type)
        return cast(DataHolderService, service)

    def get_app_service(self, service_name: str, service_type: Type[AppService] = None):
        """
        Retrieves an existing service or initializes it if it doesn't exist.
        """

        if service_name in self.__services.keys():
            return self.__services.get(service_name)

        if service_type is None:
            raise RuntimeError("Can't initialize application service without type.")

        context = KamaApplicationContext(self)
        service = service_type(context)

        self.__services[service_name] = service
        return service
