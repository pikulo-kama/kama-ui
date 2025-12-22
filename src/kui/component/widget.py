from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QWidget

from kui.core.component import KamaComponentMixin


class KamaWidget(KamaComponentMixin, QWidget):
    """
    A foundational custom widget class that integrates QWidget with CustomComponentMixin.

    This class serves as a versatile container for other components, providing
    consistent metadata handling and ensuring that custom background styles defined
    via Qt Style Sheets (QSS) are rendered correctly.
    """

    def __init__(self, *args, **kw):
        """
        Initializes the widget and its mixin, and configures attributes required
        for proper style sheet rendering.
        """

        QWidget.__init__(self, *args, **kw)
        KamaComponentMixin.__init__(self)

        # Required to properly display background-color properties
        # defined in widget style.
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
