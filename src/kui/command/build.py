from typing import TYPE_CHECKING

from kui.core.component import KamaComponent
from kui.core.command import WidgetCommand
from kui.core.metadata import WidgetMetadata
from kutil.logger import get_logger

if TYPE_CHECKING:
    from kui.core.app import style
    from kui.core.manager import ManagerContext


_logger = get_logger(__name__)


class WidgetBuildCommand(WidgetCommand):
    """
    A command responsible for instantiating widgets from metadata and registering
    them within the WidgetManager's context.

    This class handles the complete lifecycle of widget construction, including
    layout configuration, content resolution, styling, and property assignment.
    """

    def __init__(self, metadata: list[WidgetMetadata]):
        """
        Initializes the build command with a list of metadata objects.
        """

        super().__init__()
        self.__metadata = metadata

    def execute(self, context: "ManagerContext"):
        """
        Iterates through the provided metadata, builds the widgets, and adds
        them to the management context.

        Args:
            context (ManagerContext): The active context where widgets are registered.
        """

        for meta in self.__metadata:
            context.add_widget(self._build_widget(meta, context))

    @staticmethod
    def _build_widget(meta: WidgetMetadata, context: "ManagerContext") -> KamaComponent:
        """
        Constructs a single QCustomComponent instance and configures its
        visual and logical state based on the metadata row.

        Args:
            meta (WidgetMetadata): Configuration data for the widget.

        Returns:
            QCustomComponent: The fully configured widget instance.
        """

        widget_type = context.get_widget_type(meta.widget_type_name)
        widget: KamaComponent = widget_type.type()

        meta.is_interactable = widget_type.is_interactable
        widget.metadata = meta

        _logger.debug("Building widget %s", widget.metadata.name)
        _logger.debug("type=%s", widget.metadata.widget_type_name)

        if meta.layout_type_name is not None:
            _logger.debug("layout=%s", meta.layout_type_name)

            layout_type = context.get_layout_type(meta.layout_type_name)
            widget.setLayout(layout_type.type())
            widget.layout().setContentsMargins(
                meta.margin_left,
                meta.margin_top,
                meta.margin_right,
                meta.margin_bottom
            )

            if meta.spacing is not None:
                widget.layout().setSpacing(meta.spacing)

        widget.apply_alignment()

        if meta.content is not None:
            _logger.debug("content=%s", meta.content)
            widget.set_content(meta.content)

        if meta.tooltip is not None:
            _logger.debug("tooltip=%s", meta.tooltip)
            widget.setToolTip(meta.tooltip)

        if meta.object_name is not None:
            _logger.debug("object_name=%s", meta.object_name)
            widget.setObjectName(meta.object_name)

        _logger.debug("Setting properties")
        for key, value in meta.properties.items():
            _logger.debug("%s=%s", key, value)
            widget.setProperty(key, value)

        if len(meta.stylesheet) > 0:
            stylesheet = style().resolve(meta.stylesheet)
            _logger.debug("stylesheet=%s", stylesheet)
            widget.setStyleSheet(stylesheet)

        if meta.width:
            _logger.debug("width=%d", meta.width)
            widget.setFixedWidth(meta.width)

        if meta.height:
            _logger.debug("height=%d", meta.height)
            widget.setFixedHeight(meta.height)

        return widget
