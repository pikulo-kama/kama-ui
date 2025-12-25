import dataclasses
from enum import Enum, auto
from typing import TYPE_CHECKING
from kui.core.metadata import WidgetMetadata

if TYPE_CHECKING:
    from kui.core.controller import WidgetController


class Operand(Enum):
    EQ = auto()
    NE = auto()
    GT = auto()
    LT = auto()


@dataclasses.dataclass
class MetadataRequest:
    filter_field: str
    operand: Operand
    filter_value: str


@dataclasses.dataclass
class ControllerSectionsRequest:
    controller: "WidgetController"


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
