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

    heading = None

    __inline__ = True

    __header__ = {}

    @classmethod
    def new(cls, heading: int):
        if heading not in cls.__header__:
            cls.__header__[heading] = type(f'mdHeader{heading}', (cls,) , {'heading': heading})
        return cls.__header__[heading]

    @property
    def tag(self):
        return f"h{self.heading}"

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

    @property
    def tex(self) -> str:
        self.tex_usepackage('href')
        return f''

class mdSLink(mdLink):
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
        elif self.key == "mp":
            return f'<OPEN "{self.ref}">'
        else:
            stdwar[0] << f"Invalid loader '{self.key}'."
            return str()

    @property
    def tex(self) -> str:
        if self.key == "img":
            return f'''\\begin{{figure}}\n\\includegraphics{{self.ref}}\n\\end{{figure}}'''
        else:
            stdwar[0] << f"Invalid loader '{self.key}'."
            return str()