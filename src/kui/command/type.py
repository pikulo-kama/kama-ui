from typing import TYPE_CHECKING, Type
from kui.core.command import WidgetCommand

if TYPE_CHECKING:
    from kui.core.manager import ManagerContext
    from kui.core.component import KamaComponentMixin
    from kui.core.component import KamaLayoutMixin


class AddWidgetTypeCommand(WidgetCommand):

    def __init__(self, widget_types: list[Type["KamaComponentMixin"]]):
        super().__init__()
        self.__widget_types = widget_types

    def execute(self, context: "ManagerContext"):
        for widget_type in self.__widget_types:
            context.add_widget_type(widget_type)


class AddLayoutTypeCommand(WidgetCommand):

    def __init__(self, layout_types: list[Type["KamaLayoutMixin"]]):
        super().__init__()
        self.__layout_types = layout_types

    def execute(self, context: "ManagerContext"):
        for layout_type in self.__layout_types:
            context.add_layout_type(layout_type)
