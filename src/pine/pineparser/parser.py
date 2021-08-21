"""
"""
## Standard Library
import re
import sys
from pathlib import Path


## Third-Party
from ply import yacc
from cstream import Stream, stderr, stdlog

cout = Stream(fg="GREEN", file=sys.stderr)

## Local
from .lexer import Lexer
from ..error import PineError, PineSyntaxError, PineLexError
from ..pinelib import Source


class Parser(object):

    tabmodule = 'parsetab'

    TAB = '\t'

    # precedence = (
    # )

    # These lines are needed in subclasses
    _Lexer = Lexer
    tokens = Lexer.tokens

    def __init__(self, source: Source):
        self.source = source
        self.lexer = self._Lexer(self.source)
        self.parser = yacc.yacc(module=self, tabmodule=self.tabmodule)

        # --- output ---
        self.__output = None

    @classmethod
    def parse(cls, source: Source) -> object:
        parser = cls(source)
        return parser._parse()

    def _parse(self) -> object:
        try:
            self.parser.parse(str(self.source), lexer=self.lexer.lexer)
            return self.__output
        except PineError as error:
            self.__output = None
            stderr << error
        
    def retrieve(self, output: object):
        self.__output: object = output

    def syntax_error(self, msg: str, target=None, code: int = 1):
        raise PineSyntaxError(msg=msg, target=target, code=code)

    ## ------ YACC ------
    def p_error(self, p):
        if p is None:
            self.syntax_error(f"Unexpected EOF. {self.state_info()}", target=self.source.eof)
        else:
            self.syntax_error(f"{p.value!r} ({p.type}) {self.state_info()}", target=self.source.getlex(p.lexpos))

    def state_info(self) -> str:
        return f"[parser: {self.parser.state} | lexer : {self.lexer.lexer.current_state()}]"