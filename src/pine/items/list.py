import abc

from cstream import stderr

from .base import mdType
from .tags import mdTag

# Lists
class mdList(mdType):
    """"""

    __inline__ = False

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
