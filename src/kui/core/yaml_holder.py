from typing import Any

import yaml


class ApplicationConfig:

    def __init__(self, config_path: str):
        self.__data = {}

        with open(config_path, "r", encoding="utf-8") as file:
            self.__data = yaml.safe_load(file)

    def get(self, property_name: str, default_value: Any = None):
        parts = property_name.split(".")
        value = self.__data.get(parts.pop(0), {})

        for property_part in parts:
            value = value.get(property_part, {})

        if value == {}:
            value = default_value

        return value
