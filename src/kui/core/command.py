from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from kui.core.component import KamaComponentMixin
    from kui.core.manager import ManagerContext, WidgetFilter


class WidgetCommand:
    """
    Base class for command objects that perform operations on widgets
    managed by the WidgetManager.

    This follows the Command pattern, encapsulating all information needed
    to perform an action on a set of UI components within a given context.
    """

    def execute(self, context: "ManagerContext"):  # pragma: no cover
        """
        Executes the logic associated with the command using the provided context.

        Args:
            context: The context containing the widgets and
                     state required for execution.
        """
        pass


class FilterWidgetCommand(WidgetCommand):
    """
    An extension of WidgetCommand that utilizes a filter to target specific widgets.

    This class allows for selective execution, ensuring that actions are only
    performed on widgets that meet the criteria defined in the associated filter.
    """

    def __init__(self, widget_filter: "WidgetFilter"):
        """
        Initializes the command with a specific widget filter.

        Args:
            widget_filter: A callable or filter object used to
                           validate widget metadata.
        """
        self.__widget_filter = widget_filter

    def _is_applicable(self, widget: "KamaComponentMixin"):
        """
        Checks if the provided widget matches the filter criteria.

        Args:
            widget (KamaComponentMixin): The widget to evaluate.

        Returns:
            bool: True if the widget's metadata satisfies the filter,
                  False otherwise.
        """
        return self.__widget_filter(widget.metadata)
