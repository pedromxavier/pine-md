import abc

from .base import mdType


class mdTag(mdType):
    """"""

    __tags__ = {}

    def __bool__(self) -> bool:
        return True

    @classmethod
    def new(cls, tag: str) -> type:
        if tag not in cls.__tags__:
            class mdNewTag(cls):
                @property
                def tag(self):
                    return tag
            cls.__tags__[tag] = mdNewTag
        return cls.__tags__[tag]

    @abc.abstractproperty
    def tag(self):
        pass

    @property
    def html(self) -> str:
        if not self.inline:
            return "\n".join(
                [
                    f"<{self.tag}{self.keys}>{self.push}",
                    *[f"{self.pad}{c.html}" for c in self],
                    f"{self.pop}{self.pad}</{self.tag}>",
                ]
            )
        else:
            return "".join(
                [
                    f"<{self.tag}{self.keys}>",
                    *[f"{c.html}" for c in self],
                    f"</{self.tag}>",
                ]
            )
