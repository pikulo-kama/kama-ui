from typing import Callable, TYPE_CHECKING

from PyQt6.QtCore import pyqtSignal, QSettings
from PyQt6.QtGui import QCloseEvent
from PyQt6.QtWidgets import QMainWindow, QApplication, QWidget, QHBoxLayout
from kutil.logger import get_logger

from kui.command.build import WidgetSectionBuildCommand
from kui.core.constants import Directory
from kui.core.manager import WidgetManager

if TYPE_CHECKING:
    from kui.core.app import KamaApplication

_logger = get_logger(__name__)


class KamaWindow(QMainWindow):
    """
    Main class to operate with application window.
    """

    before_destroy = pyqtSignal()
    after_init = pyqtSignal()

    def __init__(self, application: "KamaApplication"):
        super().__init__()

        self.__application = application
        self.__manager = WidgetManager(self)
        self.__settings = QSettings(
            application.config.get("author"),
            application.config.get("name")
        )

        self.__root = QWidget()
        self.setCentralWidget(self.__root)
        self.__root.setObjectName("root")
        self.__root_layout = QHBoxLayout(self.__root)
        self.__root_layout.setContentsMargins(0, 0, 0, 0)

        self.__is_ui_blocked = False
        self.__is_initialized = False

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
        stylesheet = self.__application.style_builder.load_stylesheet(Directory().Styles)

        self.__application.create_dynamic_resources()
        self.__application.qt_app.setStyleSheet(stylesheet)

    def build(self, section: str):
        """
        Used to build window and all of its components.
        """

        title = self.__application.text_resources.get(
            "window_Title",
            self.__application.config.get("name", "Kama Application")
        )
        self.setWindowTitle(title)
        _logger.info("Building UI using section '%s'.", section)

        self.reload_styles()
        self.__manager.delete()
        self.__manager.execute(WidgetSectionBuildCommand(self.__application, section))
        self.__manager.refresh()
        self.is_blocked = False

        self.show()

    def refresh(self, event: str):
        """
        Used to refresh dynamic UI elements.
        """

        _logger.info("Refreshing UI with event '%s'.", event)

        self.__manager.event_refresh(event)
        title = self.__application.text_resources.get(
            "window_Title",
            self.__application.config.get("name", "Kama Application")
        )
        self.setWindowTitle(title)

    def notification(self, message: str):
        """
        Used to present notification dialog
        using provided message.
        """

        _logger.debug("Presenting notification dialog with message %s", message)
        self.__application.data.add("dialogMessage", message)
        self.__manager.execute(WidgetSectionBuildCommand(self.__application, "notification"))

    def confirmation(self, message: str, callback: Callable):
        """
        Used to present confirmation dialog
        using provided message and confirmation
        callback.
        """

        _logger.debug("Presenting confirmation dialog with message %s", message)
        self.__application.data.add("dialogMessage", message)
        self.__application.data.add("confirmationCallback", callback)
        self.__manager.execute(WidgetSectionBuildCommand(self.__application, "confirmation"))

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

    def center_window(self):
        """
        Used to center application window.
        Will ensure that each time app opened it's in the center of screen.
        """

        screen_width = QApplication.primaryScreen().size().width()
        screen_height = QApplication.primaryScreen().size().height()

        min_window_width = self.__application.config.get("minWindowWidth", 0)
        min_window_height = self.__application.config.get("minWindowHeight", 0)

        window_width = self.__application.config.get("windowWidth", 1920)
        window_height = self.__application.config.get("windowHeight", 1080)

        user_screen_width = self.__settings.value("windowWidth", window_width)
        user_screen_height = self.__settings.value("windowHeight", window_height)

        x = int((screen_width - user_screen_width) / 2)
        y = int((screen_height - user_screen_height) / 2)

        self.setMinimumSize(min_window_width, min_window_height)
        self.resize(user_screen_width, user_screen_height)
        self.move(x, y)
