from kui.component.dialog import KamaDialog
from kui.core.app import KamaApplication
from kui.core.controller import WidgetController
from kui.core.metadata import ControllerArgs


class DialogController(WidgetController):
    """
    Used to control dialog components.
    Will update parent by linking dialog
    directly to the main window instance.

    Will display dialog so it will appear
    on top of other components.
    """

    def setup(self, dialog: KamaDialog, args: ControllerArgs):
        """
        Configures the dialog's hierarchy and executes its display logic.

        This method establishes the main application window as the dialog's
        parent to ensure proper window layering, calculates the necessary
        dimensions for the content, and enters a modal event loop.

        Args:
            dialog (KamaDialog): The dialog widget instance to be managed.
            args (ControllerArgs): Configuration arguments and metadata
                passed to the controller.
        """

        application = KamaApplication()

        dialog.setParent(application.window)
        dialog.adjustSize()
        dialog.exec()
