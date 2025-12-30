from typing import Final


QBool: Final = lambda value: "true" if value else "false"
"""
Used to transform regular boolean value
into QSS compatible.
"""


class QAttr:
    """
    Contains names of QT properties
    used in QSS.
    """

    Id: Final = "id"
    Kind: Final = "kind"
    Disabled: Final = "is-disabled"
    Hidden: Final = "hidden"


UTF_8: Final = "utf-8"
