""""""

from functools import total_ordering
from ..pinelib import TrackType


class PineError(Exception):
    "Error"

    def __init__(self, msg: str = None, target: TrackType = None, code: int = 1):
        Exception.__init__(self, msg)
        self.msg = str(msg) if msg is not None else ""
        self.code = code
        self.target = target

    def __str__(self):
        if self.target is not None and hasattr(self.target, "lexinfo"):
            if self.target.source is None:
                return f"{self.__class__.__doc__}: {self.msg}\n"
            else:
                return self.target.source.error(self.msg, name=self.__doc__)
        else:
            return self.msg


class PineSyntaxError(PineError):
    "Syntax Error"

class PineLexError(PineError):
    "Lex Error"