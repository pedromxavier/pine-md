"""    
"""
import argparse
from pathlib import Path

from cstream import Stream, stdout, stdlog, stderr

from .banner import PINE_BANNER
from ..pine import pine

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

    global _output
    
    args: argparse.Namespace = parse()

    p = pine(args.source)

    if args.tokens:
        stdout[0] << p.tokens()
        exit(0)

    t = p.parse(ensure_html=args.html)

    output: str = t.html

    if args.output:
        path = Path(args.output)
        if not path.exists() or not path.is_file():
            stderr[0] << f"Invalid output file {path}"
            exit(1)
        with open(path, mode='w', encoding='utf-8') as file:
            file.write(output)
    else:
        stdout[0] << output

    if args.debug:
        stdlog[0] << t.tree
        stdlog[0] << p.parser.symbol_table

        while True:
            try:
                _output = ""
                s = input(">>> ")
                if not s:
                    break
                else:
                    exec(f"_output={s}", globals(), locals())
                    stdlog[0] << _output
            except Exception as err:
                stderr[0] << err.args

    exit(0)

def parse() -> argparse.Namespace:
    params = {"description": __doc__}
    
    parser = PineArgumentParser(**params)
    parser.add_argument("source", type=str, action="store", help="Source file.")

    parser.add_argument('-o', '--output', type=str, action="store", help="Output file path. Ensures HTML UTF-8 encoding.")

    group = parser.add_mutually_exclusive_group()
    group.add_argument("--html", action="store_true", help="Ensures HTML output.")
    group.add_argument("--tokens", action="store_true", help=argparse.SUPPRESS)
    parser.add_argument("--debug", action="store_true", help=argparse.SUPPRESS)
    
    return parser.parse_args()