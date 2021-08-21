import abc
from .base import mdType


class mdTag(mdType):
    """"""

    def __bool__(self) -> bool:
        return True

    def __init__(
        self,
        *child,
        name: str = "div",
        lang: str = None,
        ID: str = None,
        CLASS: str = None,
    ):
        mdType.__init__(self, *child)
        self.name = name
        self.lang = self.add_lang(lang)
        self._keys.update({'id': ID, 'class': CLASS})

    @property
    def keys(self) -> dict:
        return {**self._keys, 'lang': self.lang}

    @property
    def html(self) -> str:
        lang = self.get_lang()
        if self.lang is None or lang is None or lang == self.lang:
            if not self.inline:
                return "\n".join(
                    [
                        f"<{self.name}{self.options}>{self.push}",
                        *[f"{self.pad}{self.html_format(c)}" for c in self],
                        f"{self.pop}{self.pad}</{self.name}>",
                    ]
                )
            else:
                return "".join(
                    [
                        f"<{self.name}{self.options}>",
                        *[f"{self.html_format(c)}" for c in self],
                        f"</{self.name}>",
                    ]
                )
        else:
            return ""

    @property
    def tex(self) -> str:
        return "\n".join(
            [
                f"\\begin{{{self.name}}}[{self.options}]{self.push}",
                *[f"{self.pad}{self.tex_format(c)}" for c in self],
                f"{self.pop}{self.pad}\\end{{{self.name}}}",
            ]
        )
