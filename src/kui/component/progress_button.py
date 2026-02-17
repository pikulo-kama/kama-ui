from PyQt6.QtWidgets import QProgressBar

from kui.component.button import KamaPushButton


class KamaProgressPushButton(KamaPushButton):
    """
    A specialized button component that integrates a QProgressBar within its bounds.

    This component toggles between a standard push button state and an active
    progress state. When progress is initiated, the button disables user interaction
    and updates its visual property to 'in-progress', allowing for dynamic
    styling changes via Qt Style Sheets.
    """

    InProgress = "in-progress"

    def __init__(self, *args, **kw):
        """
        Initializes the progress button and creates the internal progress bar overlay.
        """

        self.__progress_bar = None

        KamaPushButton.__init__(self, *args, **kw)

        self.__progress_bar = QProgressBar(self)
        self.__progress_bar.setTextVisible(False)
        self.__progress_bar.setValue(0)

    def refresh(self, refresh_children: bool = False):
        """
        Refreshes the button state and resets the internal progress to zero.

        Args:
            refresh_children (bool): Whether to recursively refresh child components.
        """

        super().refresh(refresh_children)
        self.set_progress(0)

    def set_progress(self, progress):
        """
        Updates the progress bar value and toggles the button's interactive state.

        If progress is greater than zero, the button enters the 'in-progress'
        state, enabling the progress bar visibility and disabling the button
        to prevent duplicate actions.

        Args:
            progress (int): The progress value (0-100).
        """

        self.__progress_bar.setValue(progress)
        in_progress = progress > 0

        self.__progress_bar.setTextVisible(in_progress is True)

        if in_progress:
            self.add_class(self.InProgress)
        else:
            self.remove_class(self.InProgress)

        self.setEnabled(in_progress is False)

    def resizeEvent(self, event):
        """
        Ensures the internal progress bar always matches the button's current dimensions.

        Args:
            event (QResizeEvent): The resize event provided by Qt.
        """

        KamaPushButton.resizeEvent(self, event)
        # Update the progress bar's geometry to match the button's size
        self.__progress_bar.setGeometry(0, 0, self.width(), self.height())

    def setProperty(self, name, value):
        """
        Sets a property on the button and synchronizes specific attributes
        with the internal progress bar.

        Args:
            name (str): The name of the property.
            value (Any): The value to set.
        """

        super().setProperty(name, value)

        if self.__progress_bar is not None:
            self.__progress_bar.setProperty(f"{self.__class__.__name__}-{name}", value)
