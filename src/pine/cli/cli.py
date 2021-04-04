"""    
"""
import argparse

from cstream import Stream, stdout, stdlog, stderr

from .banner import PINE_BANNER
from ..pine import pine

stdpine = Stream(fg="GREEN", sty="DIM")

class PineArgumentParser(argparse.ArgumentParser):

    def print_help(self, from_help: bool=True):
        if from_help: stdpine[0] << PINE_BANNER
        argparse.ArgumentParser.print_help(self, stdout[0])

    def error(self, message):
        stderr[0] << f"Command Error: {message}"
        self.print_help(from_help=False)
        exit(1)

def main() -> int:
    

    params = {"description": __doc__}
    
    parser = PineArgumentParser(**params)
    parser.add_argument("source", type=str, action="store", help="Source file.")
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--html", action="store_true", help="Ensures HTML output.")
    group.add_argument("--tokens", action="store_true", help=argparse.SUPPRESS)
    parser.add_argument("--debug", action="store_true", help=argparse.SUPPRESS)
    args = parser.parse_args()

    m = pine(args.source)

    if args.tokens:
        stdout[0] << m.tokens()
    else:
        stdout[0] << m.parse(ensure_html=args.html).html

    if args.debug:
        stdlog[0] << m.parser.symbol_table

    return 0