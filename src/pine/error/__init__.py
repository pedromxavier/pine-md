""""""

from ..pinelib import TrackType, track, Source


class mdError(Exception):
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
                return (
                    f"In '{self.target.source.fpath}' at line {self.target.lineno}:\n"
                    f"{self.target.source.lines[self.target.lineno]}\n"
                    f"{' ' * self.target.chrpos}^\n"
                    f"{self.__class__.__doc__}: {self.msg}\n"
                )
        else:
            return self.msg


class mdSyntaxError(mdError):
    "Syntax Error"