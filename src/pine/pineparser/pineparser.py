"""
"""
## Standard Library
import re
import sys
from pathlib import Path


## Third-Party
from ply import yacc
from cstream import Stream, stderr
import pyduktape as pdt

## Local
from ..items import mdType, mdNull, mdCommand, mdContents
from ..items import mdHeader, mdText, mdLink, mdXLink
from ..items import mdStrike, mdCode, mdBold, mdItalic
from ..items import mdUListItem, mdOListItem
from .pinelexer import PineLexer
from .parser import Parser


class PineParser(Parser):

    precedence = [
        ("left", "ENDL", "AST", "UNDER", "TILDE", "TICK", "LPAR", "RPAR", "LBRA", "RBRA")
    ]

    # These lines are needed in subclasses
    _Lexer = PineLexer
    tokens = PineLexer.tokens

    def include(self, path: str, *, lineno: int = 0) -> mdType:
        """Includes content rendered from another file."""
        path = Path(path)
        if not path.exists() or not path.is_file():
            print(f"in line {lineno} WARNING: File '{path}' not found.")
            return None
        else:  ## Not Implemented
            with open(path, "r", encoding="utf-8") as file:
                subparser = self.__class__(file.read())
                return subparser.parse()

    def javascript(self, code: str) -> str:
        return f"JS[{code}]"

    ## ------- YACC -------
    def p_start(self, p):
        """start : blocklist"""
        return self.retrieve(p[1])

    def p_blocklist(self, p):
        """blocklist : blocklist block
        | block
        """
        if len(p) == 3:
            if p[2] is not None:
                p[1].append(p[2])
            p[0] = p[1]
        else:
            if p[1] is not None:
                p[0] = [p[1]]
            else:
                p[0] = []

    def p_block_header(self, p):
        """block : INDENT HEADING SPACE markdown ENDL
        | INDENT HEADING SPACE markdown
        """
        p[0] = ("heading", p[1], p[2], p[4])

    def p_block_markdown(self, p):
        """block : INDENT markdown ENDL
        | INDENT markdown
        """
        p[0] = ("markdown-line", p[1], p[2])

    def p_markdown(self, p):
        """markdown : markdown fragment
        | fragment
        """
        if len(p) == 3:
            if p[2] is not None:
                p[1].append(p[2])
            p[0] = p[1]
        else:
            p[0] = [p[1]]

    def p_fragment_loader(self, p):
        """ fragment : loader"""
        p[0] = p[1]

    def p_loader(self, p):
        """ loader : LBRA HREF LOADER """
        p[0] = ("loader", p[2], p[3])

    def p_loader_ref(self, p):
        """ loader : LBRA HREF RBRA """
        p[0] = ("loader-ref", p[2])

    def p_loader_link(self, p):
        """ loader : LBRA HREF LINK markdown RPAR"""
        p[0] = ("loader-link", p[2], p[5])

    def p_loader_slink(self, p):
        """ loader : LBRA HREF SLINK markdown RPAR"""
        p[0] = ("loader-slink", p[2], p[5])

    def p_fragment_javascript(self, p):
        """ fragment : javascript"""
        p[0] = p[1]

    def p_fragment_basic(self, p):
        """fragment : WORD
        | SPACE
        """
        p[0] = p[1]

    def p_fragment_format(self, p):
        """fragment : italic
        | bold
        | strike
        | code
        """
        p[0] = p[1]

    def p_format_italic(self, p):
        """ italic : UNDER markdown UNDER """
        p[0] = ("italic", p[2])

    def p_format_bold(self, p):
        """ bold : AST markdown AST """
        p[0] = ("bold", p[2])

    def p_format_strike(self, p):
        """ strike : TILDE markdown TILDE """
        p[0] = ("strike", p[2])

    def p_format_code(self, p):
        """ code : TICK markdown TICK """
        p[0] = ("code", p[2])

    # :: JAVASCRIPT ::
    def p_javascript_code(self, p):
        """ javascript : JSPUSH JSCODE JSPULL """
        p[0] = self.javascript(p[2])

    def p_javascript_blank(self, p):
        """ javascript : JSPUSH JSPULL """
        p[0] = None

    # :: JAVASCRIPT ::

    def p_block_list(self, p):
        """ block : list """
        p[0] = p[1]

    def p_list(self, p):
        """list : ulist
        | olist
        """
        p[0] = p[1]

    def p_ulist(self, p):
        """ulist : ulist ulistitem
        | ulistitem
        """
        if len(p) == 3:
            p[1].append(p[2])
            p[0] = p[1]
        else:
            p[0] = [p[1]]

    def p_ulistitem(self, p):
        """ulistitem : INDENT ULIST markdown ENDL
        | INDENT ULIST markdown
        """
        p[0] = p[3]

    def p_olist(self, p):
        """olist : olist olistitem
        | olistitem
        """
        if len(p) == 3:
            p[1].append(p[2])
            p[0] = p[1]
        else:
            p[0] = [p[1]]

    def p_olistitem(self, p):
        """olistitem : INDENT OLIST markdown ENDL
        | INDENT OLIST markdown
        """
        p[0] = p[3]

    def p_block_codeblock(self, p):
        """ block : codeblock """

    def p_codeblock(self, p):
        """codeblock : CBPUSH CBCODE CBPULL ENDL
        | CBPUSH CBCODE CBPULL
        """
        p[0] = p[2]

    def p_codeblock_empty(self, p):
        """codeblock : CBPUSH CBPULL ENDL
        | CBPUSH CBPULL
        """
        p[0] = None

    def p_block_div(self, p):
        """ block : div """
        p[0] = p[1]

    def p_div(self, p):
        """div : INDENT DIVPUSH divheader ENDL blocklist INDENT DIVPULL ENDL
        | INDENT DIVPUSH divheader ENDL blocklist INDENT DIVPULL
        """
        p[0] = ("div", p[3], p[5])

    def p_divheader_full(self, p):
        """ divheader : SPACE DIVNAME SPACE divkeys """
        p[0] = ("divheader", p[2], p[4])

    def p_divheader_name(self, p):
        """ divheader : SPACE DIVNAME """
        p[0] = ("divheader", p[2], [])

    def p_divheader_keys(self, p):
        """ divheader : SPACE divkeys """
        p[0] = ("divheader", None, p[2])

    def p_divheader_empty(self, p):
        """ divheader : """
        p[0] = ("divheader", None, [])

    def p_divkeys(self, p):
        """divkeys : divkeys SPACE divkey
        | divkey
        """
        if len(p) == 4:
            if p[3] is not None:
                p[1].append(p[3])
            p[0] = p[1]
        else:
            p[0] = [p[1]]

    def p_divkey(self, p):
        """divkey : DIVID
        | DIVCLASS
        """
        if len(p) == 2:
            p[0] = p[1]
        else:
            p[0] = None

    def p_block_empty(self, p):
        """ block : INDENT ENDL
        | ENDL"""
        p[0] = None