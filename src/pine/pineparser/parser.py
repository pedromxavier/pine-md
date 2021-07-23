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

    TAB = '\t'

    # precedence = (
    # )

    # These lines are needed in subclasses
    _Lexer = Lexer
    tokens = Lexer.tokens

    def __init__(self, source: Source):
        self.source = source
        self.lexer = self._Lexer(self.source)
        self.parser = yacc.yacc(module=self, debug=True)

        # --- output ---
        self.__output = None

    def parse(self) -> list:
        try:
            self.parser.parse(self.source, lexer=self.lexer.lexer)
            return self.__output
        except PineError as error:
            self.__output = None
            stderr << error
        
    def retrieve(self, output: list):
        self.__output: list = output

    def syntax_error(self, msg: str, target=None, code: int = 1):
        raise PineSyntaxError(msg=msg, target=target, code=code)

    ## ------ YACC ------
    def p_error(self, p):
        target = self.source.lexchr(p.lexpos)
        if p is None:
            self.syntax_error(f"Unexpected EOF. [state:{self.parser.state}]")
        else:
            self.syntax_error(f"Problem at {p} ({p.type}) [state:{self.parser.state}]", target=target)