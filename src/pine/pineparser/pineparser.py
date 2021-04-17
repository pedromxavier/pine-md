"""
"""
## Standard Library
import re
import itertools as it
from time import perf_counter as clock
from pathlib import Path
from dataclasses import dataclass
from collections import deque

## Third-Party
from ply import yacc

## Local
from .pinelexer import PineLexer, source

class mdType(object):

    def __init__(self, *child):
        self.child = child

    @property
    def items(self):
        return ",".join(map(repr, self.child))

    def __repr__(self):
        return f"mdType({self.items})"

class PineParser(object):

    class PineSyntaxError(Exception):
        def __init__(self, msg: str, *, lineno: int = '?'):
            Exception.__init__(self, msg)
            self.msg = f"In line {lineno}:\nSyntax Error: {msg}"

    @dataclass
    class Flags:
        indent: int = 0
    

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

    def parse(self, source: str, *, debug: bool = False):
        self.__flags = self.Flags()
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
        self.__output = output

    def include(self, path: str, *, lineno: int = 0) -> mdType:
        """ Includes content rendered from another file.
        """
        path = Path(path)
        if not path.exists() or not path.is_file():
            print(f"in line {lineno} WARNING: File '{path}' not found.")
            return mdType("")
        else: ## Not Implemented
            return mdType(path)

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
            self.syntax_error("Unexpected EOF.")
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
                p[1].append(p[3])
            p[0] = p[1]
        else:
            if p[1] is not None:
                p[0] = [p[1]]
            else:
                p[0] = []

    def p_block_html(self, p):
        """ block : HTML
                  | HEAD
                  | BODY
        """
        p[0] = p[1]

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
        """ markdown : scope
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
        p[0] = ("type:Header", p[1], p[3])

    def p_content(self, p):
        """ content : content fragment
                    | fragment
        """
        if len(p) == 3:
            p[1].append(p[2])
            p[0] = p[1]
        else:
            p[0] = [p[1]]

    def p_fragment_link(self, p):
        """ fragment : LBRA HREF RBRA LPAR content RPAR
        """
        p[0] = ('type:Link', p[2], p[5])

    def p_fragment_ext_link(self, p):
        """ fragment : LBRA HREF RBRA AT LPAR content RPAR
        """
        p[0] = ('type:ExtLink', p[2], p[6])

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
        p[0] = (p[1], p[2], p[3])
            

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
    
    def p_block_empty(self, p):
        """ block : empty 
        """
        p[0] = p[1]

    def p_empty(self, p):
        """ empty : """
        pass 

if __name__ == '__main__':
    t = clock()
    pparser = PineParser()
    args = pparser.parse(source, debug=True)
    print(f"Parse time: {clock() - t:.5f}s")
    
