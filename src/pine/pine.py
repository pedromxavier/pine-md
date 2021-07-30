# Standard Library
import enum
from pathlib import Path

# Third-Party
from cstream import stderr, stdlog, stdwar, stdout

# Local
from .pinelib import Source
from .pineparser import PineParser, PineLexer
from .items import mdDocument, mdType, mdNull

class Pine(object):
    """
    """

    @classmethod
    def parse(cls, fname: str, strict: bool = True) -> mdDocument:
        """
        Parameters
        ----------
        fname: str
            Source code path
        """
        path = Path(fname).absolute()

        if not path.exists() or not path.is_file():
            if strict:
                stderr[0] << f"Error: Invalid source file path '{path}'."
                exit(1)
            else:
                stdwar[1] << f"Warning: Invalid source file path '{path}'."
                return mdNull()

        doc = PineParser.parse(Source(fname=path))

        if doc is None:
            return mdDocument()
        else:
            return doc

    @classmethod
    def tokens(cls, fname: str) -> str:
        path = Path(fname).absolute()

        if not path.exists() or not path.is_file():
            stderr[0] << f"Error: Invalid source file path '{path}'."
            return []
        
        lexer = PineLexer(Source(fname=path))
        
        return "\n".join(f"{i: 3d}. {t}" for i, t in enumerate(lexer.tokenize(), start=1))

# Very Important
mdType._add_pine(Pine)