from kui.core._service import AppService
from kui.core.provider import Section
from kui.holder.xml import XMLHolder
from kui.util.file import get_files_from_directory


class ResourceReader(AppService):

    def read(self):
        self.__read_sections()

    def __read_sections(self):

        sections = []
        section_data = get_files_from_directory(
            self.application.discovery.layouts(),
            recursive=True,
            extension=".kml"
        )

        for section_xml in section_data:
            section = XMLHolder(section_xml).root

            if section.name != "KamaSection":
                raise RuntimeError("KamaSection should be root tag of the layout.")

            if not section.has_property("name"):
                raise RuntimeError("KamaSection tag doesn't have name property.")

            sections.append(Section(
                section_id=section.get_property("name"),
                section_label=section.get_property("label"),
                section_icon=section.get_property("icon")
            ))
