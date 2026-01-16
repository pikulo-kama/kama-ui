import re
from PyQt6.QtCore import Qt
from dataclasses import dataclass
from typing import Optional, TYPE_CHECKING, Any
from kutil.logger import get_logger

if TYPE_CHECKING:
    from kui.core.resolver import ContentResolver


_logger = get_logger(__name__)
_alignment_map = {
    "left": Qt.AlignmentFlag.AlignLeft,
    "top": Qt.AlignmentFlag.AlignTop,
    "center": Qt.AlignmentFlag.AlignCenter,
    "hcenter": Qt.AlignmentFlag.AlignHCenter,
    "vcenter": Qt.AlignmentFlag.AlignVCenter,
    "right": Qt.AlignmentFlag.AlignRight,
    "bottom": Qt.AlignmentFlag.AlignBottom
}

class ControllerArgs:
    """
    Wrapper for arguments passed to a widget controller.
    """

    def __init__(self, args: dict[str, Any]):
        """
        Initializes wrapper for arguments.

        Args:
            args (dict): The raw dictionary of arguments.
        """
        self.__args = args

    def get(self, name: str, default_value: Any = None):
        """
        Retrieves a specific argument value.

        Args:
            name (str): The name of the argument.
            default_value (Any, optional): Fallback value if not found.

        Returns:
            Any: The argument value or default.
        """
        return self.__args.get(name, default_value)


@dataclass
class RefreshEventMetadata:
    """
    Holder for additional refresh event metadata, such as propagation behavior.

    Attributes:
        refresh_children (bool): Whether the event should trigger recursive updates.
    """

    refresh_children: bool


class WidgetMetadata:
    """
    A comprehensive data container representing the configuration and state of a
    UI widget as defined in the system.

    This class handles the parsing of styles, alignments, layouts, and event
    registrations, acting as the primary blueprint used by WidgetBuilders to
    instantiate and configure QCustomComponents.
    """

    def __init__(self,
                 widget_id: str,
                 section_id: str,
                 widget_type: str,
                 layout_type: str = None,
                 grid_columns: int = None,
                 parent_widget_id: str = None,
                 controller: str = None,
                 controller_args: dict[str, Any] = None,
                 order_id: int = None,
                 spacing: int = None,
                 width: int = None,
                 height: int = None,
                 margin_left: int = None,
                 margin_top: int = None,
                 margin_right: int = None,
                 margin_bottom: int = None,
                 style_object_name: str = None,
                 alignment: Qt.AlignmentFlag = Qt.AlignmentFlag(0),
                 alignment_string: str = None,
                 content: str = None,
                 tooltip: str = None,
                 stylesheet: str = "",
                 properties: dict[str, str] = None,
                 refresh_events: list[str] = None,
                 refresh_events_meta: dict[str, RefreshEventMetadata] = None):
        """
        Initializes a metadata instance with layout, style, and lifecycle parameters.
        """

        self.__id = widget_id
        self.__original_id = widget_id
        self.__section_id = section_id
        self.__parent_widget_id = parent_widget_id
        self.__parent: Optional[WidgetMetadata] = None
        self.__is_interactable = None
        self.__controller = controller
        self.__controller_args = ControllerArgs(controller_args or {})
        self.__order_id = order_id or 0

        self.__widget_type = widget_type
        self.__layout_type = layout_type

        self.__grid_columns = grid_columns
        self.__spacing = spacing
        self.__width = width
        self.__height = height
        self.__margin_left = margin_left or 0
        self.__margin_top = margin_top or 0
        self.__margin_right = margin_right or 0
        self.__margin_bottom = margin_bottom or 0
        self.__alignment = alignment or self.__parse_alignment(alignment_string)
        self.__content = content
        self.__tooltip = tooltip
        self.__stylesheet = stylesheet
        self.__properties = properties or {}
        self.__refresh_events = refresh_events or []
        self.__refresh_event_meta = refresh_events_meta or {}
        self.__resolvers: list["ContentResolver"] = []

        self.__object_name = None
        self.__parse_style_object_name(style_object_name)

        self.__refresh_events = list(set(self.__refresh_events))

    @property
    def id(self) -> str:
        """
        Retrieves the current unique ID of the widget.

        Returns:
            str: The widget identifier.
        """
        return self.__id

    @id.setter
    def id(self, widget_id: str):
        """
        Sets a new unique ID for the widget.

        Args:
            widget_id (str): The new identifier.
        """
        self.__id = widget_id

    @property
    def original_id(self):
        """
        Retrieves the original ID defined in the database, useful for
        identifying template segments.

        Returns:
            str: The original source ID.
        """
        return self.__original_id

    @property
    def name(self) -> str:
        """
        Returns a qualified name combining the section ID and widget ID.

        Returns:
            str: Format 'section.id'.
        """
        return f"{self.section_id}.{self.id}"

    @property
    def section_id(self) -> str:
        """
        Retrieves the section ID, defaulting to 'root' if none is specified.

        Returns:
            str: The section identifier.
        """
        return self.__section_id

    @property
    def parent(self) -> "WidgetMetadata":
        """
        Retrieves the parent metadata object if linked.

        Returns:
            WidgetMetadata: The parent metadata instance.
        """
        return self.__parent

    @parent.setter
    def parent(self, parent: "WidgetMetadata"):
        """
        Links a parent metadata object to this instance.

        Args:
            parent (WidgetMetadata): The metadata instance to set as parent.
        """
        self.__parent = parent

    @property
    def parent_widget_id(self) -> str:
        """
        Retrieves the ID of the parent widget container.

        Returns:
            str: The parent identifier.
        """

        if self.parent is not None:
            return self.parent.id

        return self.__parent_widget_id

    @parent_widget_id.setter
    def parent_widget_id(self, parent_widget_id: str):
        """
        Sets the ID of the parent widget container.

        Args:
            parent_widget_id (str): The parent identifier string.
        """
        self.__parent_widget_id = parent_widget_id

    @property
    def parent_widget_name(self) -> str:
        """
        Returns the qualified name of the parent widget.

        Returns:
            str: Format 'section.parent_id'.
        """

        if self.parent is not None:
            return self.parent.name

        return f"{self.section_id}.{self.parent_widget_id}"

    @property
    def is_interactable(self):
        """
        Returns whether the widget allows user interaction.

        Returns:
            bool: Interactivity state.
        """
        return self.__is_interactable

    @is_interactable.setter
    def is_interactable(self, interactable: bool):
        """
        Sets whether the widget allows user interaction.

        Args:
            interactable (bool): Target state.
        """
        self.__is_interactable = interactable

    @property
    def controller(self) -> str:
        """
        Retrieves the name of the associated controller class.

        Returns:
            str: Controller class name.
        """
        return self.__controller

    @property
    def controller_args(self) -> ControllerArgs:
        """
        Retrieves the wrapped controller arguments.

        Returns:
            ControllerArgs: The arguments instance.
        """
        return self.__controller_args

    @property
    def resolvers(self) -> dict[str, "ContentResolver"]:
        """
        Returns a mapping of resolver names to instances associated with this widget.

        Returns:
            dict: Mapped resolver instances.
        """

        resolvers = {}

        for resolver in self.__resolvers:
            resolver_name = str(resolver.__class__.__name__).lower()
            resolvers[resolver_name] = resolver

        return resolvers

    def add_resolver(self, resolver: "ContentResolver"):
        """
        Registers a new content resolver for dynamic token resolution.

        Args:
            resolver (ContentResolver): The resolver instance to add.
        """
        self.__resolvers.append(resolver)

    @property
    def order_id(self) -> int:
        """
        Retrieves the sorting order for placement within a layout.

        Returns:
            int: Sequential order index.
        """
        return self.__order_id

    @order_id.setter
    def order_id(self, order_id: int):
        """
        Sets the sorting order for layout placement.

        Args:
            order_id (int): The new order index.
        """
        self.__order_id = order_id

    @property
    def widget_type_name(self) -> str:
        """
        Retrieves the type metadata (e.g., QPushButton, QLabel).

        Returns:
            str: Widget type string.
        """
        return self.__widget_type

    @property
    def layout_type_name(self) -> str:
        """
        Retrieves the layout metadata (e.g., QVBoxLayout).

        Returns:
            str: Layout type string.
        """
        return self.__layout_type

    @property
    def grid_columns(self) -> int:
        """
        Retrieves the column count for grid layouts.

        Returns:
            int: Column count.
        """
        return self.__grid_columns

    @property
    def stylesheet(self) -> str:
        """
        Retrieves the generated QSS stylesheet string.

        Returns:
            str: Stylesheet data.
        """
        return self.__stylesheet

    @property
    def properties(self) -> dict[str, str]:
        """
        Retrieves dynamic properties used for QSS targeting.

        Returns:
            dict: Key-value property mapping.
        """
        return self.__properties

    @property
    def spacing(self) -> int:
        """
        Retrieves the internal spacing of the widget's layout.

        Returns:
            int: Spacing in pixels.
        """
        return self.__spacing

    @property
    def width(self) -> int:
        """
        Retrieves the fixed width of the widget.

        Returns:
            int: Width in pixels.
        """
        return self.__width

    @property
    def height(self) -> int:
        """
        Retrieves the fixed height of the widget.

        Returns:
            int: Height in pixels.
        """
        return self.__height

    @property
    def margin_left(self) -> int:
        """
        Retrieves the left layout margin.

        Returns:
            int: Left margin.
        """
        return self.__margin_left

    @property
    def margin_top(self) -> int:
        """
        Retrieves the top layout margin.

        Returns:
            int: Top margin.
        """
        return self.__margin_top

    @property
    def margin_right(self) -> int:
        """
        Retrieves the right layout margin.

        Returns:
            int: Right margin.
        """
        return self.__margin_right

    @property
    def margin_bottom(self) -> int:
        """
        Retrieves the bottom layout margin.

        Returns:
            int: Bottom margin.
        """
        return self.__margin_bottom

    @property
    def object_name(self) -> str:
        """
        Retrieves the Qt internal object name for QSS identification.

        Returns:
            str: Object name.
        """
        return self.__object_name

    @property
    def alignment(self) -> Qt.AlignmentFlag:
        """
        Retrieves the alignment flag for the widget's content.

        Returns:
            Qt.AlignmentFlag: The resolved Qt flag.
        """
        return self.__alignment

    @property
    def content(self) -> str:
        """
        Retrieves the raw content/text value of the widget.

        Returns:
            str: Raw content string.
        """
        return self.__content

    @property
    def tooltip(self) -> str:
        """
        Retrieves the tooltip text.

        Returns:
            str: Tooltip content.
        """
        return self.__tooltip

    @property
    def refresh_events(self) -> list[str]:
        """
        Retrieves the list of events that trigger a refresh for this widget.

        Returns:
            list: List of event strings.
        """
        return self.__refresh_events

    def should_refresh_children(self, event: str):
        """
        Checks if a specific event requires recursive child refreshing.

        Args:
            event (str): The event identifier.

        Returns:
            bool: True if children should be refreshed.
        """

        event_meta = self.__refresh_event_meta.get(event)

        if not event_meta:
            return False

        return event_meta.refresh_children

    def __parse_style_object_name(self, object_name: str):
        """
        Parses a shorthand object name string that includes dynamic properties.

        Args:
            object_name (str): Suffix following the pattern 'name[prop=val]'.
        """

        if object_name is None:
            return

        _logger.debug("Parsing composed style object name.")
        _logger.debug("raw=%s", object_name)
        match = re.compile(r"(\w+)?(\[.*?])?").match(object_name)
        style_object_name = match.group(1)
        properties_string = match.group(2)

        if style_object_name is not None:
            _logger.debug("style_object_name=%s", style_object_name)
            self.__object_name = style_object_name

        if properties_string is not None:
            properties_string = properties_string[1:-1]
            properties = properties_string.split(",")

            for prop in properties:
                name, value = prop.split("=")
                name = name.strip()
                value = value.strip()

                _logger.debug("%s=%s", name, value)
                self.__properties[name] = value

    @staticmethod
    def __parse_alignment(alignment: str) -> Qt.AlignmentFlag:
        """
        Converts a hyphen-separated alignment string into Qt AlignmentFlags.

        Args:
            alignment (str): Suffix like 'left-top'.

        Returns:
            Qt.AlignmentFlag: Bitwise 'OR' Qt flags.
        """

        alignment_prop = Qt.AlignmentFlag(0)

        if alignment is None:
            return alignment_prop

        for part in alignment.split("-"):
            alignment_prop |= _alignment_map.get(part)

        return alignment_prop
