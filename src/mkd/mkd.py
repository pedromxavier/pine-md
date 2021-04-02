# Standard Library
from pathlib import Path

# Third-Party
from cstream import stderr, stdlog, stdwar, stdout

# Local
from .mkdlib import Source
from .mkdparser import mkdParser


class mkd:
    """"""

    def __init__(self, fname: str):
        """"""
        self.fname = Path(fname).absolute()

        if not self.fname.exists() or not self.fname.is_file():
            stderr[0] << f"Invalid source file '{self.fname}'."
            exit(1)

        self.source = Source(self.fname)
        self.parser = mkdParser(self.source)

    def parse(self, *, ensure_html: bool=True):
        return self.parser.parse(ensure_html=ensure_html)

    def tokens(self):
        return self.parser.test()