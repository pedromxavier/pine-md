
from pine.items.base import mdJavascript
from pine.items.html import mdHeader, mdLoader
from .parser import Parser
from .mdlexer import mdLexer
from ..items import mdItalic, mdBold, mdStrike, mdCode, mdText
from ..items import mdLink, mdSLink, mdLoader, mdHref

class mdParser(Parser):

    tabmodule = 'mdtab'

    precedence = [
        
        ('left', 'AST', 'TILDE', 'UNDER', 'TICK'),
        ('left', 'LBRA', 'RBRA', 'LOADER', 'RPAR'),
    ]

    # These lines are needed in subclasses
    _Lexer = mdLexer
    tokens = mdLexer.tokens
    
    def p_start(self, p):
        """ start : heading
                  | markdown
        """
        self.retrieve(p[1])

    def p_heading(self, p):
        """ heading : HEADING markdown """
        Heading = mdHeader.new(p[1])
        p[0] = Heading(p[2])

    def p_markdown(self, p):
        """ markdown : markdown fragment
                     | fragment
        """
        if len(p) == 3:
            p[1].append(p[2])
            p[0] = p[1]
        else:
            p[0] = mdText(p[1])

    def p_fragment(self, p):
        """ fragment : loader
                     | WORD
                     | SPACE
                     | italic
                     | bold
                     | strike
                     | code
        """
        p[0] = p[1]

    def p_loader(self, p):
        """ loader : href
                   | link
                   | slink
                   | content
        """
        p[0] = p[1]

    def p_href(self, p):
        """ href : LBRA markdown RBRA """
        p[0] = mdHref(p[2])

    def p_link(self, p):
        """ link : LBRA markdown LINK markdown RPAR """
        p[0] = mdLink(p[2], p[4])

    def p_slink(self, p):
        """ slink : LBRA markdown SLINK markdown RPAR """
        p[0] = mdSLink(p[2], p[4])

    def p_content(self, p):
        """ content : LBRA markdown LOADER """
        p[0] = mdLoader(str(p[2]), p[3])

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

    def p_javascript(self, p):
        """ fragment : JAVASCRIPT
        """
        p[0] = mdJavascript(p[1])