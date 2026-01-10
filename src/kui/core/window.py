from importlib import resources
from typing import Callable, TYPE_CHECKING

from PyQt6.QtCore import pyqtSignal, QSettings
from PyQt6.QtGui import QCloseEvent, QIcon
from PyQt6.QtWidgets import QMainWindow, QApplication, QWidget, QHBoxLayout
from kutil.logger import get_logger
from pathlib import Path
from kui.core.manager import WidgetManager
from kui.core._service import AppService

if TYPE_CHECKING:
    from kui.core.app import KamaApplicationContext

_logger = get_logger(__name__)


class KamaWindow(AppService, QMainWindow):
    """
    Main class to operate with application window.
    """

    before_destroy = pyqtSignal()
    after_init = pyqtSignal()

    def __init__(self, context: "KamaApplicationContext"):
        AppService.__init__(self, context)
        QMainWindow.__init__(self)

        self.__manager = WidgetManager(self.application, self)
        self.__settings = QSettings(
            self.application.config.author,
            self.application.config.name
        )

        self.__root = QWidget()
        self.setCentralWidget(self.__root)
        self.__root.setObjectName("root")
        self.__root_layout = QHBoxLayout(self.__root)
        self.__root_layout.setContentsMargins(0, 0, 0, 0)

        self.__is_ui_blocked = False
        self.__is_initialized = False

        self.setWindowTitle(self.application.config.name)
        icon_path = self.application.discovery.resources(self.application.config.icon)
        self.setWindowIcon(QIcon(icon_path))

        self.resize_window()

    @property
    def window_width(self):
        return self.application.config.get("window.width", 1920)

    @property
    def window_height(self):
        return self.application.config.get("window.height", 1080)

    @property
    def min_width(self):
        return self.application.config.get("window.min-width", 1080)

    @property
    def min_height(self):
        return self.application.config.get("window.min-height", 720)

    @property
    def manager(self):
        return self.__manager

    @property
    def root(self):
        """
        Central window widget.
        """
        return self.__root

    def show(self):

        if not self.__is_initialized:
            _logger.info("GUI has been initialized.")
            self.after_init.emit()  # noqa
            self.__is_initialized = True

        super().show()
        _logger.info("Application loop has been started.")

    def reload_styles(self):
        import kui.stylesheet as stylesheet_module

        stylesheet_path = resources.files(stylesheet_module)
        core_stylesheet = self.application.style.builder.load_stylesheet(stylesheet_path)
        user_stylesheet_directory = Path(self.application.discovery.Styles)
        user_stylesheet = self.application.style.builder.load_stylesheet(user_stylesheet_directory)
        stylesheet = core_stylesheet + "\n" + user_stylesheet

        self.application.style.create_dynamic_resources()
        self.application.set_stylesheet(stylesheet)

    def build(self, section: str):
        """
        Used to build window and all of its components.
        """

        _logger.info("Building UI using section '%s'.", section)

        self.reload_styles()
        self.__manager.delete()
        self.__manager.build_section(section)
        self.__manager.refresh()
        self.is_blocked = False

        self.show()

    def refresh(self, event: str):
        """
        Used to refresh dynamic UI elements.
        """

        _logger.info("Refreshing UI with event '%s'.", event)
        self.__manager.event_refresh(event)

    def notification(self, message: str):
        """
        Used to present notification dialog
        using provided message.
        """

        _logger.debug("Presenting notification dialog with message %s", message)
        self.application.data.add("dialogMessage", message)

        self.__manager.delete(lambda meta: meta.section_id == "notification")
        self.__manager.build_section("notification")

    def confirmation(self, message: str, callback: Callable):
        """
        Used to present confirmation dialog
        using provided message and confirmation
        callback.
        """

        _logger.debug("Presenting confirmation dialog with message %s", message)
        self.application.data.add("dialogMessage", message)
        self.application.data.add("confirmationCallback", callback)

        self.__manager.delete(lambda meta: meta.section_id == "confirmation")
        self.__manager.build_section("confirmation")

    @property
    def is_blocked(self):
        """
        Used to check if UI is currently blocked to any interactions.
        """
        return self.__is_ui_blocked

    @is_blocked.setter
    def is_blocked(self, is_blocked: bool):
        """
        Used to block/unblock UI.
        """

        self.__is_ui_blocked = is_blocked

        if is_blocked:
            _logger.debug("UI has been blocked.")
            self.__manager.disable()
        else:
            _logger.debug("UI has been unblocked.")
            self.__manager.enable()

    def closeEvent(self, event: QCloseEvent):
        """
        Used to call before application window
        destroyed.
        """

        _logger.debug("Persisting window geometry in registry.")
        _logger.debug("width=%s, height=%s", self.width(), self.height())

        self.__settings.setValue("windowWidth", self.width())
        self.__settings.setValue("windowHeight", self.height())

        self.before_destroy.emit()  # noqa
        _logger.info("Application shut down.")

    def resize_window(self):
        user_screen_width = self.__settings.value("windowWidth", self.window_width)
        user_screen_height = self.__settings.value("windowHeight", self.window_height)

        self.setMinimumSize(self.min_width, self.min_height)
        self.resize(user_screen_width, user_screen_height)

    def center_window(self):
        """
        Used to center application window.
        Will ensure that each time app opened it's in the center of screen.
        """

        screen_width = QApplication.primaryScreen().size().width()
        screen_height = QApplication.primaryScreen().size().height()

        user_screen_width = self.__settings.value("windowWidth", self.window_width)
        user_screen_height = self.__settings.value("windowHeight", self.window_height)

        x = int((screen_width - user_screen_width) / 2)
        y = int((screen_height - user_screen_height) / 2)

        self.move(x, y)
