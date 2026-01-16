from typing import Any


class ProviderDataTransformer:
    """
    Interface for transforming data structures between nested and flat formats.
    """

    def nest(self, data: Any):
        """
        Transforms flat data into a nested hierarchical structure.

        Args:
            data (Any): The flat data source to be transformed.

        Returns:
            Any: The resulting nested data structure.
        """
        pass

    def flatten(self, data: Any):
        """
        Transforms a nested hierarchical structure into a flat format.

        Args:
            data (Any): The nested data source to be transformed.

        Returns:
            Any: The resulting flat data structure.
        """
        pass
