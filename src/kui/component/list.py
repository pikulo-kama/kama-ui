from PyQt6.QtWidgets import QScrollArea, QFrame

from kui.core.component import KamaComponentMixin, KamaLayout
from kui.component.widget import KamaWidget
from kui.core.metadata import WidgetMetadata


class KamaScrollableWidget(KamaComponentMixin, QScrollArea):
    """
    A scrollable container widget that wraps an internal KamaWidget to provide
    scrolling capabilities for overflow content.

    This component acts as a proxy, delegating layout, metadata, and styling
    operations to its internal content widget while the QScrollArea handles
    the viewport and scrollbar logic.
    """

    def __init__(self):
        """
        Initializes the scroll area and its internal content container.
        """

        QScrollArea.__init__(self)
        KamaComponentMixin.__init__(self)

        self.setFrameShape(QFrame.Shape.NoFrame)

        self.__content = KamaWidget()
        self.__content.add_class("root")
        self.setWidget(self.__content)
        self.setWidgetResizable(True)

    def setLayout(self, layout: KamaLayout):
        """
        Sets the layout for the internal content widget.

        Args:
            layout (QCustomLayout): The layout to apply to the scrollable content.
        """
        self.__content.setLayout(layout)

    def layout(self) -> KamaLayout:
        """
        Returns the layout of the internal content widget.

        Returns:
            QCustomLayout: The layout used by the internal container.
        """
        return self.__content.layout()

    @property
    def metadata(self) -> WidgetMetadata:
        """
        Retrieves the metadata from the internal content widget.

        Returns:
            WidgetMetadata: The metadata associated with the content.
        """
        return self.__content.metadata

    @metadata.setter
    def metadata(self, metadata: WidgetMetadata):
        """
        Assigns metadata to the internal content widget.

        Args:
            metadata (WidgetMetadata): The metadata to apply.
        """
        self.__content.metadata = metadata

    def setStyleSheet(self, style_sheet: str):
        """
        Applies a CSS style sheet to the internal content widget.

        Args:
            style_sheet (str): The QSS string to apply.
        """
        self.__content.setStyleSheet(style_sheet)
