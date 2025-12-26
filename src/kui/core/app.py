import sys

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QApplication
from kutil.file import read_file, save_file

from kui.core.holder import DataHolder
from kui.core.json_holder import JsonConfigHolder
from kui.core.provider import MetadataProvider, ControllerSectionProvider, JsonControllerSectionProvider, \
    JsonMetadataProvider
from kui.core.startup import StartupJob, KamaStartupWorker
from kui.core.style import ColorMode, StyleBuilder
from kamatr.manager import TextResourceManager
from kui.core.window import KamaWindow
from kui.dto.style import KamaFont, KamaComposedColor
from kui.dto.type import DynamicResource
from kui.util.file import resolve_config, resolve_resource, resolve_temp_resource


def window():
    return KamaApplication().window


def tr(text_resource_key: str, *args):
    text_resources = KamaApplication().text_resources
    return text_resources.get(text_resource_key, *args)


def holder():
    return KamaApplication().data


def prop(property_name: str):
    return KamaApplication().config_property(property_name)


def style():
    return KamaApplication().style_builder


class SingletonMeta(type):
    """
    The Singleton class can be implemented in different ways in Python. Some
    possible methods include: base class, decorator, metaclass. We will use the
    metaclass because it is best suited for this purpose.
    """

    _instances = {}

    def __call__(cls, *args, **kwargs):
        """
        Possible changes to the value of the `__init__` argument do not affect
        the returned instance.
        """
        if cls not in cls._instances:
            instance = super().__call__(*args, **kwargs)
            cls._instances[cls] = instance

        return cls._instances[cls]

class KamaApplication(metaclass=SingletonMeta):

    def __init__(self):
        self.__application = QApplication(sys.argv)
        self.__config = JsonConfigHolder(resolve_config("app"))
        self.__style_builder = StyleBuilder()
        self.__startup_job = StartupJob(self)
        self.__window = KamaWindow(self)
        self.__text_resources = TextResourceManager()
        self.__data_holder = DataHolder()
        self.__dynamic_resources: list[DynamicResource] = []
        self.__color_mode = None

        self.__metadata_provider = JsonMetadataProvider()
        self.__section_provider = JsonControllerSectionProvider()

        self.__fonts: dict[str, KamaFont] = {}
        self.__colors: dict[str, KamaComposedColor] = {}

    @property
    def color_mode(self):
        if self.__color_mode is not None:
            return self.__color_mode

        return self.__get_system_color_mode()

    @color_mode.setter
    def color_mode(self, color_mode: str):
        self.__color_mode = color_mode

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

    @property
    def qt_app(self) -> QApplication:
        return self.__application

    @property
    def window(self) -> KamaWindow:
        return self.__window

    def exec(self):

        self.__startup_job.start()

        return self.__application.exec()

    def config_property(self, property_name: str):
        """
        Used to get property value from main configuration file (config/app.json)
        """

        parts = property_name.split(".")
        value = self.__config.get_value(parts.pop(0), {})

        for property_part in parts:
            value = value.get(property_part, {})

        return value

    def add_font(self, font: KamaFont):
        self.__fonts[font.font_code] = font

    def add_color(self, color: KamaComposedColor):
        self.__colors[color.color_code] = color

    def add_dynamic_resource(self, resource: DynamicResource):
        self.__dynamic_resources.append(resource)

    def add_startup_task(self, startup_task: KamaStartupWorker):
        self.__startup_job.add_task(startup_task)

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

            resource_content = read_file(resolve_resource(resource.resource_path, include_temporary=False))

            if current_color is not None:
                resource_content = resource_content.replace("currentColor", current_color)

            save_file(resolve_temp_resource(resource.resource_name), resource_content)

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
