import dataclasses
from typing import TYPE_CHECKING
from kui.core.metadata import WidgetMetadata

if TYPE_CHECKING:
    from kui.core.controller import WidgetController


@dataclasses.dataclass
class Section:
    section_id: str
    section_label: str
    section_icon: str


class MetadataProvider:
    def provide(self, section_id: str) -> list[WidgetMetadata]:  # noqa
        return []


class ControllerSectionProvider:
    def provide(self, controller: "WidgetController") -> list[Section]:  # noqa
        return []
