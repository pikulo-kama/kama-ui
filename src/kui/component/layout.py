from PyQt6.QtWidgets import QVBoxLayout, QHBoxLayout, QGridLayout
from kui.core.component import KamaComponent, KamaLayoutMixin


class KamaVBoxLayout(QVBoxLayout, KamaLayoutMixin):
    """
    Custom vertical layout that arranges widgets in a top-to-bottom stack.
    """
    pass


class KamaHBoxLayout(QHBoxLayout, KamaLayoutMixin):
    """
    Custom horizontal layout that arranges widgets in a left-to-right row.
    """
    pass


class KamaGridLayout(QGridLayout, KamaLayoutMixin):
    """
    Custom grid layout that automatically manages widget placement based on
    parent metadata constraints.
    """

    def add_widget(self, widget: "KamaComponent", **kw):
        """
        Adds a widget to the grid by calculating the appropriate row and
        column index based on the current child count and the parent's
        configured column limit.

        Args:
            widget (QCustomComponent): The widget to add to the grid.
            **kw: Additional layout parameters.
        """

        parent_widget: "KamaComponent" = self.parentWidget()  # noqa
        parent_meta = parent_widget.metadata

        grid_columns = parent_meta.grid_columns
        # Order of widget starts with 1.
        # We need to make it 0 based.
        order_id = self.count()  # noqa

        # Make sure columns have equal weight
        # so that when there are fewer widgets than
        # amount of configured columns it will not fill
        # all available space.
        for column_id in range(grid_columns):
            self.setColumnStretch(column_id, 1)

        row = order_id // grid_columns
        column = order_id % grid_columns

        self.addWidget(widget, row, column, **kw)  # noqa
