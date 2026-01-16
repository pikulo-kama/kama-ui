from typing import TYPE_CHECKING, Callable, Type

from kutil.reflection import get_members

from kui.command.type import AddWidgetTypeCommand, AddLayoutTypeCommand
from kui.core.component import KamaComponent, KamaComponentMixin, KamaLayout, KamaLayoutMixin
from kui.core.controller import WidgetController
from kui.command.build import WidgetBuildCommand
from kui.command.delete import WidgetDeleteCommand
from kui.command.disable import WidgetDisableCommand
from kui.command.enable import WidgetEnableCommand
from kui.command.refresh import WidgetEventRefreshCommand, WidgetRefreshCommand
from kui.core.metadata import WidgetMetadata
from kutil.logger import get_logger

if TYPE_CHECKING:
    from kui.core.window import KamaWindow
    from kui.core.app import KamaApplication
    from kui.core.command import WidgetCommand

_logger = get_logger(__name__)


WidgetFilter = Callable[[WidgetMetadata], bool]


class ManagerContext:
    """
    State container used during the execution of widget commands.

    This class acts as a bridge between the WidgetManager and Command objects,
    tracking which widgets should be added or removed during a single
    transactional update of the UI.
    """

    def __init__(self,
                 manager: "WidgetManager",
                 widgets: list[KamaComponent],
                 controllers: dict[str, WidgetController],
                 widget_types: dict[str, Type["KamaComponentMixin"]],
                 layout_types: dict[str, Type["KamaLayoutMixin"]]):
        """
        Initializes the context with current manager state.

        Args:
            manager: The parent WidgetManager instance.
            widgets: List of currently active widgets in the manager.
            controllers: Mapping of controller names to their instances.
        """

        self.__manager = manager
        self.__widgets = widgets
        self.__controllers = controllers
        self.__widget_types = widget_types
        self.__layout_types = layout_types
        self.__new_widgets = []
        self.__removed_widgets = []
        self.__new_widget_types = []
        self.__new_layout_types = []

    def get_widget_type(self, name: str):
        return self.__widget_types.get(name)

    def get_layout_type(self, name: str):
        return self.__layout_types.get(name)

    def add_widget_type(self, widget_type: Type["KamaComponentMixin"]):
        self.__new_widget_types.append(widget_type)

    def add_layout_type(self, layout_type: Type["KamaLayoutMixin"]):
        self.__new_layout_types.append(layout_type)

    def add_widget(self, widget: KamaComponent):
        """
        Registers a new widget to be built and added to the UI.

        Args:
            widget: The component instance to be added.
        """
        self.__new_widgets.append(widget)

    def remove_widget(self, widget: KamaComponent):
        """
        Schedules an existing widget for removal and cleanup.

        Args:
            widget: The component instance to be removed.
        """
        self.__removed_widgets.append(widget)

    @property
    def manager(self) -> "WidgetManager":
        """
        Returns the WidgetManager associated with this context.
        """
        return self.__manager

    @property
    def controllers(self) -> dict[str, WidgetController]:
        """
        Returns the dictionary of available widget controllers.
        """
        return self.__controllers

    @property
    def widgets(self) -> list[KamaComponent]:
        """
        Returns the list of widgets that existed when the context was created.
        """
        return self.__widgets

    @property
    def new_widgets(self) -> list[KamaComponent]:
        """
        Returns the list of widgets scheduled for addition.
        """
        return self.__new_widgets

    @property
    def removed_widgets(self) -> list[KamaComponent]:
        """
        Returns a unique list of widgets scheduled for removal.

        Uses a set internally to ensure that even if a widget was requested
        to be removed multiple times, it is only processed once.
        """
        return list(set(self.__removed_widgets))

    @property
    def new_widget_types(self) -> list[Type["KamaComponentMixin"]]:
        return self.__new_widget_types

    @property
    def new_layout_types(self) -> list[Type["KamaLayoutMixin"]]:
        return self.__new_layout_types


class WidgetManager:
    """
    Manages the lifecycle, rendering, and controller invocation for all GUI widgets.
    """

    def __init__(self, application: "KamaApplication", window: "KamaWindow"):
        """
        Initializes the manager and loads the widget controllers.

        Args:
            window: Reference to the main GUI application.
        """

        self.__application = application
        self.__window = window
        self.__widget_types: dict[str, Type["KamaComponentMixin"]] = {}
        self.__layout_types: dict[str, Type["KamaLayoutMixin"]] = {}
        self.__widgets: dict[str, KamaComponent] = {}
        self.__controllers: dict[str, WidgetController] = {}

    def execute(self, command: "WidgetCommand"):
        """
        Executes a widget command and applies the resulting additions or removals.

        Args:
            command: The command object to execute.
        """

        context = ManagerContext(
            self,
            list(self.__widgets.values()),
            self.__controllers,
            self.__widget_types,
            self.__layout_types
        )

        command.application = self.__application
        command.execute(context)

        # Add new widgets.
        self.__add_widgets(context.new_widgets)

        # Remove widgets.
        self.__remove_widgets(context.removed_widgets)

        # Add widget and layout types.
        for widget_type in context.new_widget_types:
            name = widget_type.__name__.replace("Kama", "K")
            self.__widget_types[name] = widget_type

        for layout_type in context.new_layout_types:
            name = layout_type.__name__.replace("Kama", "K")
            self.__layout_types[name] = layout_type

    def build(self, metadata: list[WidgetMetadata]):
        """
        Executes a build command for the given metadata list.

        Args:
            metadata: Metadata defining the widgets to build.
        """
        self.execute(WidgetBuildCommand(metadata))

    def build_section(self, section_id: str):
        metadata = self.__application.provider.metadata.provide(section_id)
        self.build(metadata)

    def refresh(self, widget_filter: WidgetFilter = None):
        """
        Executes a refresh command using the provided filter.

        Args:
            widget_filter: Optional filter to select widgets for refreshing.
        """
        self.__execute_with_filter(WidgetRefreshCommand, widget_filter)

    def event_refresh(self, event: str):
        """
        Executes a refresh command triggered by a specific event.

        Args:
            event: The name of the event.
        """
        self.execute(WidgetEventRefreshCommand(event))

    def enable(self, widget_filter: WidgetFilter = None):
        """
        Executes an enable command using the provided filter.

        Args:
            widget_filter: Optional filter to select widgets to enable.
        """
        self.__execute_with_filter(WidgetEnableCommand, widget_filter)

    def disable(self, widget_filter: WidgetFilter = None):
        """
        Executes a disable command using the provided filter.

        Args:
            widget_filter: Optional filter to select widgets to disable.
        """
        self.__execute_with_filter(WidgetDisableCommand, widget_filter)

    def delete(self, widget_filter: WidgetFilter = None):
        """
        Executes a delete command using the provided filter.

        Args:
            widget_filter: Optional filter to select widgets to delete.
        """
        self.__execute_with_filter(WidgetDeleteCommand, widget_filter)

    def get_widget(self, section_id: str, widget_id: str):
        """
        Retrieves a widget by its combined section and widget ID.

        Args:
            section_id: The ID of the section.
            widget_id: The ID of the widget.
        """

        widget_name = f"{section_id}.{widget_id}"
        return self.__widgets.get(widget_name)

    def invoke_controllers(self, target: str, widgets: list[KamaComponent]):
        """
        Calls a specific method on the controllers for the provided widgets.

        Args:
            target: The method name to call on the controller.
            widgets: The widgets whose controllers should be invoked.
        """

        for widget in widgets:
            controller = self.__controllers.get(widget.metadata.controller)

            if controller is None:
                continue

            method = getattr(controller, target)
            method(widget)

    def __execute_with_filter(self, command: Type, widget_filter: WidgetFilter = None):
        """
        Internal helper to execute filter-based commands.

        Args:
            command: The command class to instantiate.
            widget_filter: The filter logic to pass to the command.
        """

        if widget_filter is None:
            widget_filter = lambda meta: True

        self.execute(command(widget_filter))

    def __add_widgets(self, widgets: list[KamaComponent]):
        """
        Adds widgets to the UI hierarchy and registers them in the manager.

        Args:
            widgets: List of widgets to add.
        """

        for widget in sorted(widgets, key=lambda w: w.metadata.order_id):
            meta = widget.metadata

            if meta.parent_widget_id is None:
                parent_layout = self.__window.root.layout()
                parent_layout.addWidget(widget)

            else:
                parent = self.__widgets.get(meta.parent_widget_name)

                if parent is None:
                    parent = next((
                        widget for widget in widgets
                        if widget.metadata.name == meta.parent_widget_name
                    ), None)

                widget.metadata.parent = parent.metadata
                parent_layout: KamaLayout = parent.layout()

                _logger.debug("Adding %s as child of %s", widget.metadata.name, parent.metadata.name)
                parent_layout.add_widget(widget)

            self.__widgets[widget.metadata.name] = widget
            _logger.debug("Widget %s has been added to the manager.", widget.metadata.name)

        self.invoke_controllers("setup", widgets)

    def __remove_widgets(self, widgets: list[KamaComponent]):
        """
        Removes widgets and their children from the UI and manager registry.

        Args:
            widgets: List of widgets to remove.
        """

        def remove_widget(window_widget: KamaComponent):
            widget_name = window_widget.metadata.name

            if widget_name not in self.__widgets.keys():
                return

            del self.__widgets[window_widget.metadata.name]

            window_widget.setParent(None)
            window_widget.deleteLater()

        for widget in widgets:
            remove_widget(widget)

            for child in widget.findChildren(KamaComponentMixin):
                remove_widget(child)

    def load_components(self):

        import kui.component as core_component_package

        widget_types = []
        layout_types = []

        core_package = core_component_package.__package__
        custom_package = self.__application.config.component_package

        for member_name, member in get_members(core_package, KamaComponentMixin):
            widget_types.append(member)

        for member_name, member in get_members(core_package, KamaLayoutMixin):
            layout_types.append(member)

        for member_name, member in get_members(custom_package, KamaComponentMixin):
            widget_types.append(member)

        for member_name, member in get_members(custom_package, KamaLayoutMixin):
            layout_types.append(member)

        self.execute(AddWidgetTypeCommand(widget_types))
        self.execute(AddLayoutTypeCommand(layout_types))

    def load_controllers(self):

        import kui.controller as core_controller_package

        core_package = core_controller_package.__package__
        custom_package = self.__application.config.controller_package

        for member_name, member in get_members(core_package, WidgetController):
            controller: "WidgetController" = member(self.__application, self)
            self.__controllers[member_name] = controller

        for member_name, member in get_members(custom_package, WidgetController):
            controller: "WidgetController" = member(self.__application, self)
            self.__controllers[member_name] = controller
