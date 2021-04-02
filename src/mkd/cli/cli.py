""" md: A Markdown pill
"""
import argparse

from cstream import stdout, stdlog

from ..mkd import mkd


def main() -> int:
    params = {"description": __doc__}

    parser = argparse.ArgumentParser(**params)
    parser.add_argument("source", type=str, action="store", help="source .md file.")
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--html", action="store_true", help="Ensures HTML output.")
    group.add_argument("--tokens", action="store_true", help=argparse.SUPPRESS)
    
    parser.add_argument("--debug", action="store_true", help=argparse.SUPPRESS)
    args = parser.parse_args()

    m = mkd(args.source)

    if args.tokens:
        stdout[0] << m.tokens()
    else:
        stdout[0] << m.parse(ensure_html=args.html).html

    if args.debug:
        stdlog[0] << m.parser.symbol_table

    return 0