import os
from typing import Any

from kutil.file import read_file, save_file
from kutil.file_type import JSON


class JsonConfigHolder:
    """
    Wrapper to work with JSON configuration.
    Only allows read operations.
    """

    def __init__(self, config_path: str):
        """
        Initializes the holder by setting the path, performing setup, and loading data.

        Args:
            config_path (str): The path to the JSON configuration file.
        """

        self._config_path = JSON.add_extension(config_path)
        self._data = dict()

        self._before_file_open()

        self._load_data()

    def get_value(self, property_name, default_value=None):
        """
        Used to get property value from configuration.

        Args:
            property_name (str): The key of the property to retrieve.
            default_value (Any, optional): Fallback value if key is not found.

        Returns:
            Any: The configuration value or the default_value.
        """

        if property_name not in self._data:
            return default_value

        return self._data.get(property_name)

    def get(self):
        """
        Used to get full configuration as map.

        Returns:
            dict: The complete configuration data.
        """
        return self._data

    def _load_data(self):
        """
        Used to read configuration file
        and store contents in holder.

        Needed for testing purposes.
        """
        self._data = read_file(self._config_path, as_json=True)

    def _before_file_open(self):
        """
        To be overridden in child classes.
        Allows to perform additional operation before file opening began.
        """
        pass


class EditableJsonConfigHolder(JsonConfigHolder):
    """
    Used to operate with JSON configurations.
    Allows both read and write operations.
    """

    def set_value(self, property_name: str, value: Any):
        """
        Used to set json property in configuration.

        Args:
            property_name (str): The key to update or create.
            value (Any): The value to store.
        """

        self._data[property_name] = value
        save_file(self._config_path, self._data, as_json=True)

    def set(self, value: Any):
        """
        Used to set configuration.
        This will fully replace existing configuration.

        Args:
            value (Any): The new dictionary to replace current configuration.
        """

        self._data = value
        save_file(self._config_path, self._data, as_json=True)

    def _before_file_open(self):
        """
        Ensures the directory and the file exist before the application attempts to read them.
        """

        # Create any missing intermediate directories.
        os.makedirs(os.path.dirname(self._config_path), exist_ok=True)

        if not os.path.exists(self._config_path):
            save_file(self._config_path, {}, as_json=True)
