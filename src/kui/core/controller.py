from copy import deepcopy
from dataclasses import dataclass
from typing import TYPE_CHECKING, List, Any, Final, Dict, Optional

from PyQt6.QtCore import QThread
from kui.core.component import KamaComponent, KamaComponentMixin
from kui.core.filter import FilterBuilder
from kui.util.thread import execute_in_blocking_thread
from kui.core.metadata import WidgetMetadata, ControllerArgs
from kui.core.resolver import ContentResolver
from kui.core.worker import KamaWorker
from kutil.logger import get_logger
from kutil.reflection import get_methods

if TYPE_CHECKING:
    from kui.core.app import KamaApplication
    from kui.core.manager import WidgetManager

_logger = get_logger(__name__)


class WidgetController:
    """
    Base controller class for managing widget lifecycles and business logic.

    Controllers act as the bridge between the UI components and the application logic,
    handling setup, refresh, and state management. They are persistent for the
    duration of the application.
    """

    def __init__(self, application: "KamaApplication", manager: "WidgetManager"):
        """
        Initializes the controller with references to the application and manager.

        Args:
            application (KamaApplication): The main application instance.
            manager (WidgetManager): The manager responsible for widget lifecycles.
        """

        self.__application = application
        self.__manager = manager

        self.__thread: Optional[QThread] = None
        self.__worker: Optional[KamaWorker] = None

        # Dynamic controller state.
        # Since controllers are being created
        # only once when application starts we can't
        # use instance variables to store some data.
        # Reason for that is after widget is refreshed it could be not
        # valid anymore, because of this we need to be able
        # to clear this data when refresh is happening.
        self.__state = {}

    def setup(self, widget: KamaComponent, args: ControllerArgs):  # pragma: no cover
        """
        Hook called during the initial construction of the widget.

        Args:
            widget (KamaComponent): The widget instance being initialized.
            args (ControllerArgs): Configuration arguments passed from metadata.
        """
        pass

    def refresh(self, widget: KamaComponent, args: ControllerArgs):  # pragma: no cover
        """
        Hook called whenever the widget requires a data refresh.

        Args:
            widget (KamaComponent): The widget instance to refresh.
            args (ControllerArgs): Configuration arguments passed from metadata.
        """
        pass

    def enable(self, widget: KamaComponent, args: ControllerArgs):  # pragma: no cover
        """
        Hook called when the widget is transitioned to an enabled state.

        Args:
            widget (KamaComponent): The widget instance being enabled.
            args (ControllerArgs): Configuration arguments passed from metadata.
        """
        pass

    def disable(self, widget: KamaComponent, args: ControllerArgs):  # pragma: no cover
        """
        Hook called when the widget is transitioned to a disabled state.

        Args:
            widget (KamaComponent): The widget instance being disabled.
            args (ControllerArgs): Configuration arguments passed from metadata.
        """
        pass

    @property
    def application(self):
        """
        Returns the KamaApplication instance.

        Returns:
            KamaApplication: The global application instance.
        """
        return self.__application

    @property
    def manager(self):
        """
        Returns the WidgetManager instance.

        Returns:
            WidgetManager: The manager handling the widget tree.
        """
        return self.__manager

    def reset_state(self):
        """
        Clears the dynamic state dictionary.
        """
        self.__state.clear()

    def state(self, widget: KamaComponent, key: str, value: Any = None):
        """
        Gets or sets state values associated with a specific widget instance.

        Args:
            widget (KamaComponent): The widget associated with the state.
            key (str): The state key name.
            value (Any, optional): The value to set. If None, retrieves existing value.

        Returns:
            Any: The current or newly set state value.
        """

        widget_key = f"{widget.metadata.name}.{key}"

        if value is None:
            return self.__state.get(widget_key)

        self.__state[widget_key] = value
        return value

    def work(self, worker: KamaWorker):
        """
        Executes a background worker in a separate blocking thread.

        Args:
            worker (KamaWorker): The worker instance containing the logic to execute.
        """

        self.__thread = QThread()
        self.__worker = worker

        _logger.debug(
            "Starting %s worker from controller %s",
            self.__worker.__class__.__name__,
            self.__class__.__name__
        )
        execute_in_blocking_thread(self.__thread, self.__worker)


@dataclass
class TemplateWidgetContext:
    """
    Data container for the context of a specific element within a template.

    Attributes:
        root (KamaComponent): The main container widget of the template.
        args (ControllerArgs): The controller arguments.
        element (Any): The specific data item being rendered.
    """

    root: KamaComponent
    args: ControllerArgs
    element: Any


class TemplateResolver(ContentResolver):
    """
    A specialized resolver for handling tokens within dynamic templates.

    This class delegates the actual resolution logic back to the
    TemplateWidgetController, providing context for the specific element
    being rendered.
    """

    def __init__(self, controller: "TemplateWidgetController", context: TemplateWidgetContext):
        """
        Initializes the resolver with a controller and the data element context.

        Args:
            controller (TemplateWidgetController): The parent template controller.
            context (TemplateWidgetContext): The current iteration context.
        """

        self.__controller = controller
        self.__context = context

    def resolve(self, value: str, *args, **kw):
        """
        Resolves a string value using the associated controller.

        Args:
            value (str): The token or string to resolve.

        Returns:
            Any: The resolved content.
        """
        return self.__controller.resolve(self.__context, value, *args, **kw)


class TemplateWidgetController(WidgetController):
    """
    Advanced controller for rendering dynamic repeated UI elements (lists).

    It divides a template into header, body, and footer segments, duplicating
    the body segment for every item in a provided dataset.
    """

    HandlerPrefix: Final = "handle__"

    def __init__(self, application: "KamaApplication", manager: "WidgetManager"):
        """
        Initializes the template controller and maps handler methods for dynamic widgets.

        Args:
            application (KamaApplication): The main application instance.
            manager (WidgetManager): The manager responsible for widget lifecycles.
        """

        super().__init__(application, manager)
        self.__application = application
        self.__handlers = {}

        for name, member in get_methods(self, lambda method: method.startswith(self.HandlerPrefix)):
            widget_id = name.replace(self.HandlerPrefix, "")
            self.__handlers[widget_id] = member

    def refresh(self, widget: KamaComponent, args: ControllerArgs):
        """
        Orchestrates the building of the template structure.

        Cleans up existing dynamic widgets and iterates through the dataset to
        construct the repeated body segments, applying unique IDs and
        contextual resolvers to each.

        Args:
            widget (KamaComponent): The parent widget containing the template.
            args (ControllerArgs): Controller arguments defined for current widget.
        """

        header_section = f"{widget.metadata.id}__template_header"
        body_section = f"{widget.metadata.id}__template_body"
        footer_section = f"{widget.metadata.id}__template_footer"

        header_segments = self.__segment_metadata(header_section, widget)
        body_segments = self.__segment_metadata(body_section, widget)
        footer_segments = self.__segment_metadata(footer_section, widget)

        self.manager.delete(lambda meta: meta.section_id in (header_section, body_section, footer_section))

        # Build header widgets.
        for metadata in header_segments.values():
            self.manager.build(metadata)

        for idx, element in enumerate(self.retrieve_data(args)):
            body_segments_copy = deepcopy(body_segments)

            context = TemplateWidgetContext(
                root=widget,
                args=args,
                element=element
            )

            template_resolver = TemplateResolver(self, context)

            for root_meta, metadata in body_segments_copy.items():
                widget_count = len(metadata) * len(body_segments)

                # Modify metadata so we won't have widgets with
                # the same ID.
                for widget_meta in metadata:
                    widget_meta.order_id = widget_count * idx + widget_meta.order_id
                    widget_meta.id = f"{widget_meta.original_id}__{idx}"
                    widget_meta.add_resolver(template_resolver)

                    # We need to update parent widget ID as well
                    # so that we can link widgets to correct parents.
                    # We're not setting widget_id if parent is populated,
                    # which should be populated only for root template widgets
                    # that are linked to the input widget itself.
                    if widget_meta.parent is None:
                        widget_meta.parent_widget_id = f"{widget_meta.parent_widget_id}__{idx}"

                # Build actual widgets for segment.
                self.manager.build(metadata)
                segment_root = self.manager.get_widget(body_section, f"{root_meta.original_id}__{idx}")

                self.__invoke_widget_handlers(segment_root, context)

        # Build footer.
        for metadata in footer_segments.values():
            self.manager.build(metadata)

    def soft_refresh(self, widget: KamaComponent, args: ControllerArgs):
        body_widgets = self.manager.get_widgets(f"{widget.metadata.id}__template_body")
        body_widgets = sorted(body_widgets, key=lambda widget: widget.metadata.order_id)

        for idx, element in enumerate(self.retrieve_data(args)):

            context = TemplateWidgetContext(
                root=widget,
                args=args,
                element=element
            )

            for template_widget in body_widgets:
                if not template_widget.metadata.id.endswith(f"__{idx}"):
                    continue

                template_widget.refresh()
                handler_method = self.__handlers.get(template_widget.metadata.original_id)

                if handler_method is not None:
                    handler_method(template_widget, context)

    def retrieve_data(self, args: ControllerArgs) -> list[Any]:  # noqa
        """
        Retrieves the dataset used to populate the template.

        Args:
            args (ControllerArgs): Arguments used to filter or find the data.

        Returns:
            list[Any]: A list of items to be rendered in the template body.
        """
        return []

    def resolve(self, context: TemplateWidgetContext, value: str, *args, **kw):  # noqa
        """
        Logic for resolving template-specific tokens based on the current data element.

        Args:
            context (TemplateWidgetContext): The current rendering context.
            value (str): The token to resolve.

        Returns:
            Any: The resolved value.
        """
        return value

    def __invoke_widget_handlers(self, segment_root: KamaComponent, context: TemplateWidgetContext):
        """
        Automatically calls 'handle__' methods for widgets within a generated segment.

        Args:
            segment_root (KamaComponent): The root of the newly created segment.
            context (TemplateWidgetContext): Context containing the element and root widget.
        """

        widgets: list = segment_root.findChildren(KamaComponentMixin)
        widgets.append(segment_root)

        for widget in widgets:
            handler_method = self.__handlers.get(widget.metadata.original_id)

            if handler_method is not None:
                handler_method(widget, context)

    def __segment_metadata(self, section_id: str, widget: KamaComponent) \
            -> Dict[WidgetMetadata, List[WidgetMetadata]]:
        """
        Groups metadata into logical segments based on their root ancestors.

        Args:
            section_id (str): The ID of the template section (header/body/footer).
            widget (KamaComponent): The parent widget context.

        Returns:
            Dict[WidgetMetadata, List[WidgetMetadata]]: Mapped segment roots to their children.
        """

        metadata = self.__application.provider.metadata.provide(
            FilterBuilder() \
                .where("section").equals(section_id) \
                .build()
        )
        grouped_widgets = {}

        for widget_meta in metadata:
            segment_root = self.__get_segment_root(widget_meta, metadata)
            segment_widgets = grouped_widgets.get(segment_root)

            segment_root.parent = widget.metadata

            if segment_widgets is None:
                segment_widgets = []

            segment_widgets.append(widget_meta)
            grouped_widgets[segment_root] = segment_widgets

        return grouped_widgets

    def __get_segment_root(self, target: WidgetMetadata, all_metadata: list[WidgetMetadata]) -> WidgetMetadata:
        """
        Recursively finds the top-level metadata object for a given widget metadata.

        Args:
            target (WidgetMetadata): The metadata to trace back.
            all_metadata (list[WidgetMetadata]): The pool of available metadata.

        Returns:
            WidgetMetadata: The root ancestor metadata.
        """

        for meta in all_metadata:
            if meta.id == target.parent_widget_id:
                return self.__get_segment_root(meta, all_metadata)

        return target
