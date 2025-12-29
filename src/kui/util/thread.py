from typing import TYPE_CHECKING
from PyQt6.QtCore import Qt, QThread

if TYPE_CHECKING:
    from kui.core.worker import KamaWorker


def execute_in_blocking_thread(thread: QThread, worker: "KamaWorker"):
    """
    Used to execute operation in separate thread.

    Will update UI cursor to display that operation is being performed.
    Will block GUI while performing task.
    """

    from kui.core.app import KamaApplication

    application = KamaApplication()

    if application.window.is_blocked:
        return

    def on_finish():
        application.window.setCursor(Qt.CursorShape.ArrowCursor)
        application.window.is_blocked = False

    worker.finished.connect(on_finish)  # noqa
    execute_in_thread(thread, worker)

    application.window.setCursor(Qt.CursorShape.WaitCursor)
    application.window.is_blocked = True


def execute_in_thread(thread: QThread, worker: "KamaWorker"):

    worker.moveToThread(thread)

    worker.finished.connect(thread.quit)  # noqa
    thread.finished.connect(worker.deleteLater)  # noqa
    thread.finished.connect(thread.deleteLater)  # noqa

    thread.started.connect(worker.start)  # noqa
    thread.start()
