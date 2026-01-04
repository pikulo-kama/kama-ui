import sys
from importlib.metadata import entry_points

from PyQt6.QtWidgets import QApplication
from kamatr.manager import TextResourceManager
from kutil.meta import SingletonMeta
from kutil.reflection import get_members

from kui.core.config import AppConfig
from kui.core.discovery import ProjectDiscovery
from kui.core.data import DataHolder
from kui.core.provider import ProviderManager
from kui.core.startup import StartupJob, KamaStartupWorker
from kui.core.style import StyleManager
from kui.core.window import KamaWindow
from kui.style.color import ColorResolver, RgbaResolver
from kui.style.font import FontResolver
from kui.style.image import ImageResolver


class KamaApplication(metaclass=SingletonMeta):

    def __init__(self):
        self.__application = QApplication(sys.argv)

        self.__config = AppConfig(self)
        self.__discovery = ProjectDiscovery(self)
        self.__style_manager = StyleManager(self)
        self.__startup_job = StartupJob(self)
        self.__window = KamaWindow(self)
        self.__provider_manager = ProviderManager(self)
        self.__text_resources = TextResourceManager()
        self.__data_holder = DataHolder()

    @property
    def name(self):
        return self.config.get("application.name", "KamaUI")

    @property
    def locale(self):
        return self.text_resources.locale or self.config.get("application.locale", "en_US")

    @locale.setter
    def locale(self, locale: str):
        self.text_resources.locale = locale

    @property
    def locales(self):
        return self.__text_resources.locales

    @property
    def provider(self) -> ProviderManager:
        return self.__provider_manager

    @property
    def discovery(self):
        return self.__discovery

    @property
    def text_resources(self) -> TextResourceManager:
        return self.__text_resources

    @property
    def style(self) -> StyleManager:
        return self.__style_manager

    @property
    def data(self) -> DataHolder:
        return self.__data_holder

    def set_stylesheet(self, stylesheet: str):
        self.__application.setStyleSheet(stylesheet)

    @property
    def window(self) -> KamaWindow:
        return self.__window

    @property
    def config(self) -> AppConfig:
        return self.__config

    def exec(self):
        self.__discover_plugins()
        self.window.manager.load_components()
        self.window.manager.load_controllers()

        self.style.builder.add_resolver(ColorResolver())
        self.style.builder.add_resolver(RgbaResolver())
        self.style.builder.add_resolver(FontResolver())
        self.style.builder.add_resolver(ImageResolver())

        self.__collect_startup_tasks()

        self.__startup_job.start()
        return self.__application.exec()

    def add_startup_task(self, startup_task: KamaStartupWorker):
        self.__startup_job.add_task(startup_task)

    @staticmethod
    def __discover_plugins():
        for plugin in entry_points(group="kama_ui.plugins"):
            plugin.load()

    def __collect_startup_tasks(self):
        custom_startup_package = self.config.get("application.startup-package", "")

        for member_name, member in get_members(custom_startup_package, KamaStartupWorker):
            task: KamaStartupWorker = member()
            self.__startup_job.add_task(task)
