import os.path
import sys
from importlib.metadata import entry_points
from typing import Any

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QApplication
from kui.core.discovery import ProjectDiscovery
from kui.core.yaml_holder import YamlHolder
from kutil.file import read_file, save_file
from kutil.meta import SingletonMeta

from kui.core.holder import DataHolder
from kui.core.provider import MetadataProvider, ControllerSectionProvider
from kui.core.startup import StartupJob, KamaStartupWorker
from kui.core.style import ColorMode, StyleBuilder
from kamatr.manager import TextResourceManager
from kui.core.window import KamaWindow
from kui.style.font import KamaFont
from kui.style.color import KamaComposedColor
from kui.style.image import DynamicResource
from kui.style.color import ColorResolver, RgbaColorResolver
from kui.style.font import FontResolver
from kui.style.image import ImageResolver
from kui.util.file import get_project_dir
from kutil.reflection import get_members


class KamaApplication(metaclass=SingletonMeta):

    def __init__(self):
        self.__application = QApplication(sys.argv)
        self.__config = YamlHolder(os.path.join(get_project_dir(), "kamaconfig"))
        self.__discovery = ProjectDiscovery(self)
        self.__style_builder = StyleBuilder(self)
        self.__startup_job = StartupJob(self)
        self.__window = KamaWindow(self)
        self.__text_resources = TextResourceManager()
        self.__data_holder = DataHolder()
        self.__dynamic_resources: list[DynamicResource] = []
        self.__color_mode = None

        self.__metadata_provider = MetadataProvider()
        self.__section_provider = ControllerSectionProvider()

        self.__fonts: dict[str, KamaFont] = {}
        self.__colors: dict[str, KamaComposedColor] = {}

    @property
    def name(self):
        return self.prop("application.name", "KamaUI")

    @property
    def color_mode(self):
        if self.__color_mode is not None:
            return self.__color_mode

        return self.__get_system_color_mode()

    @color_mode.setter
    def color_mode(self, color_mode: str):
        self.__color_mode = color_mode

    @property
    def locale(self):
        return self.text_resources.locale or self.prop("locale", "en_US")

    @locale.setter
    def locale(self, locale: str):
        self.text_resources.locale = locale

    @property
    def locales(self):
        return self.__text_resources.locales

    def get_color(self, color_code: str):
        color = self.__colors.get(color_code)

        if not color:
            return None

        if self.color_mode == ColorMode.Light:
            return color.light_color

        return color.dark_color

    @property
    def metadata_provider(self):
        return self.__metadata_provider

    @metadata_provider.setter
    def metadata_provider(self, metadata_provider: MetadataProvider):
        self.__metadata_provider = metadata_provider

    @property
    def section_provider(self):
        return self.__section_provider

    @section_provider.setter
    def section_provider(self, section_provider: ControllerSectionProvider):
        self.__section_provider = section_provider

    @property
    def discovery(self):
        return self.__discovery

    @property
    def fonts(self):
        return self.__fonts

    @property
    def style_builder(self):
        return self.__style_builder

    @property
    def text_resources(self) -> TextResourceManager:
        return self.__text_resources

    @property
    def data(self) -> DataHolder:
        return self.__data_holder

    def set_stylesheet(self, stylesheet: str):
        self.__application.setStyleSheet(stylesheet)

    @property
    def window(self) -> KamaWindow:
        return self.__window

    def exec(self):
        self.__discover_plugins()
        self.__window.manager.load_components()
        self.__window.manager.load_controllers()

        self.__style_builder.add_resolver(ColorResolver())
        self.__style_builder.add_resolver(RgbaColorResolver())
        self.__style_builder.add_resolver(FontResolver())
        self.__style_builder.add_resolver(ImageResolver())

        self.__collect_startup_tasks()
        self.__startup_job.start()

        return self.__application.exec()

    def prop(self, property_name: str, default_value: Any = None):
        # todo: refactor
        app_data_token = "{AppDataDirectory}"
        base_package_token = "{base}"

        value = self.__config.get(property_name, default_value)

        if not isinstance(value, str):
            return value

        if app_data_token in value:
            path = value.replace(app_data_token, "")
            value = self.__discovery.app_data(path)

        if base_package_token in value:
            value = value.replace(base_package_token, self.prop("application.base-package", ""))

        return value

    def add_font(self, font: KamaFont):
        self.__fonts[font.font_code] = font

    def add_color(self, color: KamaComposedColor):
        self.__colors[color.color_code] = color

    def add_dynamic_resource(self, resource: DynamicResource):
        self.__dynamic_resources.append(resource)

    def add_startup_task(self, startup_task: KamaStartupWorker):
        self.__startup_job.add_task(startup_task)

    @staticmethod
    def __discover_plugins():
        for plugin in entry_points(group="kama_ui.plugins"):
            plugin.load()

    def create_dynamic_resources(self):
        """
        Used to create dynamic resources.
        Mainly this applies to SVG elements
        that are just an XML files where we can
        replace colors.

        This is needed in the first place to avoid
        creating duplicate resources where the only
        difference is color.
        """

        for resource in self.__dynamic_resources:
            current_color = resource.color_code
            resolved_color = self.get_color(resource.color_code)

            if resolved_color is not None:
                current_color = resolved_color

            resource_path = self.discovery.resources(resource.resource_path, include_temporary=False)
            resource_content = read_file(resource_path)

            if current_color is not None:
                resource_content = resource_content.replace("currentColor", current_color.color_hex)

            temp_resource_path = self.discovery.temp_resources(resource.resource_name)
            save_file(temp_resource_path, resource_content)

    @staticmethod
    def __get_system_color_mode():
        """
        Used to get current color mode.
        """

        mode = ColorMode.Light
        application = QApplication.instance()

        if application is None:
            return mode

        color_scheme = application.styleHints().colorScheme()  # noqa

        if color_scheme == Qt.ColorScheme.Dark:
            mode = ColorMode.Dark

        return mode

    def __collect_startup_tasks(self):
        custom_startup_package = self.prop("application.startup-package", "")

        for member_name, member in get_members(custom_startup_package, KamaStartupWorker):
            task: KamaStartupWorker = member()
            self.__startup_job.add_task(task)
