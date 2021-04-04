"""
"""
## Standard Library
import re
import itertools as it
from decimal import Decimal as Number
from pathlib import Path
from collections import deque

## Third-Party
from cstream import stderr, stdwar, stdlog, stdout
from ply import lex, yacc

## Local
from ..error import mdSyntaxError, mdError
from ..mkdlib import Source, track, trackable, TrackType

from ..items import *  # pylint: disable=unused-wildcard-import


def regex(pattern: str):
    def decor(callback):
        callback.__doc__ = pattern
        return callback

    return decor


class Lexer(object):

    tokens: tuple = ()

    RE_FLAGS = re.VERBOSE | re.UNICODE | re.MULTILINE

    def __init__(self, source):
        self.source = source

        self.lexer = lex.lex(object=self, reflags=self.RE_FLAGS, debug=False)

        # Errors
        self.error_stack = deque([])

    def __lshift__(self, error):
        self.error_stack.append(error)

    def interrupt(self):
        """"""
        while self.error_stack:
            error = self.error_stack.popleft()
            stderr[0] << error
        else:
            exit(1)

    def checkpoint(self):
        """"""
        if self.error_stack:
            self.interrupt()

    def t_error(self, t):
        stderr << f"Unknown token '{t.value}' at line {t.lineno}"
        if t:
            stderr << f"Syntax Error at line {t.lineno}:"
            stderr << self.source.lines[t.lineno - 1]
            stderr << f'{" " * (self.chrpos(t.lineno, t.lexpos))}^'
        else:
            stderr << "Unexpected End Of File."

    def chrpos(self, lineno, lexpos):
        return lexpos - self.source.table[lineno - 1] + 1


class Parser(object):

    Lexer = Lexer

    tokens: tuple = Lexer.tokens

    def __init__(self, source: Source):
        ## Input
        self.source = source

        ## Lex & Yacc
        self.lexer = self.Lexer(self.source)
        self.parser = yacc.yacc(module=self, debug=False)

        ## Indent
        self.indent = 0

        ## Look-up table
        self.symbol_table = {}

        ## Output & Errors
        self.output = None
        self.error_stack = deque([])

    def __lshift__(self, error: mdError):
        self.error_stack.append(error)

    def interrupt(self):
        """"""
        while self.error_stack:
            error = self.error_stack.popleft()
            stderr[0] << error
        else:
            exit(1)

    def checkpoint(self):
        """"""
        if self.error_stack:
            self.interrupt()

    def parse(self, ensure_html: bool = True, symbol_table: dict = None):
        ## True if main file, False if include
        self.ensure_html = ensure_html

        ## Build Symbol Table
        if symbol_table is None:
            self.symbol_table = {}
        else:
            self.symbol_table = symbol_table

        ## Run Parser
        if not self.source:
            self << mdSyntaxError("Empty File.", target=self.source.eof)
        else:
            self.parser.parse(self.source)

        ## Checkpoint
        self.checkpoint()

        ## Output
        return self.output

    def test(self):
        self.lexer.lexer.input(self.source)
        while True:
            tok = self.lexer.lexer.token()
            if not tok:
                break
            stdlog[0] << tok

    def retrieve(self, output: object):
        self.output = output

    def get_arg(self, p, index: int = None, do_track: bool = True):
        if index is None:
            value = p
            if do_track:
                value.lexinfo = {
                    "lineno": None,
                    "lexpos": None,
                    "chrpos": None,
                    "source": self.source,
                }
        else:
            value = p[index]
            if do_track:
                lineno = p.lineno(index)
                lexpos = p.lexpos(index)
                value.lexinfo = {
                    "lineno": lineno,
                    "lexpos": lexpos,
                    "chrpos": self.chrpos(lineno, lexpos),
                    "source": self.source,
                }
        return value

    def p_error(self, t):
        stderr[3] << f"Error Token: '{t}'"
        target = TrackType()
        if t:
            target.lexinfo = {
                "lineno": t.lineno,
                "lexpos": t.lexpos,
                "chrpos": self.chrpos(t.lineno, t.lexpos),
                "source": self.source,
            }
            msg = "Invalid Syntax"
        else:
            lineno = len(self.source.lines) - 1
            lexpos = len(self.source.lines[lineno]) - 1
            target.lexinfo = {
                "lineno": lineno,
                "lexpos": lexpos,
                "chrpos": self.chrpos(lineno, lexpos),
                "source": self.source,
            }
            msg = "Unexpected End Of File."
        self << mdSyntaxError(msg=msg, target=target)
        return None

    def chrpos(self, lineno: int, lexpos: int):
        return lexpos - self.source.table[lineno - 1] + 1

    def set_var(self, key: str, value: object):
        self.symbol_table[key] = value

    def get_var(self, key: str):
        if key in self.symbol_table:
            return self.symbol_table[key]
        else:
            return mdNull()

    def include(self, path: str):
        path = Path(str(path))
        if not path.exists() or not path.is_file():
            stdwar[0] << f"File '{path}' not found."
            return mdNull()
        if path.suffix == ".html":
            with open(path, mode="r") as file:
                return mdRawHTML(file.read())
        elif path.suffix == ".mkd" or path.suffix == ".md":
            subparser = self.__class__(Source(path))
            return subparser.parse(ensure_html=False, symbol_table=self.symbol_table)
        else:
            stdwar[0] << f"Unknown extension '{path.suffix}'."
            return mdNull()

