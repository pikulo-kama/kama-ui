from typing import TYPE_CHECKING

from kui.component.tab_bar import KamaTabBar
from kui.core.controller import WidgetController
from kui.core.filter import FilterBuilder
from kui.core.metadata import ControllerArgs
from kui.core.resolver import resolve_content
from kutil.logger import get_logger

if TYPE_CHECKING:
    from kui.core.app import KamaApplication
    from kui.core.manager import WidgetManager


_logger = get_logger(__name__)


class TabBarController(WidgetController):
    """
    Used to control game bar widget
    that contains tabs related to game
    management.
    """

    CurrentSection = "current_section"
    TabBarSections = "sections"

    def __init__(self, application: "KamaApplication", manager: "WidgetManager"):
        super().__init__(application, manager)
        self.__sections = []

    def setup(self, tab_bar: KamaTabBar, args: ControllerArgs):

        section_filter = FilterBuilder() \
            .where("section_id").among(args.get("sections", [])) \
            .build()

        sections = self.application.provider.section.provide(section_filter)
        self.state(tab_bar, self.TabBarSections, sections)

        for section in sections:
            section_label = resolve_content(section.section_label)
            tab_bar.addTab(section_label)

        tab_bar.currentChanged.connect(lambda index: self.__change_tab(tab_bar, index))
        self.__change_tab(tab_bar, 0)

    def refresh(self, tab_bar: KamaTabBar, args: ControllerArgs):

        for idx, section in enumerate(self.state(tab_bar, self.TabBarSections)):
            tab_label = resolve_content(section.section_label)
            tab_bar.setTabText(idx, tab_label)

    def __change_tab(self, tab_bar: KamaTabBar, index: int):
        """
        Used to change currently selected tab.
        """

        sections = self.state(tab_bar, self.TabBarSections)
        new_section_id = sections[index].section_id
        current_section_id = self.state(tab_bar, self.CurrentSection)

        if new_section_id == current_section_id:
            return

        self.state(tab_bar, self.CurrentSection, new_section_id)
        _logger.info("Changing tab to '%s' on '%s'", new_section_id, tab_bar.metadata.name)

        self.manager.delete(lambda meta: meta.section_id == current_section_id)
        self.manager.build_section(new_section_id)
        self.manager.refresh(lambda meta: meta.section_id == new_section_id)
        self.manager.enable()
