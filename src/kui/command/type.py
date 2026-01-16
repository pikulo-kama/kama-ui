from typing import TYPE_CHECKING, Type
from kui.core.command import WidgetCommand

if TYPE_CHECKING:
    from kui.core.manager import ManagerContext
    from kui.core.component import KamaComponentMixin
    from kui.core.component import KamaLayoutMixin


class AddWidgetTypeCommand(WidgetCommand):
    """
    Command to register a batch of widget component types into the system context.

    This class implements the Command pattern to decouple the registration of
    widget definitions from the manager's internal state management.

    Attributes:
        __widget_types (list[Type[KamaComponentMixin]]): Private list of component
            classes to be registered.
    """

    def __init__(self, widget_types: list[Type["KamaComponentMixin"]]):
        """
        Initializes the command with a list of widget component classes.

        Args:
            widget_types (list[Type[KamaComponentMixin]]): The widget classes
                to be added to the context.
        """

        super().__init__()
        self.__widget_types = widget_types

    def execute(self, context: "ManagerContext"):
        """
        Executes the registration process within the provided manager context.

        Args:
            context (ManagerContext): The execution context where widget
                types are registered.
        """

        for widget_type in self.__widget_types:
            context.add_widget_type(widget_type)


class AddLayoutTypeCommand(WidgetCommand):
    """
    Command to register a batch of layout types into the system context.

    Specifically handles components that define structural positioning
    and layout logic rather than individual UI elements.

    Attributes:
        __layout_types (list[Type[KamaLayoutMixin]]): Private list of layout
            classes to be registered.
    """

    def __init__(self, layout_types: list[Type["KamaLayoutMixin"]]):
        """
        Initializes the command with a list of layout classes.

        Args:
            layout_types (list[Type[KamaLayoutMixin]]): The layout classes
                to be added to the context.
        """

        super().__init__()
        self.__layout_types = layout_types

    def execute(self, context: "ManagerContext"):
        """
        Executes the registration process within the provided manager context.

        Args:
            context (ManagerContext): The execution context where layout
                types are registered.
        """

        for layout_type in self.__layout_types:
            context.add_layout_type(layout_type)
