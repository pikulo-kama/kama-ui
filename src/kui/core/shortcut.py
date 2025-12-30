from typing import Any
from kui.core.app import KamaApplication


def tr(text_resource_key: str, *args):
    text_resources = KamaApplication().text_resources
    return text_resources.get(text_resource_key, *args)


def dynamic_data(object_name: str):
    return KamaApplication().data.get(object_name)


def prop(property_name: str, default_value: Any = None):
    return KamaApplication().prop(property_name, default_value)
