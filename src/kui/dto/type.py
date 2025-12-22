import dataclasses

from kutil.logger import get_logger


_logger = get_logger(__name__)


@dataclasses.dataclass
class DynamicResource:
    resource_name: str
    resource_path: str
    color_code: str


class UIObjectType:
    """
    A base container for UI-related class metadata.

    This class stores the actual Python class type and its associated
    identifier, allowing for dynamic instantiation of UI elements.
    """

    def __init__(self, widget_type_name: str, widget_class: type):
        """
        Initializes the UI object type with a name and class reference.
        """

        self.__widget_type = widget_class
        self.__widget_type_name = widget_type_name

    @property
    def type(self):
        """
        Returns the Python class reference.
        """
        return self.__widget_type

    @property
    def name(self):
        """
        Returns the identifier name of the object type.
        """
        return self.__widget_type_name


class WidgetType(UIObjectType):
    """
    Extended metadata for widget objects, including interaction state.
    """

    def __init__(self, widget_type_name: str, widget_class: type, is_interactable: bool):
        """
        Initializes the widget type with interaction metadata.
        """

        super().__init__(widget_type_name, widget_class)
        self.__is_interactable = is_interactable

    @property
    def is_interactable(self):
        """
        Checks if the widget type supports user interaction.
        """
        return self.__is_interactable
