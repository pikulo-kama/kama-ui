from typing import TYPE_CHECKING, Final

from kui.component.button import KamaPushButton
from kui.component.tab_bar import KamaTabBar
from kui.core.component import KamaComponent
from kui.core.constants import QBool
from kui.core.controller import WidgetController, TemplateWidgetController, TemplateWidgetContext
from kui.core.filter import FilterBuilder
from kui.core.metadata import ControllerArgs
from kui.core.provider import Section
from kui.core.resolver import resolve_content
from kutil.logger import get_logger

if TYPE_CHECKING:
    from kui.core.app import KamaApplication
    from kui.core.manager import WidgetManager


_logger = get_logger(__name__)

CurrentSection = "current_section"
TabBarSections = "sections"


class SectionTabBarController(WidgetController):
    """
    Used to control game bar widget
    that contains tabs related to game
    management.
    """

    def __init__(self, application: "KamaApplication", manager: "WidgetManager"):
        """
        Initializes the controller with application and manager references.

        Args:
            application (KamaApplication): The main application instance.
            manager (WidgetManager): The manager responsible for widget lifecycles.
        """

        super().__init__(application, manager)
        self.__sections = []

    def setup(self, tab_bar: KamaTabBar, args: ControllerArgs):
        """
        Queries sections from the provider based on arguments and populates the tab bar.

        This method builds a filter to retrieve specific sections, stores them
        in the widget's internal state, resolves their labels, and connects
        the tab change signal.

        Args:
            tab_bar (KamaTabBar): The UI tab bar component.
            args (ControllerArgs): Arguments containing the list of 'sections' to display.
        """

        section_filter = FilterBuilder() \
            .where("section_id").among(args.get("sections", [])) \
            .build()

        sections = self.application.provider.section.provide(section_filter)
        self.state(tab_bar, TabBarSections, sections)

        for section in sections:
            section_label = resolve_content(section.section_label)
            tab_bar.addTab(section_label)

        tab_bar.currentChanged.connect(lambda index: self.__change_tab(tab_bar, index))
        self.__change_tab(tab_bar, 0)

    def refresh(self, tab_bar: KamaTabBar, args: ControllerArgs):
        """
        Updates the tab labels during a system-wide refresh.

        Args:
            tab_bar (KamaTabBar): The UI tab bar component.
            args (ControllerArgs): Arguments provided for the refresh.
        """

        for idx, section in enumerate(self.state(tab_bar, TabBarSections)):
            tab_label = resolve_content(section.section_label)
            tab_bar.setTabText(idx, tab_label)

    def __change_tab(self, tab_bar: KamaTabBar, index: int):
        """
        Used to change currently selected tab.

        Handles the transition between sections by deleting the previous
        section's widgets and building the new section's widgets.

        Args:
            tab_bar (KamaTabBar): The UI tab bar component.
            index (int): The index of the newly selected tab.
        """

        sections = self.state(tab_bar, TabBarSections)
        new_section_id = sections[index].section_id
        current_section_id = self.state(tab_bar, CurrentSection)

        if new_section_id == current_section_id:
            return

        self.state(tab_bar, CurrentSection, new_section_id)
        _logger.info("Changing tab to '%s' on '%s'", new_section_id, tab_bar.metadata.name)

        self.manager.delete(lambda meta: meta.section_id == current_section_id)
        self.manager.build_section(new_section_id)
        self.manager.refresh(lambda meta: meta.section_id == new_section_id)
        self.manager.enable()


class SectionListController(TemplateWidgetController):
    """
    Used to control application menu.
    """

    ListItemActive: Final = "active"

    def __init__(self, application: "KamaApplication", manager: "WidgetManager"):
        """
        Initializes the template-based section list controller.
        """

        super().__init__(application, manager)
        self.__sections: list[Section] = []

    def retrieve_data(self, args: ControllerArgs):
        """
        Fetches the section data that will drive the template generation.

        Args:
            args (ControllerArgs): Arguments containing the target 'sections'.

        Returns:
            list[Section]: A list of section objects.
        """

        section_filter = FilterBuilder() \
            .where("section_id").among(args.get("sections", [])) \
            .build()

        self.__sections = self.application.provider.section.provide(section_filter)
        return self.__sections

    def refresh(self, widget: KamaComponent, args: ControllerArgs):
        """
        Refreshes the section list and ensures a default tab is selected on startup.

        Args:
            widget (KamaComponent): The root component of the section list.
            args (ControllerArgs): Arguments provided for the refresh.
        """

        super().refresh(widget, args)

        if len(self.__sections) == 0:
            return

        # This will happen only once when application starts,
        # Since this would be the only time when selected section is None.
        selected_section_id = self.state(widget, CurrentSection)
        default_section_id = self.__sections[0].section_id

        if selected_section_id is None:
            self.__change_tab(widget, default_section_id)

    def handle__section_button(self, list_item: KamaPushButton, context: TemplateWidgetContext):
        """
        Used to link callback to menu item button as
        well as apply specific styles to currently selected item.

        Args:
            list_item (KamaPushButton): The button element within the template.
            context (TemplateWidgetContext): The current iteration context.
        """

        def change_tab(new_tab_id: str):
            return lambda: self.__change_tab(context.root, new_tab_id)

        section_id = context.element.section_id

        list_item.setProperty(self.ListItemActive, QBool(self.__is_selected(list_item, context.element)))
        list_item.clicked.connect(change_tab(section_id))  # noqa

    def resolve(self, context: TemplateWidgetContext, value: str, *args, **kw):
        """
        Resolves template placeholders like 'label' and 'icon'.

        Args:
            context (TemplateWidgetContext): The iteration context.
            value (str): The placeholder key to resolve.

        Returns:
            The resolved string value or None.
        """

        if value == "label":
            return context.element.section_label

        elif value == "icon":
            section_icon = context.element.section_icon

            if self.__is_selected(context.root, context.element):
                section_icon = f"active_{section_icon}"

            return section_icon

        return None

    def __is_selected(self, widget: KamaComponent, section: Section):
        """
        Used to check whether provided section is active.
        """

        selected_section_id = self.state(widget, CurrentSection)
        return selected_section_id == section.section_id

    def __change_tab(self, widget: KamaComponent, new_section_id: str):
        """
        Used to change current menu tab.

        Performs the logic of switching context: deleting the old section
        content and building the new one.

        Args:
            widget (KamaComponent): The root component.
            new_section_id (str): The ID of the section to activate.
        """

        current_section_id = self.state(widget, CurrentSection)

        if new_section_id == current_section_id:
            return

        self.state(widget, CurrentSection, new_section_id)

        _logger.info("Changing current menu item to %s", new_section_id)
        self.manager.delete(lambda meta: meta.section_id == current_section_id)
        self.manager.build_section(new_section_id)
        self.manager.refresh(lambda meta: meta.section_id == new_section_id)
        widget.refresh(refresh_children=True)
        self.manager.enable()
