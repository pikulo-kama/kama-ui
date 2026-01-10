from typing import TYPE_CHECKING

from kui.core._service import AppService
from kutil.logger import get_logger

if TYPE_CHECKING:
    from kui.core.app import KamaApplicationContext


_logger = get_logger(__name__)

class DataHolderService(AppService):
    """
    Used as intermediate storage for data
    that has been downloaded by workers.
    """

    def __init__(self, context: "KamaApplicationContext"):
        AppService.__init__(self, context)
        self.__data = {}

    def get(self, object_name: str):
        """
        Used to get data by name.
        """
        return self.__data.get(object_name)

    def add(self, object_name: str, data):
        """
        Used to add data to holder.
        """
        _logger.debug("Adding object with name %s to data holder.", object_name)
        self.__data[object_name] = data
