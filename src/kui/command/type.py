from typing import TYPE_CHECKING

from kui.core.command import WidgetCommand
from kui.dto.type import WidgetType, UIObjectType

if TYPE_CHECKING:
    from kui.core.manager import ManagerContext


class AddWidgetTypeCommand(WidgetCommand):

    def __init__(self, widget_types: list[WidgetType]):
        self.__widget_types = widget_types

    def execute(self, context: "ManagerContext"):
        for widget_type in self.__widget_types:
            context.add_widget_type(widget_type)


class AddLayoutTypeCommand(WidgetCommand):

    def __init__(self, layout_types: list[UIObjectType]):
        self.__layout_types = layout_types

    def execute(self, context: "ManagerContext"):
        for layout_type in self.__layout_types:
            context.add_layout_type(layout_type)
