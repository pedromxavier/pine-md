import abc

from .base import mdType

class mdText(mdType):
    """"""

    SEP = ''

    __inline__ = True

    def __bool__(self) -> bool:
        return len(self.text) > 0

    @property
    def text(self):
        return self.SEP.join(c.html if isinstance(c, mdType) else str(c) for c in self)

    def __str__(self):
        return self.text

    def __repr__(self):
        return f"mdText({self.text!r})"

    @property
    def html(self) -> str:
        return str(self.text)

class mdBlock(mdText):

    __inline__ = False

    SEP = '\n'

    @property
    def text(self):
        return f"{self.SEP}{self.pad}".join(c.html if isinstance(c, mdType) else str(c) for c in self)


class mdPlainText(mdText):
    """"""

    @property
    def html(self) -> str:
        return str(self.text)


class mdTextTag(mdText):
    """"""

    __inline__ = True

    @abc.abstractproperty
    def tag(self) -> str:
        pass

    @property
    def html(self) -> str:
        return f"<{self.tag}{self.keys}>{self.text}</{self.tag}>"

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

class mdStrike(mdTextTag):
    @property
    def tag(self) -> str:
        return "s"

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

    @property
    def html(self) -> str:
        raise NotImplementedError('Implement me.')