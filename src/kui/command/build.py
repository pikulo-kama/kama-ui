from typing import TYPE_CHECKING

from kui.core.component import KamaComponent
from kui.core.command import WidgetCommand
from kui.core.metadata import WidgetMetadata
from kui.core.resolver import resolve_content
from kutil.logger import get_logger

if TYPE_CHECKING:
    from kui.core.app import KamaApplication, style
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
            context.add_widget(self._build_widget(meta))

    @staticmethod
    def _build_widget(meta: WidgetMetadata) -> KamaComponent:
        """
        Constructs a single QCustomComponent instance and configures its
        visual and logical state based on the metadata row.

        Args:
            meta (WidgetMetadata): Configuration data for the widget.

        Returns:
            QCustomComponent: The fully configured widget instance.
        """

        widget: KamaComponent = meta.widget_type.type()
        widget.metadata = meta

        _logger.debug("Building widget %s", widget.metadata.name)
        _logger.debug("type=%s", widget.metadata.widget_type.name)

        if meta.layout_type is not None:
            _logger.debug("layout=%s", meta.layout_type.name)

            widget.setLayout(meta.layout_type.type())
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
            widget.set_content(resolve_content(meta.content, extra_resolvers=meta.resolvers))

        if meta.tooltip is not None:
            _logger.debug("tooltip=%s", meta.tooltip)
            widget.setToolTip(resolve_content(meta.tooltip, extra_resolvers=meta.resolvers))

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


class WidgetSectionBuildCommand(WidgetBuildCommand):
    """
    A specialized build command that targets all widgets within a specific
    UI section by querying the database.
    """

    def __init__(self, application: "KamaApplication", section_id: str):
        """
        Initializes the command by fetching all metadata for the requested section.
        """

        metadata = application.metadata_provider.provide(section_id)
        super().__init__(metadata)
