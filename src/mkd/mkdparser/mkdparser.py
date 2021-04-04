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
from .mdparser import mdParser

class mkdLexer(Lexer):

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

    @regex(r'^\{[^\S\r\n]*([a-zA-Z0-9\_\-\+]*)')
    def t_DIV_PUSH(self, t):
        t.value = re.match(r'^\{[^\S\r\n]*([a-zA-Z0-9\_\-\+]*)', t.value, self.RE_FLAGS).group(1)
        return t

    @regex(r'^\}$')
    def t_DIV_POP(self, t):
        return t

    @regex(r'^\@([a-z]+)[^\S\r\n]+([^\n]*)$')
    def t_LOAD(self, t):
        m = re.match(r'^\@([a-z]+)[^\S\r\n]+([^\n]*)$', t.value, self.RE_FLAGS)
        t.value = (m.group(2), m.group(1))
        return t

    @regex(r'^\§(\t|[ ]{3})[^\r\n]*$')
    def t_MARKDOWN(self, t):
        s = str(t.value[1:])
        if s[0] == '\t':
            t.value = s[1:]
        else:
            t.value = s[3:]
        return t

    @regex(r'^\/(\t|[ ]{3})[^\r\n]*$')
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

    t_EQ = r'\='
    t_ignore = ' '
    
    

class mkdParser(Parser):

    Lexer = mkdLexer
    tokens = mkdLexer.tokens

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

    def p_html_code(self, p):
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
        """code : code codeline
                | codeline
        """
        if len(p) == 3:
            p[1].append(p[2])
            p[0] = p[1]
        else:
            p[0] = mdContents(p[1])
    
    def p_codeline(self, p):
        """codeline : content LINE
                    | content
        """
        p[0] = p[1]
        
    def p_content(self, p):
        """content : assignment
                   | markdown
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
        return mdNull()

    def p_markdown(self, p):
        """markdown : MARKDOWN"""
        p[0] = self.markdown(p[1])

    def p_include(self, p):
        """include : INCLUDE"""
        p[0] = self.include(p[1])

    def p_load(self, p):
        """load : LOAD"""
        ref, key = p[1]
        p[0] = mdLoader(ref, key)

    def p_div(self, p):
        """div : DIV_PUSH div_options LINE code DIV_POP
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