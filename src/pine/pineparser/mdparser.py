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
from ..pinelib import Source, track, trackable, TrackType

from ..items import *  # pylint: disable=unused-wildcard-import

from .base import Lexer, Parser, regex


class mdLexer(Lexer):

    ## List of token names.
    tokens = (
        "VAR",
        #       "BACK",
        "LINE",
        "WORD",
        "LBRA",
        "RBRA",
        "LPAR",
        "RPAR",
        "DASH",
        "PLUS",
        "CODE",
        "ESCAPE",
        "SPACE",
        "UNDER",
        "TILDE",
        "AST",
    )

    t_AST = r"\*"
    _BACK = r"\\"
    t_LBRA = r"\["
    t_RBRA = r"\]"
    t_LPAR = r"\("
    t_RPAR = r"\)"
    _DOLL = r"\$"
    t_CODE = r'\`'
    t_TILDE = r"\~"
    t_UNDER = r"\_"

    ESCAPE_CHAR = r"\\"

    ESCAPE_TOKENS = (
        t_AST,
        _BACK,
        t_LBRA,
        t_RBRA,
        t_LPAR,
        t_RPAR,
        t_UNDER,
        t_TILDE,
        _DOLL,
        t_CODE
    )

    RE_ESCAPE = r"|".join(
        map(lambda token, escape=ESCAPE_CHAR: f"{escape}{token}", ESCAPE_TOKENS)
    )

    @regex(r"\n")
    def t_LINE(self, t):
        self.lexer.lineno += 1
        return t

    @regex(r"\$[a-zA-Z0-9\_]+")
    def t_VAR(self, t):
        t.value = str(t.value[1:])
        return t

    @regex(r"^[^\S\r\n]*\-")
    def t_DASH(self, t):
        t.value = r'\-'
        return t

    @regex(r"^[^\S\r\n]*\+")
    def t_PLUS(self, t):
        t.value = r'\+'
        return t

    @regex(RE_ESCAPE)
    def t_ESCAPE(self, t):
        t.value = t.value[1:]
        return t

    @regex(r"[^\s\r\n\[\]\(\)\*\_\\\~]")
    def t_WORD(self, t):
        return t

    @regex(r"[^\S\r\n]")
    def t_SPACE(self, t):
        t.value = " "
        return t


class mdParser(Parser):
    Lexer = mdLexer
    tokens = mdLexer.tokens

    def p_start(self, p):
        """start : block"""
        self.retrieve(p[1])

    def p_block(self, p):
        """block : markdown_block
        | list
        """
        p[0] = p[1]

    def p_list(self, p):
        """list : ulist
        | olist
        """
        p[0] = p[1]

    def p_ulist(self, p):
        """ulist : ulist LINE ulist_item
        | ulist_item
        """
        if len(p) == 4:
            p[1].append(p[3])
            p[0] = p[1]
        else:
            p[0] = mdUList(p[1])

    def p_olist(self, p):
        """olist : olist LINE olist_item
        | olist_item
        """
        if len(p) == 4:
            p[1].append(p[3])
            p[0] = p[1]
        else:
            p[0] = mdOList(p[1])

    def p_ulist_item(self, p):
        """ulist_item : DASH markdown"""
        p[0] = mdListItem(p[2])

    def p_olist_item(self, p):
        """olist_item : PLUS markdown"""
        p[0] = mdListItem(p[2])

    def p_markdown_block(self, p):
        """markdown_block : markdown_block LINE markdown
                          | markdown
        """
        if len(p) == 4:
            p[1].append(p[3])
            p[0] = p[1]
        else:
            p[0] = mdBlock(p[1])

    def p_markdown(self, p):
        """markdown : markdown element
                    | element
        """
        if len(p) == 3:
            p[1].append(p[2])
            p[0] = p[1]
        else:
            p[0] = mdPlainText(p[1])

    def p_element(self, p):
        """element : text
                   | link
                   | effect
        """
        if len(p) == 2:
            p[0] = p[1]
        else:
            p[0] = mdNull()

    def p_effect_italic(self, p):
        """effect : UNDER text UNDER"""
        p[0] = mdItalic(p[2])

    def p_effect_bold(self, p):
        """effect : AST text AST"""
        p[0] = mdBold(p[2])

    def p_effect_strike(self, p):
        """effect : TILDE text TILDE"""
        p[0] = mdStrike(p[2])

    def p_effect_code(self, p):
        """effect : CODE text CODE"""
        p[0] = mdCode(p[2])

    def p_text(self, p):
        """text : text word
                | word
        """
        if len(p) == 3:
            p[1].append(p[2])
            p[0] = p[1]
        else:
            p[0] = mdText(p[1])

    def p_word(self, p):
        """word : WORD
        | SPACE
        | ESCAPE
        """
        p[0] = mdText(p[1])

    def p_word_var(self, p):
        """word : VAR"""
        p[0] = self.get_var(p[1])

    def p_link(self, p):
        """link : LBRA text RBRA LPAR text RPAR"""
        p[0] = mdLink(p[2], p[5])

    def p_xlink(self, p):
        """link : LBRA text RBRA AST LPAR text RPAR"""
        p[0] = mdXLink(p[2], p[6])