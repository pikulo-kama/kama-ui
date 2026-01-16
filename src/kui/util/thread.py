from typing import TYPE_CHECKING
from PyQt6.QtCore import Qt, QThread

if TYPE_CHECKING:
    from kui.core.worker import KamaWorker


def execute_in_blocking_thread(thread: QThread, worker: "KamaWorker"):
    """
    Executes an operation in a separate thread while blocking the UI.

    Updates the UI cursor to a WaitCursor and sets the window's blocked state
    to True. Restores the cursor and unblocks the UI once the worker finishes.

    Args:
        thread (QThread): The thread instance to run the worker in.
        worker (KamaWorker): The worker object containing the task logic.
    """

    from kui.core.app import KamaApplication

    application = KamaApplication()

    # Prevent re-blocking if already in a blocked state
    if application.window.is_blocked:
        return

    def on_finish():
        """
        Cleanup function triggered when the worker finishes execution.
        """
        application.window.setCursor(Qt.CursorShape.ArrowCursor)
        application.window.is_blocked = False

    # Connect the finish signal before starting the thread
    worker.finished.connect(on_finish)  # noqa
    execute_in_thread(thread, worker)

    # Set UI feedback state
    application.window.setCursor(Qt.CursorShape.WaitCursor)
    application.window.is_blocked = True


def execute_in_thread(thread: QThread, worker: "KamaWorker"):
    """
    Moves a worker to a thread and manages its execution and cleanup.

    Args:
        thread (QThread): The thread instance to manage.
        worker (KamaWorker): The worker to execute.
    """

    # Move the worker logic to the target thread
    worker.moveToThread(thread)

    # Clean up thread and worker once execution completes
    worker.finished.connect(thread.quit)  # noqa
    thread.finished.connect(worker.deleteLater)  # noqa
    thread.finished.connect(thread.deleteLater)  # noqa

    # Start the worker logic when the thread begins
    thread.started.connect(worker.start)  # noqa
    thread.start()
