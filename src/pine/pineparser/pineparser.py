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
from ..items import mdJavascript, mdPre, mdCode
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
        self.line_break = False

    @classmethod
    def _add_js_context(cls, js_context):
        cls.__js__ = js_context

    @property
    def js_context(self):
        if self.__js__ is None:
            self._add_js_context(pyduktape.DuktapeContext())
        return self.__js__

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
        """ start : blocklist"""
        self.retrieve(mdDocument(*p[1]))

    def p_blocklist(self, p):
        """ blocklist : blocklist newline block
                      | block
        """
        if len(p) == 4:
            if p[3] is not None:
                p[1].append(p[3])
            p[0] = p[1]
        else:
            if p[1] is not None:
                p[0] = [p[1]]
            else:
                p[0] = []

    def p_newline(self, p):
        """ newline : ENDL
                    | BREAK
        """
        p[0] = p[1]

    def p_block_div(self, p):
        """ block : div 
        """
        p[0] = p[1]

    def p_block_list(self, p):
        """ block : listitem """
        p[0] = p[1]

    def p_listitem(self, p):
        """ listitem : OLIST MARKDOWN
                     | ULIST MARKDOWN
        """
        p[0] = (p[1], p[2])

    def p_div(self, p):
        """ div : DIVPUSH divheader newline blocklist DIVPULL """
        Tag = mdTag.new(p[2]['name'])
        div = Tag(*p[4])
        div.update({'class': p[2]['class'], 'id': p[2]['id']})
        p[0] =  div

    def p_divheader(self, p):
        """ divheader : divheader divitem
                      | divitem
        """
        if len(p) == 3:
            p[1].update(p[2])
            p[0] = p[1]
        else:
            p[0] = {'name': 'div', 'class': '', 'id': ''}
            p[0].update(p[1])

    def p_divheader_empty(self, p):
        """ divheader : """
        p[0] = {'name': 'div', 'class': '', 'id': ''}

    def p_divitem_divname(self, p):
        """ divitem : DIVNAME """
        p[0] = {'name' : p[1]}

    def p_divitem_divid(self, p):
        """ divitem : DIVID """
        p[0] = {'id' : p[1]}

    def p_divitem_divclass(self, p):
        """ divitem : DIVCLASS """
        p[0] = {'class' : p[1]}

    def p_block_markdown(self, p):
        """ block : MARKDOWN
        """
        p[0] = mdParser.parse(Source(buffer=p[1], offset=p.lexpos(1)))

    def p_block_javascript(self, p):
        """ block : JAVASCRIPT"""
        p[0] = mdJavascript(p[1])

    def p_block_codeblock(self, p):
        """ block : CODEBLOCK"""
        lang, code = p[1]
        code = mdCode(mdType.html_escape(code))
        code['class'] = f'language-{lang}'
        p[0] = mdPre(code)

    def p_block_empty(self, p):
        """ block : """
        p[0] = None