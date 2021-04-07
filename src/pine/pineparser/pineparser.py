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


class pineLexer(Lexer):

    tokens = (
        "LINE",
        "INDENT",
        "HTML",
        "HEAD",
        "BODY",
        "PINE_INCLUDE",
        "PINE_VAR",
        "ULIST_INDENT",
        "OLIST_INDENT",
        "DIVPUSH_INDENT",
        "DIVPOP_INDENT",
        "AT",
        "AST",
        "DOT",
        "DASH",
        "PLUS",
        "TICK",
        "DOLL",
        "HASH",
        "EQUAL",
        "UNDER",
        "TILDE",
        "QUOTE",
        "NAME",
        "WORD",
        "SPACE",
        "STRING",
        "ESCAPE",
        "LPAR",
        "RPAR",
        "LBRA",
        "RBRA",
        "LCUR",
        "RCUR",
    )
    # New Line Character '\n'
    @regex(r"\n+")
    def t_LINE(self, t):
        self.lexer.lineno += len(t.value)
        return t

    @regex(r"^\#[^\r\n]*$")
    def t_COMMENT(self, t):
        return None

    # List Indent
    @regex(r"^(\t|\ {4})[^\S\r\n]*\-")
    def t_ULIST_INDENT(self, t):
        return t

    @regex(r"^(\t|\ {4})[^\S\r\n]*\+")
    def t_OLIST_INDENT(self, t):
        return t

    @regex(r"^(\t|\ {4})[^\S\r\n]*\{")
    def t_DIVPUSH_INDENT(self, t):
        return t

    @regex(r"^(\t|\ {4})[^\S\r\n]*\}")
    def t_DIVPOP_INDENT(self, t):
        return t

    # Indent
    @regex(r"^(\t|\ {4})[^\S\r\n]*")
    def t_INDENT(self, t):
        return t

    # Special HTML tags
    @regex(r"^html[^\S\r\n]*$")
    def t_HTML(self, t):
        return t

    @regex(r"^head[^\S\r\n]*$")
    def t_HEAD(self, t):
        return t

    @regex(r"^body[^\S\r\n]*$")
    def t_BODY(self, t):
        return t

    # Pinecode
    @regex(r"^\/")
    def t_PINE_INCLUDE(self, t):
        return t

    @regex(r"^\$")
    def t_PINE_VAR(self, t):
        return t

    # Symbols
    t_AT = r"\@"
    t_AST = r"\*"
    t_DOT = r"\."
    t_HASH = r"\#"
    t_DASH = r"\-"
    t_PLUS = r"\+"
    t_TICK = r"\`"
    t_DOLL = r"\$"
    t_EQUAL = r"\="
    t_UNDER = r"\_"
    t_TILDE = r"\~"
    t_QUOTE = r"\""

    # Delimiters
    t_LPAR = r"\("
    t_RPAR = r"\)"
    t_LBRA = r"\["
    t_RBRA = r"\]"
    t_LCUR = r"\{"
    t_RCUR = r"\}"

    ESCAPE = (
        t_AT,
        t_AST,
        t_DASH,
        t_PLUS,
        t_TICK,
        t_UNDER,
        t_EQUAL,
        t_TILDE,
        t_LPAR,
        t_RPAR,
        t_LBRA,
        t_RBRA,
        t_LCUR,
        t_RCUR,
        t_DOLL,
        t_HASH,
        t_QUOTE,
        t_DOT,
    )
    ESCAPE_CHAR = r"\\"

    RE_ESCAPE = r"|".join(map(lambda c, e=ESCAPE_CHAR: f"{e}{c}", ESCAPE))

    # Names and Words
    @regex(r"\"[^\"\r\n]*\"|\'[^\'\r\n]*\'")
    def t_STRING(self, t):
        return t

    @regex(r"\b[a-zA-Z][a-zA-Z0-9\-]*\b")
    def t_NAME(self, t):
        return t

    t_WORD = r"[^\s\r\n%s]+" % "".join(ESCAPE)

    @regex(r"[\t ]+")
    def t_SPACE(self, t):
        t.value = r" "
        return t

    @regex(RE_ESCAPE)
    def t_ESCAPE(self, t):
        t.value = str(t.value[1:])
        return t


class pineParser(Parser):

    Lexer = pineLexer
    tokens = pineLexer.tokens

    def __init__(self, source: Source):
        Parser.__init__(self, source)

    def p_start(self, p):
        """start : file"""
        self.retrieve(p[1])

    def p_file(self, p):
        """file : html
                | head body
                | head
                | body
                | code
        """
        if len(p) == 3:
            if self.ensure_html:
                p[0] = mdHTML(p[1], p[2])
            else:
                p[0] = mdContents(p[1], p[2])
        elif len(p) == 2:
            if isinstance(p[1], mdHTML):
                p[0] = p[1]
            elif isinstance(p[1], (mdHead, mdBody)):
                if self.ensure_html:
                    p[0] = mdHTML(p[1])
                else:
                    p[0] = p[1]
            else:
                if self.ensure_html:
                    p[0] = mdHTML(*p[1])
                else:
                    p[0] = mdContents(*p[1])

    def p_html_block(self, p):
        """html : HTML LINE code head body
                | HTML LINE code head
                | HTML LINE code
        """
        if len(p) == 6:
            p[0] = mdHTML(*p[3], p[4], p[5])
        elif len(p) == 5:
            p[0] = mdHTML(*p[3], p[4])
        elif len(p) == 4:
            p[0] = mdHTML(*p[3])

    def p_html(self, p):
        """html : HTML LINE head body
                | HTML LINE head
                | HTML LINE body
        """
        if len(p) == 5:
            p[0] = mdHTML(p[3], p[4])
        elif len(p) == 5:
            p[0] = mdHTML(p[3])

    def p_head(self, p):
        """head : HEAD LINE code"""
        p[0] = mdHead(*p[3])

    def p_body(self, p):
        """body : BODY LINE code"""
        p[0] = mdBody(*p[3])

    def p_code(self, p):
        """code : code block
                | block
        """
        if len(p) == 3:
            p[1].append(p[2])
            p[0] = p[1]
        elif len(p) == 2:
            p[0] = mdContents(p[1])

    # Div
    def p_md_div(self, p):
        """markdown_line : div LINE
                         | div
        """
        p[0] = p[1]

    def p_div(self, p):
        """div : DIVPUSH_INDENT div_header LINE code DIVPOP_INDENT"""
        tag, keys = p[2]
        if tag is None:
            p[0] = mdDiv(*p[4])
            p[0].update(keys)
        else:
            Tag = mdTag.new(tag)
            p[0] = Tag(*p[4])
            p[0].update(keys)

    def p_div_header(self, p):
        """div_header : space div_tag space div_options space"""
        p[0] = p[2], p[4]

    def p_div_tag(self, p):
        """div_tag : NAME
                   |
        """
        if len(p) == 2:
            p[0] = p[1]
        else:
            p[0] = None

    def p_div_options(self, p):
        """div_options : div_options space div_option
                       | div_option
                       |
        """
        if len(p) == 4:
            k, v = p[3]
            if k in p[1]:
                p[1][k] = f"{p[1][k]} {v}"
            else:
                p[1][k] = v
            p[0] = p[1]
        elif len(p) == 2:
            k, v = p[1]
            p[0] = {k: v}
        else:
            p[0] = {}

    def p_div_option_id(self, p):
        """div_option : HASH NAME"""
        p[0] = ("id", p[2])

    def p_div_option_class(self, p):
        """div_option : DOT NAME"""
        p[0] = ("class", p[2])

    # Pinecode
    def p_block_pinecode(self, p):
        """block : pinecode_block"""
        p[0] = p[1]

    def p_pinecode_block(self, p):
        """pinecode_block : pinecode_block pinecode_line
                          | pinecode_line
        """
        if len(p) == 3:
            p[1].append(p[2])
            p[0] = p[1]
        else:
            p[0] = mdBlock(p[1])

    def p_pinecode_line(self, p):
        """pinecode_line : pinecode LINE
                         | pinecode
        """
        p[0] = p[1]

    def p_pinecode(self, p):
        """pinecode : pine_assignment
                    | pine_include
                    |
        """
        if len(p) == 2:
            p[0] = p[1]
        else:
            p[0] = mdNull()

    def p_pine_assignment(self, p):
        """pine_assignment : PINE_VAR space NAME space EQUAL space STRING"""
        self.set_var(p[3], str(p[7][1:-1]))
        p[0] = mdNull()

    def p_pine_include(self, p):
        """pine_include : PINE_INCLUDE space STRING"""
        p[0] = self.include(str(p[3][1:-1]))

    # Markdown
    def p_block_markdown(self, p):
        """block : markdown_block LINE
                 | markdown_block
        """
        p[0] = p[1]

    def p_markdown_block(self, p):
        """markdown_block : markdown_block markdown_line
                          | markdown_line
        """
        if len(p) == 3:
            p[1].append(p[2])
            p[0] = p[1]
        else:
            p[0] = mdBlock(p[1])

    def p_markdown_line(self, p):
        """markdown_line : INDENT markdown LINE
                         | INDENT markdown
        """
        p[0] = p[2]

    def p_markdown(self, p):
        """markdown : markdown markdown_element
                    | markdown_element
        """
        if len(p) == 3:
            p[1].append(p[2])
            p[0] = p[1]
        else:
            p[0] = mdText(p[1])

    def p_markdown_element(self, p):
        """markdown_element : effect
                            | text
                            | link
                            | load
        """
        if len(p) == 2:
            p[0] = p[1]
        else:
            p[0] = mdNull()

    def p_mark(self, p):
        """mark : DOT
                | HASH
                | DASH
                | PLUS
                | RCUR
                | LCUR
                | LPAR
                | RPAR
                | EQUAL
        """
        p[0] = p[1]

    def p_effect_italic(self, p):
        """effect : UNDER space markdown_element space UNDER"""
        p[0] = mdItalic(p[3])

    def p_effect_bold(self, p):
        """effect : AST space markdown_element space AST"""
        p[0] = mdBold(p[3])

    def p_effect_strike(self, p):
        """effect : TILDE space markdown_element space TILDE"""
        p[0] = mdStrike(p[3])

    def p_effect_code(self, p):
        """effect : TICK space markdown_element space TICK"""
        p[0] = mdCode(p[3])

    def p_link(self, p):
        """link : LBRA text RBRA LPAR space markdown_element space RPAR"""
        p[0] = mdLink(p[2], p[6])

    def p_xlink(self, p):
        """link : LBRA text RBRA AST LPAR space markdown_element space RPAR"""
        p[0] = mdXLink(p[2], p[7])

    def p_load(self, p):
        """load : LBRA text RBRA AT NAME"""
        p[0] = mdLoader(p[2], p[5])


    # Text & Words
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
        | NAME
        | mark
        | SPACE
        | ESCAPE
        """
        p[0] = mdText(p[1])

    def p_word_var(self, p):
        """word : DOLL NAME"""
        p[0] = self.get_var(p[2])


    # Lists
    def p_list_block(self, p):
        """block : ulist_block
                 | olist_block
        """
        p[0] = mdBlock(p[1])

    def p_ulist_block(self, p):
        """ulist_block : ulist_block ulist_line
                       | ulist_line
        """
        if len(p) == 3:
            p[1].append(p[2])
            p[0] = p[1]
        else:
            p[0] = mdUList(p[1])

    def p_ulist_item(self, p):
        """ulist_line : ULIST_INDENT space markdown space LINE
                      | ULIST_INDENT space markdown space
        """
        p[0] = mdListItem(p[3])

    def p_olist_block(self, p):
        """olist_block : olist_block olist_line
                       | olist_line
        """
        if len(p) == 3:
            p[1].append(p[2])
            p[0] = p[1]
        else:
            p[0] = mdOList(p[1])

    def p_olist_item(self, p):
        """olist_line : OLIST_INDENT space markdown space LINE
                      | OLIST_INDENT space markdown space
        """
        p[0] = mdListItem(p[3])

    # Spacing
    def p_space(self, p):
        """space : SPACE
        |
        """
        if len(p) == 2:
            p[0] = p[1]
        else:
            p[0] = None