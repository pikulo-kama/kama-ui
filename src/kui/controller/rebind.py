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
        new_parent = args.get("parent")

        if new_parent is None:
            raise RuntimeError("Target rebind widget was not provided.")

        target_section_id, target_widget_id = str(new_parent).split(".")

        target_widget = self.manager.get_widget(target_section_id, target_widget_id)
        target_layout = target_widget.layout()
        original_layout = widget.layout()

        _logger.debug("Rebinding '%s' to '%s'", widget.metadata.name, target_widget.metadata.name)

        original_layout.removeWidget(widget)
        target_layout.addWidget(widget)
