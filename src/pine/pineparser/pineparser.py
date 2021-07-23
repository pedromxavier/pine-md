"""
"""
## Standard Library
import re
import sys
from pathlib import Path


## Third-Party
from ply import yacc
from cstream import Stream, stderr
import pyduktape

## Local
from ..pinelib import Source
from ..items import mdType, mdTag, mdDocument, mdBlock, mdLoader
from ..items import mdHeader, mdText, mdLink, mdSLink
from ..items import mdStrike, mdCode, mdBold, mdItalic
from ..items import mdUList, mdOList, mdListItem
from .pinelexer import PineLexer
from .parser import Parser


class PineParser(Parser):

    DEFAULT_DIV = {'name': 'div', 'id': None, 'class': []}

    precedence = [
        
        ("left", "ULIST", "OLIST"),
        ("left", "INDENT"),
        ("left", "LPAR", "RPAR", "LINK", "SLINK", "LOADER"),
        ("left", "WORD", "SPACE", "HREF"),
        ("left", "AST", "UNDER", "TILDE", "TICK", "LBRA", "RBRA"),
        
    ]

    # These lines are needed in subclasses
    _Lexer = PineLexer
    tokens = PineLexer.tokens

    def __init__(self, source: Source):
        Parser.__init__(self, source)
        self.js_context = None

        self.list_buffer = None
        self.list_stack = []

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
        if self.js_context is None:
            self.js_context = pyduktape.DuktapeContext()
        output = self.js_context.eval_js(code)
        if output:
            return str(output)
        else:
            return None

    def list_pull(self):
        """"""
        if self.list_stack:
            output = self.list_stack[0]['buffer']
            self.list_stack.clear()
            self.list_buffer = None
        else:
            output = None

        return output


    def list_push(self, indent: int, kind: str, item: mdType):
        """"""
        if self.list_stack:
            top = self.list_stack[-1]
            if top['indent'] == indent:
                if top['kind'] == kind:
                    self.list_buffer.append(mdListItem(item))
                    return None
                elif kind == '+': # Ordered List
                    if len(self.list_stack) >= 2:
                        self.list_stack[-2]['buffer'].append(self.list_buffer)
                        output = None
                    else:
                        output = self.list_buffer
                    self.list_buffer = mdOList(mdListItem(item))
                elif kind == '-': # Unordered List
                    if len(self.list_stack) >= 2:
                        self.list_stack[-2]['buffer'].append(self.list_buffer)
                        output = None
                    else:
                        output = self.list_buffer
                    self.list_buffer = mdUList(mdListItem(item))
                else:
                    raise ValueError(f"Invalid list kind: '{kind}'.")
        
                self.list_stack[-1] = {'indent': indent, 'kind': kind, 'buffer': self.list_buffer}
                return output
            elif top['indent'] < indent: # Push
                if kind == '+': # Ordered List
                    self.list_buffer = mdOList(mdListItem(item))
                elif kind == '-': # Unordered List
                    self.list_buffer = mdUList(mdListItem(item))
                else:
                    raise ValueError(f"Invalid list kind: '{kind}'.")
                
                self.list_stack[-1]['buffer'].append(self.list_buffer)
                self.list_stack.append({'indent': indent, 'kind': kind, 'buffer': self.list_buffer})
                return None
            else:
                self.list_stack.pop()
                if self.list_stack:
                    self.list_buffer = self.list_stack[-1]['buffer']
                return self.list_push(indent, kind, item)
        else:
            if kind == '+': # Ordered List
                self.list_buffer = mdOList(mdListItem(item))
            elif kind == '-': # Unordered List
                self.list_buffer = mdUList(mdListItem(item))
            else:
                raise ValueError(f"Invalid list kind: '{kind}'.")

            self.list_stack.append({'indent': indent, 'kind': kind, 'buffer': self.list_buffer})
            return None

    ## ------- YACC -------
    def p_start(self, p):
        """start : blocklist"""
        self.retrieve(mdDocument(self.list_pull(), *p[1]))

    def p_blocklist(self, p):
        """blocklist : blocklist ENDL block
                     | block
        """
        if len(p) == 4:
            p[0] = [*p[1], *p[3]]
        else:
            p[0] = p[1]

    def p_block(self, p):
        """ block : div
                  | header
                  | mdline
                  | codeblock
        """
        p[0] = [self.list_pull(), p[1]]

    def p_block_list(self, p):
        """ block : listitem """
        p[0] = [self.list_push(*p[1])]

    def p_listitem(self, p):
        """ listitem : INDENT listtoken space markdown"""
        p[0] = (p[1], p[2], mdText(*p[4]))

    def p_listtoken(self, p):
        """ listtoken : OLIST
                      | ULIST
        """
        p[0] = p[1]

    def p_header(self, p):
        """ header : INDENT HEADING space markdown
        """
        Heading = mdHeader.new(p[2])
        p[0] =  Heading(*p[4])

    def p_markdown_line(self, p):
        """ mdline : INDENT markdown
        """
        p[0] = mdText(*p[2])

    # :: LISTS ::

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

    def p_fragment(self, p):
        """ fragment : loader
                     | javascript
                     | WORD
                     | SPACE
                     | italic
                     | bold
                     | strike
                     | code
        """
        p[0] = p[1]

    def p_loader(self, p):
        """ loader : LBRA HREF LOADER """
        p[0] = mdLoader(p[2], p[3])

    def p_loader_ref(self, p):
        """ loader : LBRA HREF RBRA """
        p[0] = ("loader-ref", p[2])

    def p_loader_link(self, p):
        """ loader : LBRA HREF LINK markdown RPAR"""
        p[0] = mdLink(p[2], p[5])

    def p_loader_slink(self, p):
        """ loader : LBRA HREF SLINK markdown RPAR"""
        p[0] = mdSLink(p[2], p[5])

    def p_format_italic(self, p):
        """ italic : UNDER markdown UNDER """
        p[0] = mdItalic(*p[2])

    def p_format_bold(self, p):
        """ bold : AST markdown AST """
        p[0] = mdBold(*p[2])

    def p_format_strike(self, p):
        """ strike : TILDE markdown TILDE """
        p[0] = mdStrike(*p[2])

    def p_format_code(self, p):
        """ code : TICK markdown TICK """
        p[0] = mdCode(*p[2])

    # :: JAVASCRIPT ::
    def p_javascript_code(self, p):
        """ javascript : JSPUSH JSCODE JSPULL """
        p[0] = self.javascript(p[2])

    def p_javascript_blank(self, p):
        """ javascript : JSPUSH JSPULL """
        p[0] = None

    # :: JAVASCRIPT ::
    def p_codeblock(self, p):
        """ codeblock : CBPUSH CBCODE CBPULL
        """
        p[0] = p[2]

    def p_codeblock_empty(self, p):
        """ codeblock : CBPUSH CBPULL
        """
        p[0] = None

    def p_div(self, p):
        """ div : INDENT DIVPUSH divheader ENDL blocklist ENDL INDENT DIVPULL
        """
        Tag = mdTag.new(p[3]['name'])
        element = Tag(*p[5])
        element.update({'id' : p[3]['id'], 'class': " ".join(p[3]['class'])})
        p[0] = element

    def p_divheader(self, p):
        """ divheader : space divkeys """
        keys = self.DEFAULT_DIV.copy()
        keys.update(p[2])
        p[0] = keys

    def p_divheader_empty(self, p):
        """ divheader : """
        p[0] = self.DEFAULT_DIV.copy()

    def p_divkeys(self, p):
        """divkeys : divkeys space divkey
                   | divkey
        """
        if len(p) == 4:
            keys = p[1]
            key, val = p[3]
        else:
            keys = {}
            key, val = p[1]
        
        if key == 'id' or key == 'name':
            keys[key] = val
        elif key == 'class':
            if key in keys:
                keys[key].append(val)
            else:
                keys[key] = [val]
        else:
            raise ValueError('key not in {id, name, class}')
        
        p[0] = keys

    def p_divkey_name(self, p):
        """divkey : DIVNAME"""
        p[0] = ('name', p[1])
        
    def p_divkey_id(self, p):
        """divkey : DIVID"""
        p[0] = ('id', p[1])

    def p_divkey_class(self, p):
        """divkey : DIVCLASS"""
        p[0] = ('class', p[1])

    def p_block_empty(self, p):
        """ block : INDENT
                  |
        """
        p[0] = []

    def p_space(self, p):
        """ space : SPACE
                  | 
        """
        if len(p) == 2:
            p[0] = p[1]
        else:
            p[0] = 0