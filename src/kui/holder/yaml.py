import os.path
from typing import Any

import yaml
from kutil.file_type import YML, YAML
from kutil.logger import get_logger


_logger = get_logger(__name__)


class YamlHolder:
    """
    A utility class for loading and accessing configuration data from YAML files.
    """

    def __init__(self, config_path: str):
        """
        Initializes the holder by locating and parsing a YAML file.

        The constructor checks for both .yaml and .yml extensions. If a file
        is found, its contents are loaded into an internal dictionary.

        Args:
            config_path (str): The base path to the configuration file (without extension).
        """

        self.__data = {}

        file_path = None
        yml_file_path = YML.add_extension(config_path)
        yaml_file_path = YAML.add_extension(config_path)

        if os.path.exists(yaml_file_path):
            file_path = yaml_file_path

        elif os.path.exists(yml_file_path):
            file_path = yml_file_path

        if file_path is None:
            _logger.error("KamaUI configuration file is missing.")
            return

        with open(file_path, "r", encoding="utf-8") as file:
            self.__data = yaml.safe_load(file)

    def get(self, property_name: str, default_value: Any = None):
        """
        Retrieves a configuration value using dot-notation.

        This method traverses the nested dictionary using a string key where
        each level is separated by a dot.

        Args:
            property_name (str): The dot-notated key (e.g., 'server.port').
            default_value (Any, optional): The value to return if the key path
                does not exist. Defaults to None.

        Returns:
            Any: The resolved value from the configuration or the default_value.
        """

        parts = property_name.split(".")
        value = self.__data.get(parts.pop(0), {})

        for property_part in parts:
            value = value.get(property_part, {})

        if value == {}:
            value = default_value

        return value
