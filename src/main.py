#!/usr/bin/env python3

# main.py: running the tool

import argparse
import sys
import json

from ast import AST # type: ignore
from analyzer import analyze # type: ignore

def main(input_file: str, pattern_file: str):
    with open(input_file, 'r') as f:
        program = json.load(f)

    with open(pattern_file, 'r') as f:
        patterns = json.load(f)

    prog_tree = AST.from_json(program)
    vulns = analyze(prog_tree, patterns)

    output = input_file.split('.json')[0] + '.output.json'
    with open(output, 'w') as f:
        json.dump([v.json() for v in vulns], fp=f)


if __name__ == '__main__':
    assert len(sys.argv) == 3, 'argv: {}'.format(sys.argv)
    main(sys.argv[1], sys.argv[2])
