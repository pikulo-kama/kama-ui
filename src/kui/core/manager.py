from typing import TYPE_CHECKING, Callable, Type

from kui.core.filter import FilterBuilder
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
            manager (WidgetManager): The parent WidgetManager instance.
            widgets (list): List of currently active widgets.
            controllers (dict): Mapping of controller names to instances.
            widget_types (dict): Mapping of registered widget types.
            layout_types (dict): Mapping of registered layout types.
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
        """
        Retrieves a registered widget type by name.
        """
        return self.__widget_types.get(name)

    def get_layout_type(self, name: str):
        """
        Retrieves a registered layout type by name.
        """
        return self.__layout_types.get(name)

    def add_widget_type(self, widget_type: Type["KamaComponentMixin"]):
        """
        Schedules a new widget type for registration.
        """
        self.__new_widget_types.append(widget_type)

    def add_layout_type(self, layout_type: Type["KamaLayoutMixin"]):
        """
        Schedules a new layout type for registration.
        """
        self.__new_layout_types.append(layout_type)

    def add_widget(self, widget: KamaComponent):
        """
        Registers a new widget to be built and added to the UI.

        Args:
            widget (KamaComponent): The component instance to be added.
        """
        self.__new_widgets.append(widget)

    def remove_widget(self, widget: KamaComponent):
        """
        Schedules an existing widget for removal and cleanup.

        Args:
            widget (KamaComponent): The component instance to be removed.
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
        """
        return list(set(self.__removed_widgets))

    @property
    def new_widget_types(self) -> list[Type["KamaComponentMixin"]]:
        """
        Returns a list of newly registered widget types.
        """
        return self.__new_widget_types

    @property
    def new_layout_types(self) -> list[Type["KamaLayoutMixin"]]:
        """
        Returns a list of newly registered layout types.
        """
        return self.__new_layout_types


class WidgetManager:
    """
    Manages the lifecycle, rendering, and controller invocation for all GUI widgets.
    """

    def __init__(self, application: "KamaApplication", window: "KamaWindow"):
        """
        Initializes the manager and pre-allocates storage for types, widgets, and controllers.

        Args:
            application (KamaApplication): The global application instance.
            window (KamaWindow): Reference to the main GUI window.
        """

        self.__application = application
        self.__window = window
        self.__widget_types: dict[str, Type["KamaComponentMixin"]] = {}
        self.__layout_types: dict[str, Type["KamaLayoutMixin"]] = {}
        self.__widgets: dict[str, KamaComponent] = {}
        self.__controllers: dict[str, WidgetController] = {}

    def execute(self, command: "WidgetCommand"):
        """
        Executes a widget command and applies the resulting state changes to the UI.

        Args:
            command (WidgetCommand): The command object to execute.
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
        Instantiates and builds widgets based on the provided metadata.

        Args:
            metadata (list): Metadata defining the widgets to build.
        """
        self.execute(WidgetBuildCommand(metadata))

    def build_section(self, section_id: str):
        """
        Queries metadata for a specific section and initiates a build.

        Args:
            section_id (str): The unique identifier of the section to build.
        """

        metadata = self.__application.provider.metadata.provide(
            FilterBuilder() \
                .where("section").equals(section_id) \
                .build()
        )
        self.build(metadata)

    def refresh(self, widget_filter: WidgetFilter = None):
        """
        Triggers a refresh on widgets matching the provided filter.

        Args:
            widget_filter (WidgetFilter, optional): Logic to select widgets.
        """
        self.__execute_with_filter(WidgetRefreshCommand, widget_filter)

    def event_refresh(self, event: str):
        """
        Triggers a refresh based on a specific named event.

        Args:
            event (str): The event name triggering the refresh.
        """
        self.execute(WidgetEventRefreshCommand(event))

    def enable(self, widget_filter: WidgetFilter = None):
        """
        Enables widgets matching the filter.

        Args:
            widget_filter (WidgetFilter, optional): Selection logic.
        """
        self.__execute_with_filter(WidgetEnableCommand, widget_filter)

    def disable(self, widget_filter: WidgetFilter = None):
        """
        Disables widgets matching the filter.

        Args:
            widget_filter (WidgetFilter, optional): Selection logic.
        """
        self.__execute_with_filter(WidgetDisableCommand, widget_filter)

    def delete(self, widget_filter: WidgetFilter = None):
        """
        Deletes widgets matching the filter.

        Args:
            widget_filter (WidgetFilter, optional): Selection logic.
        """
        self.__execute_with_filter(WidgetDeleteCommand, widget_filter)

    def get_widget(self, section_id: str, widget_id: str):
        """
        Retrieves an active widget instance from the manager.

        Args:
            section_id (str): The section ID.
            widget_id (str): The widget ID.

        Returns:
            KamaComponent: The widget instance if found, otherwise None.
        """

        widget_name = f"{section_id}.{widget_id}"
        return self.__widgets.get(widget_name)

    def invoke_controllers(self, target: str, widgets: list[KamaComponent]):
        """
        Executes a named method on the controllers for a group of widgets.

        Args:
            target (str): The controller method to call (e.g., 'setup').
            widgets (list): The list of widgets to process.
        """

        for widget in widgets:
            controller = self.__controllers.get(widget.metadata.controller)

            if controller is None:
                continue

            method = getattr(controller, target)
            method(widget, widget.metadata.controller_args)

    def __execute_with_filter(self, command: Type, widget_filter: WidgetFilter = None):
        """
        Helper to execute commands that require a selection filter.
        """

        if widget_filter is None:
            widget_filter = lambda meta: True

        self.execute(command(widget_filter))

    def __add_widgets(self, widgets: list[KamaComponent]):
        """
        Handles the internal logic of parenting and registering new widgets.
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

                if parent is None:
                    _logger.warning(
                        "Can't add widget %s to manager since parent %s doesn't exist.",
                        meta.name, meta.parent_widget_name
                    )
                    continue

                widget.metadata.parent = parent.metadata
                parent_layout: KamaLayout = parent.layout()

                _logger.debug("Adding %s as child of %s", widget.metadata.name, parent.metadata.name)
                parent_layout.add_widget(widget)

            self.__widgets[widget.metadata.name] = widget
            _logger.debug("Widget %s has been added to the manager.", widget.metadata.name)

        self.invoke_controllers("setup", widgets)

    def __remove_widgets(self, widgets: list[KamaComponent]):
        """
        Handles the internal cleanup of widgets and their children.
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
        """
        Scans internal and external packages to register available widget and layout types.
        """

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
        """
        Instantiates all widget controllers found in core and custom packages.
        """

        import kui.controller as core_controller_package

        core_package = core_controller_package.__package__
        custom_package = self.__application.config.controller_package

        for member_name, member in get_members(core_package, WidgetController):
            controller: "WidgetController" = member(self.__application, self)
            self.__controllers[member_name] = controller

        for member_name, member in get_members(custom_package, WidgetController):
            controller: "WidgetController" = member(self.__application, self)
            self.__controllers[member_name] = controller
