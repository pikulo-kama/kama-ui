from PyQt6.QtCore import QObject, pyqtSignal
from kutil.logger import get_logger


_logger = get_logger(__name__)


class KamaWorker(QObject):
    """
    Represents worker that
    performs single operation
    and emits events.
    """

    finished = pyqtSignal()

    def start(self):
        """
        Worker entry point.
        """

        _logger.info("Starting worker.")
        self._run()

        self.finished.emit()  # noqa
        _logger.info("Worker has finished its work.")

    def _run(self):
        """
        Should be overridden by child classes.
        Contains main worker logic.
        """
        raise NotImplementedError()
