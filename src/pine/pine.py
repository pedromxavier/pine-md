# Standard Library
from pathlib import Path

# Third-Party
from cstream import stderr, stdlog, stdwar, stdout

# Local
from .pinelib import Source
from .pineparser import PineParser

class Pine(object):
    """
    Parameters
    ----------
    fname: str
        Source code path
    """

    def __init__(self, fname: str):
        """"""
        self.fname = Path(fname).absolute()

        if not self.fname.exists() or not self.fname.is_file():
            stderr[0] << f"Invalid source file '{self.fname}'."
            exit(1)

        self.source = Source(fname=self.fname)    
        self.parser = PineParser(self.source)

    def parse(self) -> list:
        return self.parser.parse()

    def tokens(self) -> list:
        self.parser.lexer.lexer.input(self.source)
        return self.parser.lexer.tokenize()