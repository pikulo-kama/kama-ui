from typing import Any

import yaml
from kui.util.file import resolve_app_data


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

        if isinstance(value, str):
            value = self.__resolve_tokens(value)

        return value

    @staticmethod
    def __resolve_tokens(value: str):

        app_data_token = "AppData:"

        if app_data_token in value:
            path = value.replace(app_data_token, "")
            value = resolve_app_data(path)

        return value
