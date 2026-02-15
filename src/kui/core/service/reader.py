import xmltodict
from kui.core._service import AppService
from kui.util.file import get_files_from_directory


class ResourceReader(AppService):

    def read(self):
        self.__read_sections()

    def __read_sections(self):
        section_data = get_files_from_directory(self.application.discovery.layouts(), recursive=True, extension=".kml")
        metadata = []

        for section_xml in section_data:
            section = xmltodict.parse(section_xml)
            print(section)
