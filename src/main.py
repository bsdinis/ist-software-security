#!/usr/bin/env python3

# main.py: running the tool

import argparse
import sys


def stub(a, b):
    output = a.split('.json')[0] + '.output.json'
    with open(output, 'w') as f:
        print('No vulnerabilities found (unimplemented)', file=f)


if __name__ == '__main__':
    assert len(sys.argv) == 3
    stub(sys.argv[1], sys.argv[2])
