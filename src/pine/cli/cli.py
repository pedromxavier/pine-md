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
    # parser.add_argument('-o', '--output', type=str, action="store", help="Output file path. Ensures HTML UTF-8 encoding.")
    # parser.add_argument('-v', '--verbose', type=int, choices=range(4), default=0, help="Output verbosity.")
    # parser.add_argument("--html", action="store_true", help="Ensures HTML output.")
    # parser.add_argument("--debug", action="store_true", help=argparse.SUPPRESS)
    parser.add_argument("--lex", action="store_true", help=argparse.SUPPRESS)
    # parser.add_argument("--tree", action="store_true", help=argparse.SUPPRESS)

    ## Parse Arguments
    args = parser.parse_args()

    pine = Pine(args.source)

    if args.lex:
        TOKENS = list(pine.tokens())
        print(f"Total: {len(TOKENS)} tokens.")
        print("\n".join(f"{k: 3d}. {t}" for k, t in enumerate(TOKENS, 1)))
    else:
        tree = pine.parse()
        if tree is not None:
            print(tree.html)
        else:
            stderr[0] << "No Output Generated."
        
