# Standard Library
from pathlib import Path

# Third-Party
from cstream import stderr, stdlog, stdwar, stdout

# Local
from .pinelib import Source
from .pineparser import pineParser
from .pineparser.exparser import pineParser as expParser


class Pine(object):
    """
    Parameters
    ----------
    fname: str
        Source code path
    """

    def __init__(self, fname: str, *,  parser: str = None):
        """"""
        self.fname = Path(fname).absolute()

        if not self.fname.exists() or not self.fname.is_file():
            stderr[0] << f"Invalid source file '{self.fname}'."
            exit(1)

        self.source = Source(fname=self.fname)
            
        if parser == "EXPERIMENTAL":
            self.parser = expParser(self.source)
        else:
            self.parser = pineParser(self.source)

    def parse(self, *, ensure_html: bool=True):
        return self.parser.parse(ensure_html=ensure_html)

    def tokens(self):
        return self.parser.test()