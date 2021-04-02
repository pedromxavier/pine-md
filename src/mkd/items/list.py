import abc

from .base import mdType
from .tags import mdTag

# Lists
class mdList(list, mdType):
    """"""

    def __init__(self, *content: tuple):
        list.__init__(self, content)
        mdType.__init__(self)

    @abc.abstractproperty
    def tag(self) -> str:
        pass

    @property
    def html(self) -> str:
        return "\n".join(
            [
                f"<{self.tag}>{self.push}",
                *[f"{self.pad}{c.html}" for c in self],
                f"{self.pop}{self.pad}</{self.tag}>",
            ]
        )

    @property
    def child(self) -> list:
        return list(self)


class mdUList(mdList):
    """"""

    @property
    def tag(self) -> str:
        return "ul"


class mdOList(mdList):
    """"""

    @property
    def tag(self) -> str:
        return "ol"


class mdListItem(mdTag):
    """"""

    __inline__ = True

    @property
    def tag(self) -> str:
        return "li"
