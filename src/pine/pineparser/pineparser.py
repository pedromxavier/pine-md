"""
"""
## Standard Library
from pathlib import Path


## Third-Party
from cstream import stdwar
import pyduktape

## Local
from .pinelexer import PineLexer
from .parser import Parser
from ..pinelib import Source
from ..items import mdType, mdDocument, mdTag
from ..items import mdUList, mdOList, mdListItem
from ..items import mdJavascript
from .mdparser import mdParser

class PineParser(Parser):

    tabmodule = 'pinetab'

    DEFAULT_DIV = {'name': 'div', 'id': None, 'class': []}

    # These lines are needed in subclasses
    _Lexer = PineLexer
    tokens = PineLexer.tokens

    __js__ = None

    def __init__(self, source: Source):
        Parser.__init__(self, source) 
        self.list_buffer = None
        self.list_stack = []
        self.head_stack = []
        self.line_break = False

    def head_push(self, head: list):
        self.head_stack.append(head)

    def head_pull(self) -> list:
        if self.head_stack:
            return self.head_stack.pop()
        else:
            raise ValueError('Empty head_stack')

    def markdown(self, offset: int, length: int) -> mdType:
        return mdParser.parse(self.source.slice(offset=offset, length=length))

    def get_head(self):
        if self.head_stack:
            return self.head_stack[-1]
        else:
            raise ValueError('Empty head_stack')

    def list_pull(self):
        """"""
        if self.list_stack:
            output = self.list_stack[0]['buffer']
            self.list_stack.clear()
            self.list_buffer = None
        else:
            output = None

        if output is not None:
            self.get_head().append(output)

    def list_push(self, indent: int, kind: str, item: mdType):
        """"""
        if self.list_stack:
            top = self.list_stack[-1]
            if top['indent'] == indent:
                if top['kind'] == kind:
                    self.list_buffer.append(item)
                    return None
                elif kind == '+': # Ordered List
                    if len(self.list_stack) >= 2:
                        self.list_stack[-2]['buffer'].append(self.list_buffer)
                        output = None
                    else:
                        output = self.list_buffer
                    self.list_buffer = mdOList(item)
                elif kind == '-': # Unordered List
                    if len(self.list_stack) >= 2:
                        self.list_stack[-2]['buffer'].append(self.list_buffer)
                        output = None
                    else:
                        output = self.list_buffer
                    self.list_buffer = mdUList(item)
                else:
                    raise ValueError(f"Invalid list kind: '{kind}'.")
        
                self.list_stack[-1] = {'indent': indent, 'kind': kind, 'buffer': self.list_buffer}
                return output
            elif top['indent'] < indent: # Push
                if kind == '+': # Ordered List
                    self.list_buffer = mdOList(item)
                elif kind == '-': # Unordered List
                    self.list_buffer = mdUList(item)
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
                self.list_buffer = mdOList(item)
            elif kind == '-': # Unordered List
                self.list_buffer = mdUList(item)
            else:
                raise ValueError(f"Invalid list kind: '{kind}'.")

            self.list_stack.append({'indent': indent, 'kind': kind, 'buffer': self.list_buffer})
            return None

    ## ------- YACC -------
    def p_start(self, p):
        """ start : start_hook blocklist"""
        self.list_pull()
        self.retrieve(self.head_pull())

    def p_start_hook(self, p):
        """ start_hook : """
        self.head_push(mdDocument())

    def p_blocklist(self, p):
        """ blocklist : blocklist newline block
                      | block
        """
        pass

    
    def p_newline_endl(self, p):
        """ newline : ENDL
        """
        p[0] = p[1]

    
    def p_newline_break(self, p):
        """ newline : BREAK """
        self.list_pull()
        p[0] = p[1]

    def p_listitem(self, p):
        """ block : OLIST MARKDOWN
                  | ULIST MARKDOWN
        """
        self.list_push(*p[1], mdListItem(self.markdown(offset=p.lexpos(2), length=len(p[2]))))

    def p_div(self, p):
        """ block : div_push blocklist DIVPULL """
        self.list_pull()
        div = self.head_pull()
        self.get_head().append(div)

    def p_div_push(self, p):
        """ div_push : DIVPUSH divheader newline """
        tag = mdTag(name=p[2]['name'], lang=p[2]['lang'], ID=p[2]['id'], CLASS=p[2]['class'])
        self.head_push(tag)

    def p_divheader(self, p):
        """ divheader : divheader divitem
                      | divitem
        """
        if len(p) == 3:
            key, val = p[2]
            if key == 'name' or key == 'id':
                p[1][key] = val
            elif key == 'class':
                p[1][key] = f'{p[1][key]} {val}'
            elif key == 'lang':
               p[1][key] = f'{p[1][key]},{val}'
            else:
                raise ValueError('Invalid key for html div.')
            p[0] = p[1]
        else:
            key, val = p[1]
            p[0] = {'name': 'div', 'class': '', 'id': '', 'lang': None}
            p[0][key] = val

    def p_divheader_empty(self, p):
        """ divheader : """
        p[0] = {'name': 'div', 'class': '', 'id': ''}

    def p_divitem_divname(self, p):
        """ divitem : DIVNAME """
        p[0] = ('name', p[1])

    def p_divitem_divid(self, p):
        """ divitem : DIVID """
        p[0] = ('id', p[1])

    def p_divitem_divclass(self, p):
        """ divitem : DIVCLASS """
        p[0] = ('class', p[1])

    def p_divitem_divlang(self, p):
        """ divitem : DIVLANG """
        p[0] = ('lang', p[1])

    def p_block_markdown(self, p):
        """ block : MARKDOWN
        """
        self.list_pull()
        self.get_head().append(self.markdown(offset=p.lexpos(1), length=len(p[1])))

    def p_block_javascript(self, p):
        """ block : JAVASCRIPT"""
        self.list_pull()
        self.get_head().append(mdJavascript(p[1]))

    def p_block_codeblock(self, p):
        """ block : CODEBLOCK"""
        self.list_pull()
        lang, code = p[1]
        self.get_head().append(mdTag(mdTag(mdType.html_escape(code), name='code', CLASS=f'language-{lang}'), name='pre'))

    def p_block_empty(self, p):
        """ block : """
        self.list_pull()