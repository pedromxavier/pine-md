import re
from ply import lex

def regex(pattern: str):
    def decor(callback):
        callback.__doc__ = pattern
        return callback
    return decor

class PineLexer(object):

    TAB_SIZE = 4
    RE_FLAGS = re.VERBOSE | re.UNICODE | re.MULTILINE

    class PineLexerError(Exception):
        def __init__(self, msg: str, *, lineno: int = '?'):
            Exception.__init__(self, msg)
            self.msg = f"In line {lineno}:\nError: {msg}"

    def __init__(self):
        self.lexer = lex.lex(module=self, reflags=self.RE_FLAGS)

    def tokenize(self):
        while True:
            tok = self.lexer.token()
            if tok:
                yield tok
            else:
                break

    def display(self):
        for tok in self.tokenize():
            print(f"{tok.type}\t{tok.value!r}")

    states = [
        ('comment', 'exclusive'),
        ('include', 'exclusive'),
        ('setvar', 'exclusive'),
        ('getvar', 'exclusive'),
        ('markdown', 'exclusive'),
        ('mdinit', 'exclusive'),
        ('mdpush', 'exclusive'),
        ('mdpop', 'exclusive'),
        ('mdhref', 'exclusive'),
        ('mdload', 'exclusive'),
    ]

    tokens = (
        'INCLUDE', 'PATH',
        'SET_VAR', 'NAME', 'EQ', 'CONTENT',
        'GET_VAR',
        'INDENT',
        'SPACE',
        'ENDL',
        # Scope
        'PUSH', 'CLASS', 'ID',
        'POP',
        # Markdown stuff
        'HEADER',
        'WORD', 'ESCAPE',
        'ULIST',
        'OLIST',
        'I', 'B', 'C' , 'S',
        'LPAR', 'RPAR',
        'LBRA', 'RBRA',
        'HREF', 'AT',
        'HTML', 'HEAD', 'BODY',
    )

    def lexer_error(self, msg):
        raise self.PineLexerError(msg, lineno=self.lexer.lineno)

    @regex(r'^[^\S\r\n]+$|[^\S\r\n]*\n')
    def t_ANY_ENDL(self, t):
        t.value = t.value.count('\n')
        self.lexer.lineno += t.value
        self.lexer.begin('INITIAL')
        return t
    
    @regex(r'^[\t\ ]+')
    def t_INITIAL_INDENT(self, t):
        t.value = t.value.count('\t') * self.TAB_SIZE + t.value.count(' ')
        if t.value % self.TAB_SIZE:
            self.lexer_error("Inconsistent identation.")
        else:
            t.value //= self.TAB_SIZE
            self.lexer.begin('mdinit')
        return t

    @regex(r'^\#')
    def t_INITIAL_COMMENT(self, t):
        self.lexer.begin('comment')
        return None

    @regex(r'[^\r\n]+')
    def t_comment_CONTENT(self, t):
        # Ignore
        return None

    @regex(r'^html')
    def t_INITIAL_HTML(self, t):
        return t

    @regex(r'^head')
    def t_INITIAL_HEAD(self, t):
        return t

    @regex(r'^body')
    def t_INITIAL_BODY(self, t):
        return t

    @regex(r'^\/')
    def t_INITIAL_INCLUDE(self, t):
        self.lexer.begin('include')
        return t

    @regex(r"\"[^\"\r\n]*\"|\'[^\'\r\n]*\'")
    def t_include_PATH(self, t):
        t.value = str(t.value[1:-1])
        return t

    @regex(r'^\$')
    def t_INITIAL_SET_VAR(self, t):
        self.lexer.begin('setvar')
        return t

    @regex(r"\"(\\\"|[^\"\r\n])*\"|\'(\\\'[^\'\r\n])*\'")
    def t_setvar_CONTENT(self, t):
        t.value = str(t.value[1:-1])
        return t

    @regex(r"[a-zA-Z\_][a-zA-Z0-9\_\-]*")
    def t_setvar_NAME(self, t):
        return t

    @regex(r"\=")
    def t_setvar_EQ(self, t):
        return t

    @regex(r'\#[1-6]?')
    def t_mdinit_HEADER(self, t):
        self.lexer.begin('markdown')
        return t

    @regex(r'\{')
    def t_mdinit_PUSH(self, t):
        self.lexer.begin('mdpush')
        return t

    @regex(r'\}')
    def t_mdinit_POP(self, t):
        self.lexer.begin('mdpop')
        return t

    @regex(r'[^\S\r\n]+')
    def t_mdpush_SPACE(self, t):
        return None

    @regex(r'\b[a-zA-Z\-\_][a-zA-Z0-9\-\_]*\b')
    def t_mdpush_NAME(self, t):
        return t

    @regex(r'\#\b[a-zA-Z\-\_][a-zA-Z0-9\-\_]*\b')
    def t_mdpush_ID(self, t):
        return t

    @regex(r'\.\b[a-zA-Z\-\_][a-zA-Z0-9\-\_]*\b')
    def t_mdpush_CLASS(self, t):
        return t

    @regex(r'[^\S\r\n]+')
    def t_mdpop_SPACE(self, t):
        return None

    @regex(r'\-')
    def t_mdinit_ULIST(self, t):
        self.lexer.begin('markdown')
        return t

    @regex(r'\+')
    def t_mdinit_OLIST(self, t):
        self.lexer.begin('markdown')
        return t

    @regex(r'\\[^\r\n]')
    def t_mdinit_ESCAPE(self, t):
        t.value = t.value[1]
        self.lexer.begin('markdown')
        return t

    @regex(r'[^\s\\\~\_\*\`\[\]\(\)\#\$\-\+][^\s\\\~\_\*\$\`\[\]\(\)]*')
    def t_mdinit_WORD(self, t):
        self.lexer.begin('markdown')
        return t

    @regex(r'\[')
    def t_mdinit_LBRA(self, t):
        self.lexer.begin('mdhref')
        return t

    @regex(r'\\[^\r\n]')
    def t_markdown_ESCAPE(self, t):
        t.value = t.value[1]
        return t

    @regex(r'\_')
    def t_markdown_I(self, t):
        t.value = 'i'
        return t

    @regex(r'\*')
    def t_markdown_B(self, t):
        t.value = 'b'
        return t

    @regex(r'\`')
    def t_markdown_C(self, t):
        t.value = 'c'
        return t

    @regex(r'\~')
    def t_markdown_S(self, t):
        t.value = 's'
        return t

    @regex(r'\[')
    def t_markdown_LBRA(self, t):
        self.lexer.begin('mdhref')
        return t

    @regex(r'[^\r\n\[\]]+')
    def t_mdhref_HREF(self, t):
        return t

    @regex(r'\]')
    def t_mdhref_RBRA(self, t):
        self.lexer.begin('mdload')
        return t

    @regex(r'\@')
    def t_mdload_AT(self, t):
        return t

    @regex(r'[^\S\r\n]+')
    def t_mdload_SPACE(self, t):
        return None

    @regex(r'[a-zA_Z][a-zA-Z\-]*')
    def t_mdload_NAME(self, t):
        self.lexer.begin('markdown')
        return t

    @regex(r'\(')
    def t_mdload_LPAR(self, t):
        self.lexer.begin('markdown')
        return t

    @regex(r'\)')
    def t_markdown_RPAR(self, t):
        return t

    @regex(r'\$')
    def t_markdown_GET_VAR(self, t):
        self.lexer.begin('getvar')
        return t

    @regex(r"[a-zA-Z\_][a-zA-Z0-9\_\-]*")
    def t_getvar_NAME(self, t):
        self.lexer.begin('markdown')
        return t
    
    @regex(r'[^\s\\\~\_\*\`\$\[\]\(\)]+')
    def t_markdown_WORD(self, t):
        return t

    @regex(r'[^\S\r\n]+')
    def t_ANY_SPACE(self, t):
        t.value = ' '
        return t

    def t_ANY_error(self, t):
        self.lexer_error(f"Unexpected token '{t.value[0]}'.")