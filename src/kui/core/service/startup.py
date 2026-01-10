import time
from typing import Optional, TYPE_CHECKING

from PyQt6.QtCore import QThread
from kutil.logger import get_logger

from kui.core.worker import KamaWorker
from kui.util.thread import execute_in_thread
from kui.core._service import AppService

if TYPE_CHECKING:
    from kui.core.app import KamaApplicationContext


_logger = get_logger(__name__)


class StartupService(AppService):
    """
    Used to perform all word needed for application to load main screen.
    Will initiate application UI build once all workers are finished.
    """

    def __init__(self, context: "KamaApplicationContext"):
        super().__init__(context)
        self.__tasks = []

        self.__startup_threads = []
        self.__finished_tasks = []

    def add_task(self, task: "KamaStartupWorker"):
        self.__tasks.append(task)

    def start(self):
        """
        Used to start all available startup workers.
        All workers would be executed in separate threads.
        """

        if len(self.__tasks) > 0:
            self.application.window.build("wait")

        else:
            self.application.window.build("root")

        for task in self.__tasks:
            thread = QThread()

            task.link(self)
            task.finished.connect(self.__on_worker_finish(task))

            # Need to have hard reference for the thread,
            # so it won't be garbage collected.
            self.__startup_threads.append(thread)
            execute_in_thread(thread, task)

    @property
    def finished_tasks(self):
        """
        Used to get list of class names of
        tasks that have been completed.
        """
        return self.__finished_tasks

    def __on_worker_finish(self, startup_worker: "KamaStartupWorker"):
        """
        Used to get callback function that gets invoked
        each time the worker finishes its work.
        """

        def update_execution_info():
            self.__finished_tasks.append(startup_worker.name)
            _logger.debug("Startup task %s has been completed.", startup_worker.name)

            # If all tasks have been finished then initiate
            # main screen build.
            if len(self.__finished_tasks) == len(self.__tasks):
                _logger.debug("All startup tasks finished its work.")
                self.application.window.build("root")

        return update_execution_info


class KamaStartupWorker(KamaWorker):
    """
    Represents worker that is used for startup operations.
    """

    def __init__(self):
        KamaWorker.__init__(self)
        self.__job: Optional[StartupService] = None

    @property
    def name(self):
        """
        Used to get unique name of startup task.
        """
        return type(self).__name__

    def start(self):
        """
        Used to start worker.

        If worker has dependencies that haven't finished yet
        then current worker will wait until they're finished.
        """

        _logger.debug("Launching startup task %s", self.name)
        _logger.debug("dependencies=%s", self.dependencies)

        while self.__has_unfinished_dependencies():
            _logger.debug("Task has unfinished dependencies. Sleeping...")
            time.sleep(0.05)

        super().start()

    def link(self, job: StartupService):
        """
        Used to link startup worker to the
        startup job.
        """
        self.__job = job

    @property
    def dependencies(self) -> list[str]:
        """
        Used to get list of worker names
        current worker depends on.
        """
        return []

    def __has_unfinished_dependencies(self):
        """
        Used to check if all dependency workers
        finished its work.
        """

        for dependency in self.dependencies:
            if dependency not in self.__job.finished_tasks:
                return True

        return False
