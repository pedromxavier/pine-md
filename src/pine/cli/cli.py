"""    
"""
import argparse
from pathlib import Path

from cstream import Stream, stdout, stdlog, stderr

from .banner import PINE_BANNER
from ..pine import Pine
from ..pinelib.repl import repl

stdpine = Stream(fg="GREEN", sty="DIM")

_output = ""

class PineArgumentParser(argparse.ArgumentParser):

    def print_help(self, from_help: bool=True):
        if from_help: stdpine[0] << PINE_BANNER
        argparse.ArgumentParser.print_help(self, stdout[0])

    def error(self, message):
        stderr[0] << f"Command Error: {message}"
        self.print_help(from_help=False)
        exit(1)

def main():
    """"""

    ## Argument Parser Definition
    params = {"description": __doc__}
    
    parser = PineArgumentParser(**params)
    parser.add_argument("source", type=str, action="store", help="Source file.")
    parser.add_argument('-o', '--output', type=str, action="store", help="Output file path. Ensures HTML UTF-8 encoding.")
    parser.add_argument('-v', '--verbose', type=int, choices=range(4), default=0, help="Output verbosity.")
    parser.add_argument("--html", action="store_true", help="Ensures HTML output.")
    parser.add_argument("--debug", action="store_true", help=argparse.SUPPRESS)
    parser.add_argument("--exp", action="store_true", help=argparse.SUPPRESS)
    
    ## Parse Arguments
    args = parser.parse_args()

    if args.debug:
        Stream.set_lvl(3)
    else:
        Stream.set_lvl(args.verbose)

    path = Path(args.source)

    if not path.exists() or not path.is_file():
        stderr[0] << f"Invalid File Path: '{args.source}'."
        exit(1)

    if args.exp:
        pine = Pine(path, parser="EXPERIMENTAL")
        try:
            html = pine.parse()
        except SyntaxError:
            stderr[0] << "Syntax Error"
            html = None
    else:
        pine = Pine(path)
        tree = pine.parse(ensure_html=args.html)

        html: str = tree.html

    if args.output:
        path = Path(args.output)
        if not path.exists() or not path.is_file():
            stderr[0] << f"Invalid output file '{path}'."
            exit(1)
        with open(path, mode='w', encoding='utf-8') as file:
            file.write(html)
    else:
        stdout[0] << html

    if args.debug:
        repl(globals(), locals())

    exit(0)