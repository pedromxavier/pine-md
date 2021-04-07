## Standard Library
import os
import itertools as it
from pathlib import Path
from functools import wraps


class EOFType(object):
    def __init__(self, lexinfo: dict):
        ## Add tracking information
        self.lineno = lexinfo["lineno"]
        self.lexpos = lexinfo["lexpos"]
        self.chrpos = lexinfo["chrpos"]
        self.source = lexinfo["source"]

        self.lexinfo = lexinfo


class Source(str):
    """This source code object aids the tracking of tokens in order to
    indicate error position on exception handling.
    """

    def __new__(cls, *, fname: str = None, buffer: str = None):
        """This object is a string itself with additional features for
        position tracking.
        """
        if fname is not None and buffer is not None:
            raise ValueError("Can't work with both 'fname' and 'buffer' parameters.")

        elif fname is not None:
            if not isinstance(fname, (str, Path)):
                raise TypeError(
                    f"Invalid type '{type(fname)}' for 'fname'. Must be 'str' or 'Path'."
                )

            fpath = Path(fname)

            if not fpath.exists() or not fpath.is_file():
                raise FileNotFoundError(f"Invalid file path '{fname}'.")

            with open(fpath, mode="r", encoding="utf-8") as file:
                return super(Source, cls).__new__(cls, file.read())

        elif buffer is not None:
            if not isinstance(buffer, str):
                raise TypeError(
                    f"Invalid type '{type(buffer)}' for 'buffer'. Must be 'str'."
                )

            return super(Source, cls).__new__(cls, buffer)
        else:
            raise ValueError("Either 'fname' or 'buffer' must be provided.")

    def __init__(self, *, fname: str = None, buffer: str = None):
        """Separates the source code in multiple lines. A blank first line is added for the indexing to start at 1 instead of 0. `self.table` keeps track of the (cumulative) character count."""
        self.fpath = Path(fname).absolute() if (fname is not None) else "<string>"
        self.lines = [""] + self.split("\n")
        self.table = list(it.accumulate([(len(line) + 1) for line in self.lines]))

    def __repr__(self):
        return f"Source @ '{self.fpath}'"

    def __bool__(self):
        """Truth-value for emptiness checking."""
        return self.__len__() > 0

    @property
    def eof(self):
        """Virtual object to represent the End-of-File for the given source
        object. It's an anonymously created EOFType instance.
        """

        ## SatType lexinfo interface
        lineno = len(self.lines) - 1
        lexpos = len(self.lines[lineno]) - 1
        chrpos = lexpos - self.table[lineno - 1] + 1

        lexinfo = {"lineno": lineno, "lexpos": lexpos, "chrpos": chrpos, "source": self}

        ## Anonymous object
        return EOFType(lexinfo)


def trackable(cls: type):

    init_func = cls.__init__

    @wraps(init_func)
    def __init__(self, *args, **kwargs):
        init_func(self, *args, **kwargs)
        setattr(
            self, "lexinfo", {"lineno": 0, "lexpos": 0, "chrpos": 0, "source": None}
        )

    setattr(cls, "__init__", __init__)

    setattr(cls, "lineno", property(lambda self: getattr(self, "lexinfo")["lineno"]))
    setattr(cls, "lexpos", property(lambda self: getattr(self, "lexinfo")["lexpos"]))
    setattr(cls, "chrpos", property(lambda self: getattr(self, "lexinfo")["chrpos"]))
    setattr(cls, "source", property(lambda self: getattr(self, "lexinfo")["source"]))

    return cls


def track(from_: object, to_: object, out: bool = False):
    if hasattr(from_, "lexinfo"):
        if hasattr(to_, "lexinfo"):
            to_.lexinfo.update(from_.lexinfo)
            if out:
                return to_
        else:
            raise AttributeError(
                "`to_` is not trackable, i.e. has no attribute `lexinfo`."
            )
    else:
        raise AttributeError(
            "`from_` is not trackable, i.e. has no attribute `lexinfo`."
        )


@trackable
class TrackType(object):
    pass


__all__ = ["Source", "track", "trackable", "TrackType"]