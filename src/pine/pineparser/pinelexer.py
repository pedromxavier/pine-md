from .lexer import Lexer, regex
from ..pinelib import Source


class PineLexer(Lexer):

    states = [
        ("div", "exclusive"),
        ("mdfancy", "exclusive"),
        ("markdown", "exclusive"),
        ("javascript", "exclusive"),
        ("codeblock", "exclusive"),
        ("loader", "exclusive"),
    ]

    tokens = (
        "LBRA",
        "RBRA",
        "LPAR",
        "RPAR",
        "HREF",
        "AST",
        "UNDER",
        "TILDE",
        "TICK",
        "INDENT",
        "ENDL",
        "HEADING",
        "LOADER",
        "LINK",
        "SLINK",
        "WORD",
        "OLIST",
        "ULIST",
        "JSPUSH",
        "JSPULL",
        "JSCODE",
        "DIVPUSH",
        "DIVNAME",
        "DIVCLASS",
        "DIVID",
        "DIVPULL",
        "SPACE",
        "CBPUSH",
        "CBPULL",
        "CBCODE",
    )

    @regex(r"^\#[^\r\n]*[\r\n]?")
    def t_INITIAL_COMMENT(self, t):
        self.lexer.lineno += t.value.count("\n")
        return None

    @regex(r"^[\t\ ]+")
    def t_INITIAL_INDENT(self, t):
        t.value = t.value.count("\t") * self.TAB_SIZE + t.value.count(" ")
        if t.value % self.TAB_SIZE:
            self.lexer_error("Inconsistent indentation.")
        else:
            t.value //= self.TAB_SIZE
            self.lexer.begin("mdfancy")
        return t

    @regex(r"\{")
    def t_mdfancy_DIVPUSH(self, t):
        self.lexer.begin("div")
        return t

    @regex(r"[a-zA-Z][a-zA-Z0-9\-]+")
    def t_div_DIVNAME(self, t):
        return t

    @regex(r"\.[a-zA-Z][a-zA-Z0-9\-]+")
    def t_div_DIVCLASS(self, t):
        return t

    @regex(r"\.[a-zA-Z][a-zA-Z0-9\-]+")
    def t_div_DIVID(self, t):
        return t

    @regex(r"\}")
    def t_mdfancy_DIVPULL(self, t):
        return t

    @regex(r"\#[1-6]")
    def t_mdfancy_HEADING(self, t):
        return t

    @regex(r"\+")
    def t_mdfancy_OLIST(self, t):
        self.lexer.begin("markdown")
        return t

    @regex(r"\-")
    def t_mdfancy_ULIST(self, t):
        self.lexer.begin("markdown")
        return t

    @regex(r"\[")
    def t_mdfancy_LBRA(self, t):
        self.lexer.begin("loader")
        return t

    @regex(r"[^\[\]\r\n]+")
    def t_loader_HREF(self, t):
        return t

    @regex(r"\]\@[a-z]+")
    def t_loader_LOADER(self, t):
        t.value = t.value[2:]
        self.lexer.begin("markdown")
        return t

    @regex(r"\]\(")
    def t_loader_LINK(self, t):
        self.lexer.begin("markdown")
        return t
    
    @regex(r"\]\*\(")
    def t_loader_SLINK(self, t):
        self.lexer.begin("markdown")
        return t

    @regex(r"\]")
    def t_loader_RBRA(self, t):
        self.lexer.begin("markdown")
        return t

    @regex(r"\(")
    def t_markdown_mdfancy_LPAR(self, t):
        return t

    @regex(r"\)")
    def t_markdown_mdfancy_RPAR(self, t):
        return t

    @regex(r"\_")
    def t_markdown_mdfancy_UNDER(self, t):
        return t

    @regex(r"\*")
    def t_markdown_mdfancy_AST(self, t):
        return t

    @regex(r"\~")
    def t_markdown_mdfancy_TILDE(self, t):
        return t

    @regex(r"\`\`\`[a-z]*\n")
    def t_mdfancy_CBPUSH(self, t):
        self.lexer.begin("codeblock")
        t.value = t.value[3:-2]
        return t

    @regex(r"[^\`]")
    def t_codeblock_CBCODE(self, t):
        return t

    @regex(r"\`\`\`\n?")
    def t_codeblock_CBPULL(self, t):
        self.lexer.begin("INITIAL")
        return t

    @regex(r"\`")
    def t_markdown_mdfancy_TICK(self, t):
        return t

    @regex(r"\§")
    def t_markdown_mdfancy_JSPUSH(self, t):
        self.lexer.begin("javascript")
        return t

    @regex(r"[^\S\r\n]*\n+")
    def t_javascript_ENDL(self, t):
        self.lexer.lineno += t.value.count("\n")
        return None

    @regex(r"[^\§]+")
    def t_javascript_JSCODE(self, t):
        return t

    @regex(r"\§")
    def t_javascript_JSPULL(self, t):
        self.lexer.begin("markdown")
        return t

    @regex(r"[^\s\§\r\n\{\}\[\]\(\)\_\*\~\`\-\+\#]+")
    def t_mdfancy_WORD(self, t):
        self.lexer.begin("markdown")
        return t

    @regex(r"[^\s\§\r\n\{\}\[\]\(\)\_\*\~\`]+")
    def t_markdown_WORD(self, t):
        self.lexer.begin("markdown")
        return t

    @regex(r"[^\S\r\n]*\n+")
    def t_ANY_ENDL(self, t):
        t.value = t.value.count("\n")
        self.lexer.lineno += t.value
        self.lexer.begin("INITIAL")
        return t

    @regex(r"[^\S\r\n]+")
    def t_ANY_SPACE(self, t):
        t.value = " "
        return t

    def t_ANY_error(self, t):
        target = self.source.lexchr(t.lexpos)
        self.lexer_error(
            f"Unexpected token '{t.value[0]}'. [{self.lexer.current_state()}]",
            target=target,
        )
