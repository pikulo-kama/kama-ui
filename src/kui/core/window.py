import sys
from typing import Callable, TYPE_CHECKING

from PyQt6.QtCore import pyqtSignal, QSettings
from PyQt6.QtGui import QCloseEvent, QIcon
from PyQt6.QtWidgets import QMainWindow, QApplication, QHBoxLayout
from kutil.file import cleanup_directory
from kutil.logger import get_logger
from pathlib import Path

from kui.component.widget import KamaWidget
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
        """
        Initializes the window, sets up the central widget, and loads configuration.

        Args:
            context (KamaApplicationContext): The application context for service access.
        """

        self.__qt_application = QApplication(sys.argv)

        AppService.__init__(self, context)
        QMainWindow.__init__(self)

        self.__manager = WidgetManager(self.application, self)
        self.__settings = QSettings(
            self.application.config.author,
            self.application.config.name
        )

        self.__root = KamaWidget()
        self.__root.add_class("root")
        self.__root_layout = QHBoxLayout(self.__root)
        self.__root_layout.setContentsMargins(0, 0, 0, 0)
        self.setCentralWidget(self.__root)

        self.__is_ui_blocked = False
        self.__is_initialized = False

        self.setWindowTitle(self.application.config.name)
        icon_path = self.application.discovery.images(self.application.config.icon)
        self.setWindowIcon(QIcon(icon_path))

        self.resize_window()

    def exec(self):
        """
        Enters the main Qt event loop.
        """
        self.__qt_application.exec()

    @property
    def window_width(self):
        """
        Returns the default window width from configuration.

        Returns:
            int: Default width (Default: 1920).
        """
        return self.application.config.get("window.width", 1920)

    @property
    def window_height(self):
        """
        Returns the default window height from configuration.

        Returns:
            int: Default height (Default: 1080).
        """
        return self.application.config.get("window.height", 1080)

    @property
    def min_width(self):
        """
        Returns the minimum allowed window width.

        Returns:
            int: Min width (Default: 1080).
        """
        return self.application.config.get("window.min-width", 1080)

    @property
    def min_height(self):
        """
        Returns the minimum allowed window height.

        Returns:
            int: Min height (Default: 720).
        """
        return self.application.config.get("window.min-height", 720)

    @property
    def qt_application(self):
        """
        Returns the underlying QApplication instance.

        Returns:
            QApplication: The Qt application object.
        """
        return self.__qt_application

    @property
    def manager(self):
        """
        Returns the WidgetManager associated with this window.

        Returns:
            WidgetManager: The manager handling UI components.
        """
        return self.__manager

    @property
    def root(self):
        """
        Central window widget.

        Returns:
            KamaWidget: The root container widget.
        """
        return self.__root

    def show(self):
        """
        Displays the window and emits the after_init signal if not already initialized.
        """

        if not self.__is_initialized:
            _logger.info("GUI has been initialized.")
            self.after_init.emit()  # noqa
            self.__is_initialized = True

        super().show()
        _logger.info("Application loop has been started.")

    def reload_styles(self):
        """
        Combines and applies core and user stylesheets to the application.
        """

        user_stylesheet_directory = Path(self.application.discovery.Styles)
        user_stylesheet = self.application.style.builder.load_stylesheet(user_stylesheet_directory)
        user_stylesheet = "".join([f"{block.qss}\n" for block in user_stylesheet])

        self.application.style.create_dynamic_images()
        self.__qt_application.setStyleSheet(user_stylesheet)

    def build(self, section: str = "root"):
        """
        Used to build window UI from scratch
        by removing any existing UI elements.

        If target section is not provided - 'root'
        section would be built by default.

        Args:
            section (str): The section identifier to build.
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

        Args:
            event (str): The refresh event name.
        """

        _logger.info("Refreshing UI with event '%s'.", event)
        self.__manager.event_refresh(event)

    def notification(self, message: str):
        """
        Used to present notification dialog
        using provided message.

        Args:
            message (str): The text to display in the dialog.
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

        Args:
            message (str): The question to ask the user.
            callback (Callable): The function to execute on confirmation.
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

        Returns:
            bool: The blocked state.
        """
        return self.__is_ui_blocked

    @is_blocked.setter
    def is_blocked(self, is_blocked: bool):
        """
        Used to block/unblock UI.

        Args:
            is_blocked (bool): True to disable interaction, False to enable.
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
        destroyed. Persists settings and cleans directories.

        Args:
            event (QCloseEvent): The close event instance.
        """

        _logger.debug("Persisting window geometry in registry.")
        _logger.debug("width=%s, height=%s", self.width(), self.height())

        self.__settings.setValue("windowWidth", self.width())
        self.__settings.setValue("windowHeight", self.height())

        # Cleanup AppData directories.
        directories = [
            self.application.discovery.Output,
            self.application.discovery.TempImages
        ]

        for directory in directories:
            cleanup_directory(directory)

        self.before_destroy.emit()  # noqa
        _logger.info("Application shut down.")

    def resize_window(self):
        """
        Adjusts the window size based on user settings or defaults.
        """

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
