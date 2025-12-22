
import dataclasses

from kutil.logger import get_logger


_logger = get_logger(__name__)


@dataclasses.dataclass
class TextResource:
    resource_key: str
    translations: dict[str, str]


class TextResourceHolder:

    def __init__(self):
        self.__text_resources: dict[str, TextResource] = {}
        self.__current_locale = None

    @property
    def locale(self) -> str:
        return self.__current_locale

    @locale.setter
    def locale(self, locale: str):
        self.__current_locale = locale

    def add(self, text_resource: TextResource):
        self.__text_resources[text_resource.resource_key] = text_resource

    def get(self, text_resource_key: str, *args, locale: str = None):
        """
        Gets text resource by key using currently selected game.
        If text resources has placeholder and arguments have been provided then they would be resolved.
        """

        text_resource = self.__text_resources.get(text_resource_key)

        if text_resource is None:
            return text_resource_key

        if locale is None:
            locale = self.__current_locale

        label = text_resource.translations.get(locale, text_resource_key)

        _logger.debug("TextResource '%s.%s' = %s", locale, text_resource_key, label)

        if len(args) > 0:
            _logger.debug("TextResource Args = %s", args)
            label = label.format(*args)

        return label

    def remove(self, text_resource_key: str):
        if text_resource_key in self.__text_resources.keys():
            del self.__text_resources[text_resource_key]

    def remove_all(self):
        self.__text_resources = {}
