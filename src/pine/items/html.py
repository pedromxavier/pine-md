import abc

from cstream import stdwar, stderr

from .base import mdType
from .text import mdText
from .tags import mdTag


class mdRawHTML(mdType):
    """"""

    def __init__(self, text: str):
        mdType.__init__(self)
        self.text = text

    def __bool__(self) -> bool:
        return len(self.text) > 0

    @property
    def html(self):
        return self.text

class mdHTML(mdType):
    """"""

    def __bool__(self) -> bool:
        return True

    @property
    def meta(self) -> str:
        return "<!DOCTYPE html>"

    @property
    def html(self) -> str:
        return "\n".join(
            [
                f"{self.meta}",
                f"<html{self.keys}>{self.push}",
                *[f"{self.pad}{c.html}" for c in self],
                f"{self.pop}{self.pad}</html>",
            ]
        )


class mdHead(mdTag):
    """"""

    def __bool__(self) -> bool:
        return True

    @property
    def tag(self):
        return f"head"


class mdBody(mdTag):
    """"""

    def __bool__(self) -> bool:
        return True

    @property
    def tag(self):
        return f"body"


class mdDiv(mdTag):
    """"""

    @property
    def tag(self):
        return f"div"


# Headers
class mdHeader(mdTag):
    """"""

    __inline__ = True

    @abc.abstractproperty
    def heading(self) -> int:
        pass

    @property
    def tag(self):
        return f"h{self.heading}"


class mdHeader1(mdHeader):
    """"""

    @property
    def heading(self) -> int:
        return 1


class mdHeader2(mdHeader):
    """"""

    @property
    def heading(self) -> int:
        return 2


class mdHeader3(mdHeader):
    """"""

    @property
    def heading(self) -> int:
        return 3


class mdHeader4(mdHeader):
    """"""

    @property
    def heading(self) -> int:
        return 4

# Links & Multimedia
class mdLink(mdType):
    """"""

    def __init__(self, ref: mdText, text: mdText):
        mdType.__init__(self)
        self.ref = ref
        self.text = text

    @property
    def html(self) -> str:
        return f'<a href="{self.ref.html}"{self.keys}>{self.text.html}</a>'

class mdXLink(mdLink):
    """"""

    @property
    def html(self) -> str:
        return f'<a href="{self.ref.html}" target="_blank" rel="noopener noreferrer"{self.keys}>{self.text.html}</a>'

class mdLoader(mdType):
    """"""

    def __init__(self, ref: str, key: str):
        mdType.__init__(self)
        self.ref = ref
        self.key = key

    def __bool__(self) -> bool:
        return True

    @property
    def html(self) -> str:
        if self.key == "js":
            return f'<script type="text/javascript" src="{self.ref}"></script>'
        elif self.key == "css":
            return f'<link rel="stylesheet" href="{self.ref}">'
        elif self.key == "img":
            return f'<img src="{self.ref}">'
        else:
            stdwar[0] << f"Invalid loader '{self.key}'."
            return str()