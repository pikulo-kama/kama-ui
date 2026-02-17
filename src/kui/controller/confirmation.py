from kui.component.button import KamaPushButton
from kui.component.dialog import KamaDialog
from kui.core.app import KamaApplication
from kui.core.metadata import ControllerArgs
from kui.core.shortcut import dynamic_data

from kui.controller.dialog import DialogController


class ConfirmationDialogController(DialogController):
    """
    Used to control confirmation dialog.
    Will bind configured callback to confirm button
    and will bind dialog closing to cancel button.
    """

    def setup(self, dialog: KamaDialog, args: ControllerArgs):
        """
        Initializes the confirmation dialog by blocking the main application window
        and connecting button click signals to their respective logic.

        This method retrieves the confirm and cancel buttons from the manager,
        enables them, and sets up local event handlers for handling the
        confirmation callback and dialog closure.

        Args:
            dialog (KamaDialog): The dialog instance being controlled.
            args (ControllerArgs): Metadata and arguments passed to the controller.
        """

        application = KamaApplication()

        def on_confirm():
            """
            Handles the confirm button click. Retrieves a dynamic callback,
            hides the dialog, unblocks the window, and executes the callback.
            """

            confirm_callback = dynamic_data("confirmationCallback")

            dialog.hide()
            application.window.is_blocked = False
            confirm_callback()

        def on_cancel():
            """
            Handles the cancel button click. Hides the dialog and
            unblocks the application window.
            """

            dialog.hide()
            application.window.is_blocked = False

        confirm_button: KamaPushButton = self.manager.get_widget("confirmation", args.get("confirm"))
        cancel_button: KamaPushButton = self.manager.get_widget("confirmation", args.get("cancel"))

        application.window.is_blocked = True

        if confirm_button is not None:
            confirm_button.enable()
            confirm_button.clicked.connect(on_confirm)

        if cancel_button is not None:
            cancel_button.enable()
            cancel_button.clicked.connect(on_cancel)

        super().setup(dialog, args)
