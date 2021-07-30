from .lexer import Lexer, regex
from ..pinelib import Source

class mdLexer(Lexer):

    strict = True

    tokens = (
        "LBRA",
        "RBRA",
#       "LPAR",
        "RPAR",
        "AST",
        "UNDER",
        "TILDE",
        "TICK",
        "HEADING",
        "LOADER",
        "LINK",
        "SLINK",
        "WORD",
        "JAVASCRIPT",
        "SPACE",
    )

    @regex(r"^\#[1-6][^\S\r\n]*")
    def t_HEADING(self, t):
        t.value = int(t.value[1])
        return t

    @regex(r"\[\[")
    def t_ESCLBRA(self, t):
        t.value = r"["
        t.type = "WORD"
        return t

    @regex(r"\]\]")
    def t_ESCRBRA(self, t):
        t.value = r"]"
        t.type = "WORD"
        return t

    @regex(r"\(\(")
    def t_ESCLPAR(self, t):
        t.value = r"("
        t.type = "WORD"
        return t

    @regex(r"\)\)")
    def t_ESCRPAR(self, t):
        t.value = r")"
        t.type = "WORD"
        return t
    
    @regex(r"\[")
    def t_LBRA(self, t):
        return t

    @regex(r"\]\@[a-z]+")
    def t_LOADER(self, t):
        t.value = t.value[2:]
        return t

    @regex(r"\]\(")
    def t_LINK(self, t):
        return t
    
    @regex(r"\]\*\(")
    def t_SLINK(self, t):
        return t

    @regex(r"\]")
    def t_RBRA(self, t):
        return t

    @regex(r"\(")
    def t_LPAR(self, t):
        return t

    @regex(r"\)")
    def t_RPAR(self, t):
        return t

    @regex(r"\_")
    def t_UNDER(self, t):
        return t

    @regex(r"\*")
    def t_AST(self, t):
        return t

    @regex(r"\~")
    def t_TILDE(self, t):
        return t
        
    @regex(r"\`")
    def t_TICK(self, t):
        return t

    @regex(r"\§([^\§\r\n]+)\§")
    def t_JAVASCRIPT(self, t):
        t.value = t.value[1:-1]
        return t

    @regex(r"[^\s\[\]\(\)\_\~\`\*]+")
    def t_WORD(self, t):
        return t

    @regex(r"[^\S\r\n]+")
    def t_SPACE(self, t):
        t.value = " "
        return t

    def t_error(self, t):
        if self.strict:
            target = self.source.getlex(t.lexpos)
            self.lexer_error(
                f"Unexpected token '{t.value[0]}'. [{self.lexer.current_state()}]",
                target=target,
            )
        else:
            t.type = 'WORD'
            return t