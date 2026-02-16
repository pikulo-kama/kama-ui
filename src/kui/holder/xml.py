from functools import cached_property
from typing import Any

import xmltodict


class XMLTag:

    def __init__(self, name: str):
        self.__name = name
        self.__properties = {}
        self.__children = []

    @cached_property
    def name(self):
        return self.__name

    @property
    def properties(self):
        return self.__properties

    @property
    def children(self):
        return self.__children

    @children.setter
    def children(self, children: list[XMLTag]):
        self.__children = children

    def get_property(self, name: str):
        if not self.has_property(name):
            return None

        return self.properties.get(name)

    def has_property(self, name: str):
        return name in self.__properties

    def add_property(self, name: str, value: str):
        self.__properties[name.replace("@", "")] = value

    def add_children(self, tag: XMLTag):
        self.__children.append(tag)


class XMLHolder:

    def __init__(self, content: str):
        self.__data = self.__parse_xml(xmltodict.parse(content))
        super().__init__(self.__data[0].name)

    @property
    def root(self):
        return self.__data[0]

    def __parse_xml(self, data: dict[str, Any], parent_tag: XMLTag = None) -> list[XMLTag]:
        tags = []

        for key, value in data.items():

            # Handle properties.
            if key.startswith("@") and parent_tag is not None:
                parent_tag.add_property(key, value)

            else:
                tag = XMLTag(key)
                tag.children = self.__parse_xml(value, tag)
                tags.append(tag)

        return tags
