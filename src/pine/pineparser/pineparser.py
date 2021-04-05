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
from .mdparser import mdParser

class pineLexer(Lexer):

    ## List of token names.
    tokens = (
        'LINE',
        "HTML", 'HEAD', 'BODY',
        'MARKDOWN', 'INCLUDE',
        'LOAD',
        'ASSIGNMENT', 'NAME', 'STRING',
        'EQ',
        'DIV_PUSH', 'DIV_POP', 'DIV_CLASS', 'DIV_ID'
    )

    @regex(r'\n')
    def t_LINE(self, t):
        self.lexer.lineno += 1
        return t

    @regex(r'^\#[^\r\n]*$')
    def t_COMMENT(self, t):
        return None

    @regex(r'^html$')
    def t_HTML(self, t):
        return t

    @regex(r'^head$')
    def t_HEAD(self, t):
        return t

    @regex(r'^body$')
    def t_BODY(self, t):
        return t

    RE_DIV_PUSH = r'^[^\S\r\n]*\{[^\S\r\n]*([a-zA-Z0-9\_\-\+]*)'
    @regex(RE_DIV_PUSH)
    def t_DIV_PUSH(self, t):
        t.value = re.match(self.RE_DIV_PUSH, t.value, self.RE_FLAGS).group(1).strip('\t ')
        return t

    @regex(r'^[^\S\r\n]*\}[^\S\r\n]*$')
    def t_DIV_POP(self, t):
        t.value = r'\}'
        return t

    RE_LOAD = r'^\@([a-z]+)[^\S\r\n]+([^\r\n]+)$'
    @regex(RE_LOAD)
    def t_LOAD(self, t):
        m = re.match(self.RE_LOAD, t.value, self.RE_FLAGS)
        t.value = (m.group(2), m.group(1))
        return t

    RE_INCLUDE = r'^\/(\t|[ ]{3})[^\S\r\n]*([^\r\n]+)$'
    @regex(RE_INCLUDE)
    def t_INCLUDE(self, t):
        t.value = re.match(self.RE_INCLUDE, t.value, self.RE_FLAGS).group(2).strip('\t ')
        return t

    @regex(r'^\$(\t|[ ]{3})')
    def t_ASSIGNMENT(self, t):
        t.value = r'\$'
        return t

    RE_MARKDOWN = r'^(\t|[ ]{4})[^\S\r\n]*([^\r\n]+)$'
    @regex(RE_MARKDOWN)
    def t_MARKDOWN(self, t):
        t.value = re.match(self.RE_MARKDOWN, t.value, self.RE_FLAGS).group(2).strip('\t ')
        return t

    @regex(r'\"[^\"\r\n]*\"|\'[^\'\r\n]*\'')
    def t_STRING(self, t):
        t.value = str(t.value[1:-1])
        return t

    @regex(r'\.[a-zA-Z0-9\_\-]+')
    def t_DIV_CLASS(self, t):
        t.value = str(t.value[1:])
        return t

    @regex(r'\#[a-zA-Z0-9\_\-]+')
    def t_DIV_ID(self, t):
        t.value = str(t.value[1:])
        return t

    @regex(r'[a-zA-Z0-9_]+')
    def t_NAME(self, t):
        return t

    @regex(r'[ ]')
    def t_SPACE(self, t):
        return None

    t_EQ = r'\='

class pineParser(Parser):

    Lexer = pineLexer
    tokens = pineLexer.tokens

    def __init__(self, source: Source):
        Parser.__init__(self, source)

    def markdown(self, s: str):
        md_parser = mdParser(Source.from_str(s))
        return md_parser.parse(symbol_table=self.symbol_table)

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

    def p_block_markdown(self, p):
        """block : markdown_block LINE
                 | markdown_block
        """
        p[0] = self.markdown(str(p[1]))

    def p_markdown_block(self, p):
        """markdown_block : markdown_block markdown_line
                          | markdown_line
        """
        if len(p) == 3:
            p[1].append(p[2])
            p[0] = (p[1])
        else:
            p[0] = mdBlock(p[1])

    def p_markdown_line(self, p):
        """markdown_line : MARKDOWN LINE
                         | MARKDOWN
        """
        p[0] = p[1]

    def p_block_pinecode(self, p):
        """block : pinecode_block
        """
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
        """pinecode : assignment
                    | include
                    | load
                    | div
                    |
        """
        if len(p) == 2:
            p[0] = p[1]
        else:
            p[0] = mdNull()

    def p_assignment(self, p):
        """assignment : ASSIGNMENT NAME EQ STRING"""
        self.set_var(p[2], p[4])
        p[0] = mdNull()

    def p_include(self, p):
        """include : INCLUDE"""
        p[0] = self.include(p[1])

    def p_load(self, p):
        """load : LOAD"""
        ref, key = p[1]
        p[0] = mdLoader(ref, key)

    def p_div(self, p):
        """div : DIV_PUSH div_options LINE block DIV_POP
        """
        if p[1]:
            Tag = mdTag.new(p[1])
            tag = Tag(*p[4])
            tag.update(p[2])
            p[0] = tag
        else:
            tag = mdDiv(*p[4])
            tag.update(p[2])
            p[0] = tag

    def p_div_options(self, p):
        """div_options : div_options div_option
                       | div_option
                       |
        """
        if len(p) == 3:
            k, v = p[2]
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
        """div_option : DIV_ID"""
        p[0] = ('id', p[1])

    def p_div_option_class(self, p):
        """div_option : DIV_CLASS"""
        p[0] = ('class', p[1])