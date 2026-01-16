from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from kui.core.app import KamaApplication, KamaApplicationContext


class AppService:
    """
    Base class for all application services, providing access to the global context.
    """

    def __init__(self, context: "KamaApplicationContext"):
        """
        Initializes the service with the provided application context.
        """
        self.__context = context

    @property
    def application(self) -> "KamaApplication":
        """
        Returns the KamaApplication instance associated with the context.
        """
        return self.__context.application
