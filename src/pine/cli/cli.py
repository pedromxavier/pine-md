"""    
"""
import argparse
from pathlib import Path

from cstream import Stream, stdout, stderr

from .banner import PINE_BANNER
from ..pine import Pine
from ..error import PineError

stdpine = Stream(fg="GREEN", sty="DIM")

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
    parser.add_argument('-w', '--warn', action="store_true", help="Show warnings.")
    # parser.add_argument("--html", action="store_true", help="Ensures HTML output.")
    # parser.add_argument("--debug", action="store_true", help=argparse.SUPPRESS)
    parser.add_argument("--lex", action="store_true", help=argparse.SUPPRESS)
    # parser.add_argument("--tree", action="store_true", help=argparse.SUPPRESS)

    parser.set_defaults(func=None)

    ## Parse Arguments
    args = parser.parse_args()

    if args.func is not None:
        exit(args.func(args))

    if args.lex:
        stdout[0] << Pine.tokens(args.source)
        exit(0)

    pine = Pine.parse(args.source)

    if args.warn:
        Stream.set_lvl(1)
    else:
        Stream.set_lvl(0)

    if args.output is None:
        stdout[0] << pine.html
    else:
        output_path = Path(args.output).absolute()

        with output_path.open(mode='w', encoding='utf8') as file:
            file.write(pine.html)

    exit(0)
