import abc

from cstream import stdwar, stderr

from .base import mdType
from .text import mdText
from .tags import mdTag
from .path import mdPath

# Headers
class mdHeader(mdTag):
    """"""
    __inline__ = True
    
    def __init__(self, *child, heading: int):
        mdTag.__init__(self, *child, name=f"h{heading}")


# Links & Multimedia
class mdLink(mdType):
    """"""

    def __init__(self, ref: mdPath, text: mdText):
        mdType.__init__(self)
        self.ref = ref
        self.text = text

    @property
    def html(self) -> str:
        return f'<a href="{self.ref.html}"{self.options}>{self.text.html}</a>'

    @property
    def tex(self) -> str:
        self.tex_usepackage("href")
        return f""


class mdSLink(mdLink):
    """"""

    @property
    def html(self) -> str:
        return f'<a href="{self.ref.html}" target="_blank" rel="noopener noreferrer"{self.options}>{self.text.html}</a>'


class mdLoader(mdType):
    """"""

    def __init__(self, ref: mdPath, key: str):
        mdType.__init__(self)
        self.ref = ref
        self.key = key

    def __bool__(self) -> bool:
        return True

    @property
    def html(self) -> str:
        if self.key == "js":
            return f'<script type="text/javascript" src="{self.ref.html}"></script>'
        elif self.key == "css":
            return f'<link rel="stylesheet" href="{self.ref.html}">'
        elif self.key == "img":
            return f'<img src="{self.ref.html}">'
        elif self.key == "mp":
            from ..pine import Pine
            return Pine.parse(self.ref.html, strict=False).html
        else:
            stdwar[1] << f"Invalid loader '{self.key}'."
            return str()

    @property
    def tex(self) -> str:
        if self.key == "img":
            return (
                f"""\\begin{{figure}}\n\\includegraphics{{self.ref}}\n\\end{{figure}}"""
            )
        else:
            stdwar[1] << f"Invalid loader '{self.key}'."
            return str()

class mdHref(mdType):

    __href__ = {}
    __nref__ = 0

    @classmethod
    def counter(cls) -> int:
        cls.__nref__ += 1
        return cls.__nref__

    def __new__(cls, ref: str):
        if ref not in cls.__href__:
            cls.__href__[ref] = (mdType.__new__(cls), cls.counter())
        return cls.__href__[ref][0]

    def __init__(self, ref: str):
        self.ref = ref

    @property
    def html(self) -> str:
        inner = self.html_escape(f'[{self.__href__[self.ref][1]}]')
        return f'<a href="#{self.ref}">{inner}</a>'

    @property
    def tex(self) -> str:
        raise NotImplementedError

    @classmethod
    def html_cite(cls, ref: str) -> str:
        if ref in cls.__href__:
            return f'<span id="{ref}">{cls.html_escape(f"[{cls.__href__[ref][1]}]")}</span>'
        else:
            return f'<span>{cls.html_escape(f"[?]")}</span>'

    @classmethod
    def tex_cite(cls, ref: str) -> str:
        raise NotImplementedError