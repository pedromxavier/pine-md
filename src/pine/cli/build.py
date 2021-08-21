import argparse

from ..items import mdPath

def build(args: argparse.Namespace):
    mdPath.set_root(args.path)