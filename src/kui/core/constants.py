import os
from typing import Final
from kutil.file import get_runtime_root


"""
Used to transform regular boolean value
into QSS compatible.
"""
QBool: Final = lambda value: "true" if value else "false"


class QAttr:
    """
    Contains names of QT properties
    used in QSS.
    """

    Id: Final = "id"
    Kind: Final = "kind"
    Disabled: Final = "is-disabled"
    Hidden: Final = "hidden"



class Directory:
    """
    Contains names of directories used by application.
    """

    @property
    def ProjectRoot(self):  # noqa
        return os.path.dirname(get_runtime_root())

    @property
    def Config(self):  # noqa
        return str(os.path.join(self.ProjectRoot, "config"))

    @property
    def Resources(self):  # noqa
        return os.path.join(self.ProjectRoot, "resources")

    @property
    def Styles(self):  # noqa
        return os.path.join(self.ProjectRoot, "styles")

    @property
    def ImportData(self):  # noqa
        return os.path.join(self.ProjectRoot, "importData")

    @property
    def Migrations(self):  # noqa
        return os.path.join(self.ProjectRoot, "migration")

    @property
    def AppDataRoot(self):  # noqa
        # We need to have fallback value for APPDATA token, since
        # when tests are executed on Linux environment it would fail.
        return os.path.join(os.getenv("APPDATA") or "", "SaveGem")

    @property
    def Output(self):  # noqa
        return os.path.join(self.AppDataRoot, "Output")

    @property
    def TempResources(self):  # noqa
        return os.path.join(self.Output, "Resources")

    @property
    def Logs(self):  # noqa
        return os.path.join(self.AppDataRoot, "Logs")

    @property
    def Logback(self):  # noqa
        return os.path.join(self.AppDataRoot, "Logback")

UTF_8: Final = "utf-8"
SHA_256: Final = "sha256"
