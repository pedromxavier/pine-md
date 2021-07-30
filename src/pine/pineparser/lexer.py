import re
from ply import lex
from cstream import stderr

# Local
from ..error import PineLexError, PineError
from ..pinelib import TrackType, Source


def regex(pattern: str):
    def decor(callback):
        callback.__doc__ = pattern
        return callback

    return decor


class Lexer(object):

    TAB_SIZE = 4
    RE_FLAGS = re.VERBOSE | re.UNICODE | re.MULTILINE

    tokens = ()

    def __init__(self, source: Source):
        self.source = source
        self.lexer = lex.lex(module=self, reflags=self.RE_FLAGS)

    def tokenize(self) -> list:
        self.lexer.input(self.source)
        tokens = []
        while True:
            tok = self.lexer.token()
            if tok:
                tokens.append(f"[{self.lexer.current_state()}] {tok}")
            else:
                return tokens

    def lexer_error(self, msg: str, target: TrackType = None, code: int = 1):
        raise PineLexError(msg=msg, target=target, code=code)

    # -- LEX --
    def t_ANY_error(self, t):
        target = self.source.getlex(t.lexpos)
        self.lexer_error(f"Unexpected token '{t.value[0]}'.", target=target)