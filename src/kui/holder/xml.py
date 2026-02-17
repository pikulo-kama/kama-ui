from functools import cached_property
from lxml import etree


class XMLTag:

    def __init__(self, name: str, parent: XMLTag):
        self.__name = name
        self.__parent = parent
        self.__content = None
        self.__properties = {}
        self.__children = []

    @cached_property
    def name(self):
        return self.__name

    @property
    def content(self):
        return self.__content

    @content.setter
    def content(self, content: str):
        self.__content = content

    @property
    def parent(self) -> XMLTag:
        return self.__parent

    @property
    def properties(self):
        return self.__properties

    @property
    def children(self) -> list[XMLTag]:
        return self.__children

    @children.setter
    def children(self, children: list[XMLTag]):
        self.__children = children

    def get(self, name: str, default_value=None):
        if not self.has(name):
            return default_value

        value = self.properties.get(name)

        if str(value).isdigit():
            value = int(value)

        return value

    def set(self, name: str, value: str):
        self.properties[name] = value

    def has(self, name: str):
        return name in self.__properties

    def add(self, name: str, value: str):
        self.__properties[name] = value

    def __str__(self):
        return self.name


class XMLHolder:

    def __init__(self, content: str):
        xml_data = etree.fromstring(content, parser=etree.XMLParser(remove_comments=True))  # noqa
        self.__root = self.__process_xml(xml_data)

    @property
    def root(self):
        return self.__root

    def __process_xml(self, element, parent_tag: XMLTag = None) -> XMLTag:
        tag = XMLTag(element.tag, parent_tag)

        if element.text and len(element.text.strip()) > 0:
            tag.content = element.text.strip()

        # Handle properties.
        for key, value in element.items():
            tag.add(key, value)

        tag.children = [self.__process_xml(child, tag) for child in element]
        return tag
