"""
"""
## Standard Library
import re
from pathlib import Path


## Third-Party
from ply import yacc

## Local
from ..items import mdType, mdNull, mdCommand, mdContents
from ..items import mdHeader, mdText, mdLink, mdXLink
from ..items import mdStrike, mdCode, mdBold, mdItalic
from ..items import mdListItem
from .pinelexer import PineLexer

class PineParser(object):

    class PineSyntaxError(Exception):
        def __init__(self, msg: str, *, lineno: int = '?'):
            Exception.__init__(self, msg)
            self.msg = f"In line {lineno}:\nSyntax Error: {msg}"

    precedence = (
        ('left', 'I', 'B', 'C', 'S'),
    )

    tokens = PineLexer.tokens

    def __init__(self):
        self.lexer = PineLexer()
        self.parser = yacc.yacc(module=self, debug=True)

        # --- memory ---
        self.__var_table = {}

        # --- debug ----
        self.__debug = False

        # --- output ---
        self.__output = None

    def parse(self, source: str, *, debug: bool = False) -> list:
        self.__debug = debug
        try:
            self.parser.parse(source, lexer=self.lexer.lexer)
        except self.PineSyntaxError as error:
            print(error.msg)
        except PineLexer.PineLexerError as error:
            print(error.msg)

        if self.__debug:
            print(f"VAR TABLE:\n{self.__var_table}")
        
        return self.__output

    def retrieve(self, output: list):
        self.__output: list = output

    def include(self, path: str, *, lineno: int = 0) -> mdType:
        """ Includes content rendered from another file.
        """
        path = Path(path)
        if not path.exists() or not path.is_file():
            print(f"in line {lineno} WARNING: File '{path}' not found.")
            return mdNull()
        else: ## Not Implemented
            with open(path, 'r', encoding='utf-8') as file:
                subparser = self.__class__()
                return subparser.parse(file)

    def set_var(self, name: str, item: object):
        self.__var_table[name] = item

    def get_var(self, name: str):
        try:
            return self.__var_table[name]
        except KeyError:
            return None

    def syntax_error(self, msg):
        raise self.PineSyntaxError(msg, lineno=self.lexer.lexer.lineno)

    ## ------- YACC -------
    def p_error(self, p):
        if p is None:
            self.syntax_error(f"Unexpected EOF. [{self.parser.state}]")
        else:
            self.syntax_error(f"problem at {p.type!r} [{self.parser.state}]")

    def p_start(self, p):
        """ start : blocklist
        """
        self.retrieve(p[1])

    def p_blocklist(self, p):
        """ blocklist : blocklist ENDL block
                      | block
        """
        if len(p) == 4:
            if p[3] is not None:
                p[1].append((p[2], p[3]))
            p[0] = p[1]
        else:
            if p[1] is not None:
                p[0] = [(0, p[1])]
            else:
                p[0] = []

    def p_block_html(self, p):
        """ block : HTML
                  | HEAD
                  | BODY
        """
        p[0] = mdCommand(p[1])

    def p_block_pinecode(self, p):
        """ block : pinecode """
        p[0] = p[1]

    def p_pinecode(self, p):
        """ pinecode : include
                     | set_var
        """
        p[0] = p[1]

    def p_include(self, p):
        """ include : INCLUDE SPACE PATH
        """
        p[0] = self.include(p[3], lineno=p.lineno(3))

    def p_set_var(self, p):
        """ set_var : SET_VAR SPACE NAME SPACE EQ SPACE CONTENT
        """
        self.set_var(p[3], p[7])

    def p_block_markdown(self, p):
        """ block : markdown """
        p[0] = p[1]

    def p_markdown_scope(self, p):
        """ block : scope
        """
        p[0] = p[1]

    def p_scope(self, p):
        """ scope : INDENT PUSH scope_header ENDL blocklist ENDL INDENT POP """
        p[0] = ('type:Scope', p[3], p[5])

    def p_scope_header(self, p):
        """ scope_header : scope_tag scope_options
        """
                        
        p[0] = (p[1], p[2])

    def p_scope_tag(self, p):
        """ scope_tag : NAME
                      | empty
        """
        if p[1] is not None:
            p[0] = p[1]
        else:
            p[0] = 'div'

    def p_scope_options(self, p):
        """ scope_options : scope_options scope_option
                          | scope_option
                          | empty
        """
        if len(p) == 3:
            p[1].append(p[2])
            p[0] = p[1]
        else:
            if p[1] is not None:
                p[0] = [p[1]]
            else:
                p[0] = []

    def p_scope_option(self, p):
        """ scope_option : ID
                         | CLASS
        """
        p[0] = p[1]


    def p_markdown_else(self, p):
        """ markdown : INDENT header
                     | INDENT content
        """
        p[0] = (p[1], p[2])

    def p_header(self, p):
        """ header : HEADER SPACE content """
        Header = mdHeader.new(p[1])
        p[0] = Header(p[3])

    def p_content(self, p):
        """ content : content fragment
                    | fragment
        """
        if len(p) == 3:
            p[1].append(p[2])
            p[0] = p[1]
        else:
            p[0] = mdText(p[1])

    def p_fragment_link(self, p):
        """ fragment : LBRA HREF RBRA LPAR content RPAR
        """
        p[0] = mdLink(p[2], p[5])

    def p_fragment_ext_link(self, p):
        """ fragment : LBRA HREF RBRA AT LPAR content RPAR
        """
        p[0] = p[0] = mdXLink(p[2], p[6])

    def p_fragment_load(self, p):
        """ fragment : LBRA HREF RBRA AT NAME
        """
        p[0] = ('type:Loader', p[2], p[5])

    def p_fragment_effects(self, p):
        """ fragment : I content I
                     | B content B
                     | C content C
                     | S content S
        """
        if p[1] == 'i': # italic
            p[0] = mdItalic(p[2])
        elif p[1] == 'b':
            p[0] = mdBold(p[2])
        elif p[1] == 'c':
            p[0] = mdCode(p[2])
        elif p[1] == 's':
            p[0] = mdStrike(p[2])
        else:
            raise ValueError("CRITICAL ERROR @ p_fragment_effects")

    def p_fragment_else(self, p):
        """ fragment : WORD
                     | getvar
                     | ESCAPE
                     | SPACE
        """
        p[0] = p[1]

    def p_getvar(self, p):
        """ getvar : GET_VAR NAME
        """
        p[0] = self.get_var(p[2])

    def p_markdown_list(self, p):
        """ markdown : INDENT ULIST content
                     | INDENT OLIST content
        """
        p[0] = (p[1], p[2], p[3])
    
    def p_block_empty(self, p):
        """ block : empty 
        """
        p[0] = p[1]

    def p_empty(self, p):
        """ empty : """
        pass 