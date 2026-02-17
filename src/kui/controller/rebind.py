from kui.component.widget import KamaWidget
from kui.core.controller import WidgetController
from kui.core.metadata import ControllerArgs
from kutil.logger import get_logger

_logger = get_logger(__name__)


class RebindParentController(WidgetController):
    """
    Used to rebind widget to another widget.
    """

    def setup(self, widget: KamaWidget, args: ControllerArgs):
        """
        Relocates a widget from its current layout to a target widget's layout.

        This method parses a target identifier from the provided arguments,
        locates the target widget via the manager, and performs the layout
        transfer by removing the widget from its source and adding it to the
        destination layout.

        Args:
            widget (KamaWidget): The widget instance to be rebound.
            args (ControllerArgs): Arguments containing the 'parent' key.
                The 'parent' value must be a string in 'section.widget_id' format.

        Raises:
            RuntimeError: If the 'parent' argument is missing.
            ValueError: If the 'parent' string does not contain a '.' separator.
        """

        new_parent = args.get("parent")

        if new_parent is None:
            raise RuntimeError("Target rebind widget was not provided.")

        target_section_id, target_widget_id = str(new_parent).split(".")

        target_widget = self.manager.get_widget(target_section_id, target_widget_id)

        if target_widget is None:
            raise RuntimeError(f"Target widget '{new_parent}' doesn't exist.")

        target_layout = target_widget.layout()

        if target_layout is None:
            raise RuntimeError(f"Target widget '{new_parent}' doesn't have layout.")

        original_layout = widget.layout()

        _logger.debug("Rebinding '%s' to '%s'", widget.metadata.name, target_widget.metadata.name)

        original_layout.removeWidget(widget)
        target_layout.addWidget(widget)
