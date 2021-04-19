"""
"""

from dataclasses import dataclass

from ..items import mdType, mdNull
from ..items import mdHTML, mdHead, mdBody, mdText

from .pineparser import PineParser


class PineCompiler(object):
    """"""

    HTML = 0

    @dataclass
    class Flags:
        html: int = 0
        head: int = 0
        body: int = 0
        indent: int = 0

    def __init__(self, *, mode: int = HTML):
        self.__parser = PineParser()
        self.__flags = self.Flags()
        self.__mode = mode

    def compile(self, source: str, *, ensure_html: bool = False) -> mdType:
        bytecode = self.__parser.parse(source)

        for indent, md in bytecode:
            
            if isinstance(md, mdCommand):
                if md.cmd == 'html':


            self.__flags.indent = indent