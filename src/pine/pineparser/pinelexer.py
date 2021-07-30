import re



from .lexer import Lexer, regex
from .mdlexer import mdLexer
from ..pinelib import Source

R_CODEBLOCK = re.compile(r"^([^\S\r\n]*)\`\`\`([a-zA-Z]*)[^\S\r\n]*\n([\S\s]+?)[^\S\r\n]*\`\`\`")
R_JAVASCRIPT = re.compile(r"^[^\S\r\n]*\§\§([\S\s]+?)\§\§")
R_OLIST = re.compile(r"^([^\S\r\n]*)\+")
R_ULIST = re.compile(r"^([^\S\r\n]*)\-")

class PineLexer(Lexer):

    states = [
        ("div", "exclusive")
    ]

    tokens = (
        "ENDL",
        "BREAK",
        "DIVPUSH",
        "DIVNAME",
        "DIVID",
        "DIVCLASS",
        "DIVPULL",
        "OLIST",
        "ULIST",
        "MARKDOWN",
        "CODEBLOCK",
        "JAVASCRIPT",
    )

    def tokenize(self) -> list:
        self.lexer.input(self.source)
        tokens = []
        while True:
            tok = self.lexer.token()
            if tok:
                tokens.append(f"[{self.lexer.current_state()}] {tok}")
                if tok.type == "MARKDOWN":
                    tokens.extend([f'\t{t}' for t in mdLexer(Source(buffer=tok.value)).tokenize()])
            else:
                return tokens

    def __init__(self, source: Source):
        Lexer.__init__(self, source)

    def indent(self, s: str) -> int:
        return s.count('\t') * self.TAB_SIZE + s.count(' ')

    def gobble(self, s: str, g: int = 0) -> str:
        i = 0
        n = len(s)
        while i < n:
            if s[i] == ' ':
                g -= 1
                i += 1
            elif s[i] == '\t':
                if g >= self.TAB_SIZE:
                    g -= self.TAB_SIZE
                    i += 1
                else:
                    break
            else:
                break
        return s[i:]

    @regex(r"^\![^\r\n]*\n?")
    def t_INITIAL_COMMENT(self, t):
        self.lexer.lineno += t.value.count("\n")
        return None

    @regex(R_OLIST.pattern)
    def t_INITIAL_OLIST(self, t):
        match = R_OLIST.match(t.value)
        indent = self.indent(match.group(1))
        t.value = (indent, '+')
        return t

    @regex(R_ULIST.pattern)
    def t_INITIAL_ULIST(self, t):
        match = R_ULIST.match(t.value)
        indent = self.indent(match.group(1))
        t.value = (indent, '-')
        return t

    @regex(r"^[^\S\r\n]*\{")
    def t_INITIAL_DIVPUSH(self, t):
        self.lexer.begin("div")
        return t

    @regex(r"[a-zA-Z][a-zA-Z0-9\-]+")
    def t_div_DIVNAME(self, t):
        return t

    @regex(r"\.[a-zA-Z][a-zA-Z0-9\-]+")
    def t_div_DIVCLASS(self, t):
        t.value = t.value[1:]
        return t

    @regex(r"\#[a-zA-Z][a-zA-Z0-9\-]+")
    def t_div_DIVID(self, t):
        t.value = t.value[1:]
        return t

    @regex(r"^[^\S\r\n]*\}")
    def t_INITIAL_DIVPULL(self, t):
        return t

    @regex(R_CODEBLOCK.pattern)
    def t_INITIAL_CODEBLOCK(self, t):
        match = R_CODEBLOCK.match(t.value)
        
        lines = match.group(3).split('\n')
        indent = self.indent(match.group(1))

        t.value = (match.group(2), '\n'.join(self.gobble(line, indent) for line in lines).strip())
        
        self.lexer.lineno += len(lines)
        return t

    @regex(R_JAVASCRIPT.pattern)
    def t_INITIAL_JAVASCRIPT(self, t):
        match = R_JAVASCRIPT.match(t.value)

        code = match.group(1)
        
        t.value = code

        self.lexer.lineno += code.count('\n')
        return t

    @regex(r"\n{2,}")
    def t_ANY_BREAK(self, t):
        self.lexer.begin("INITIAL")
        t.value = t.value.count("\n")
        self.lexer.lineno += t.value
        return t

    @regex(r"\n")
    def t_ANY_ENDL(self, t):
        self.lexer.begin("INITIAL")
        t.value = t.value.count("\n")
        self.lexer.lineno += t.value
        return t

    @regex(r"[^\S\r\n]+")
    def t_ANY_SPACE(self, t):
        return None

    @regex(r"[^\r\n]+")
    def t_INITIAL_MARKDOWN(self, t):
        return t

    def t_ANY_error(self, t):
        target = self.source.getlex(t.lexpos)
        self.lexer_error(
            f"Unexpected token '{t.value[0]}'. [{self.lexer.current_state()}]",
            target=target,
        )
