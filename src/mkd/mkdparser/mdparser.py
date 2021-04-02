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

from .base import Lexer, Parser, regex

class mdLexer(Lexer):

    ## List of token names.
    tokens = (
        'LINE',
        "HTML", 'HEAD', 'BODY',
        'MARKDOWN', 'INCLUDE',
        'ASSIGNMENT', 'NAME', 'STRING',
        'EQ'
    )

        ## List of token names.
    tokens = (
        'LINE',
        "HTML", 'HEAD', 'BODY',
        'MARKDOWN', 'INCLUDE',
        'ASSIGNMENT', 'NAME', 'STRING',
        'EQ'
    )

    @regex(r'\n')
    def t_LINE(self, t):
        self.lexer.lineno += 1
        return t

    @regex(r'^html$')
    def t_HTML(self, t):
        return t

    @regex(r'^head$')
    def t_HEAD(self, t):
        return t

    @regex(r'^body$')
    def t_BODY(self, t):
        return t

    @regex(r'^\§(\t|[ ]{3})[^\n]*$')
    def t_MARKDOWN(self, t):
        s = str(t.value[1:])
        if s[0] == '\t':
            t.value = s[1:]
        else:
            t.value = s[3:]
        return t

    @regex(r'^\/(\t|[ ]{3})[^\n]*$')
    def t_INCLUDE(self, t):
        s = str(t.value[1:])
        if s[0] == '\t':
            t.value = s[1:]
        else:
            t.value = s[3:]
        return t

    @regex(r'^\$(\t|[ ]{3})')
    def t_ASSIGNMENT(self, t):
        return t

    @regex(r'[a-zA-Z0-9_]+')
    def t_NAME(self, t):
        return t

    @regex(r'\"[^\"\n]*\"|\'[^\'\n]*\'')
    def t_STRING(self, t):
        t.value = str(t.value[1:-1])
        return t

    @regex(r'^\#[^\n]*$')
    def t_COMMENT(self, t):
        return None

    t_EQ = r'\='
    t_ignore = ' '

class mdParser(Parser):
    Lexer = mdLexer
    tokens = mdLexer.tokens

    def p_start(self, p):
        """start : markdown"""
        self.retrieve(p[1])

    def p_markdown(self, p):
        """markdown : """
