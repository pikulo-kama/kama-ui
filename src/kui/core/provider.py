import dataclasses
import enum

from kui.core.controller import WidgetController
from kui.core.metadata import WidgetMetadata


@enum.Enum
class Operand:
    EQ = enum.auto()
    NE = enum.auto()
    GT = enum.auto()
    LT = enum.auto()


@dataclasses.dataclass
class MetadataRequest:
    filter_field: str
    operand: Operand
    filter_value: str


@dataclasses.dataclass
class ControllerSectionsRequest:
    controller: WidgetController


@dataclasses.dataclass
class Section:
    section_id: str
    section_label: str
    section_icon: str


class MetadataProvider:

    def provide(self, request: MetadataRequest) -> list[WidgetMetadata]:
        return []


class ControllerSectionProvider:

    def provide(self, request: ControllerSectionsRequest) -> list[Section]:
        return []
