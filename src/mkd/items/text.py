import abc

from .base import mdType

class mdText(mdType):
    """"""

    __inline__ = True

    def __init__(self, *content: tuple):
        mdType.__init__(self)
        self.content = [c for c in content if c]

    @property
    def text(self):
        return " ".join(c.html if isinstance(c, mdType) else str(c) for c in self.content)

    def __str__(self):
        return self.text

    def __repr__(self):
        return f"mdText({self.text!r})"

    @property
    def html(self) -> str:
        return self.escape(self.text)


class mdPlainText(mdText):
    """"""

    @property
    def html(self) -> str:
        return str(self.text)


class mdTextTag(mdType):
    """"""

    __inline__ = True

    def __init__(self, text: mdText):
        mdType.__init__(self)
        self.text = text

    @abc.abstractproperty
    def tag(self) -> str:
        pass

    @property
    def html(self) -> str:
        return f"<{self.tag}{self.keys}> {self.text.html} </{self.tag}>"

# Simple Text Elements
class mdPar(mdTextTag):
    @property
    def tag(self) -> str:
        return "p"

class mdSpan(mdTextTag):
    @property
    def tag(self) -> str:
        return "span"

# Text Formatting
class mdBold(mdTextTag):
    @property
    def tag(self) -> str:
        return "b"

class mdItalic(mdTextTag):
    @property
    def tag(self) -> str:
        return "i"

class mdDeleted(mdTextTag):
    @property
    def tag(self) -> str:
        return "del"

class mdInserted(mdTextTag):
    @property
    def tag(self) -> str:
        return "ins"

class mdCode(mdTextTag):
    """"""

    @property
    def tag(self):
        return 'code'

class mdScript(mdType):
    def __init__(self, code: mdCode):
        self.code = code

    @property
    def html(self) -> str:
        return f'<script type="text/javascript"> {self.code.html} </script>'