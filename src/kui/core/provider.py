import dataclasses
import os.path
from typing import TYPE_CHECKING

from kui.core.metadata import WidgetMetadata
from kui.util.file import resolve_config
from kutil.file import read_file
from kutil.file_type import JSON

if TYPE_CHECKING:
    from kui.core.controller import WidgetController


@dataclasses.dataclass
class Section:
    section_id: str
    section_label: str
    section_icon: str


class MetadataProvider:
    def provide(self, section_id: str) -> list[WidgetMetadata]:
        return []


class ControllerSectionProvider:
    def provide(self, controller: "WidgetController") -> list[Section]:
        return []


class JsonMetadataProvider(MetadataProvider):

    def provide(self, section_id: str) -> list[WidgetMetadata]:

        metadata = []
        section_file_name = JSON.add_extension(section_id)
        metadata_file_path = resolve_config(os.path.join("widgets", section_file_name))

        if not os.path.exists(metadata_file_path):
            return metadata

        metadata_json = read_file(metadata_file_path, as_json=True)

        for widget in metadata_json:
            widget_meta = WidgetMetadata(**widget)
            metadata.append(widget_meta)

        return metadata


class JsonControllerSectionProvider(ControllerSectionProvider):

    def provide(self, controller: "WidgetController") -> list[Section]:

        sections = []
        config_file_name = JSON.add_extension(controller.__class__.__name__)
        section_file_path = resolve_config(os.path.join("sections", config_file_name))

        if not os.path.exists(section_file_path):
            return sections

        section_data = read_file(section_file_path, as_json=True)

        for section in section_data:
            section_meta = Section(**section)
            sections.append(section_meta)

        return sections
