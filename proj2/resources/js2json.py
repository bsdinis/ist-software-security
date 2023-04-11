#!/usr/bin/env python3
'''
js2json.py

convert javascript to json
'''

import esprima # type: ignore
import sys
import json

def extract(js_file: str) -> str:
    return json.dumps(esprima.parseScript(js_file).toDict())

if __name__ == '__main__':
    nargs = len(sys.argv)
    if nargs == 1: # read from stdin, write to stdout
        js = sys.stdin.read()
        print(extract(js))
    elif nargs in [2, 3]: # read from file
        with open(sys.argv[1], 'r') as f:
            ast = extract(f.read())

        if nargs == 2: # write to file with ext switched
            output_split = sys.argv[1].strip().split('.js')
            if len(output_split) == 1:
                output = ''.join(output_split) + '.json'
            else:
                output = ''.join(output_split[:-1]) + '.json'
        else:
            output = sys.argv[2].strip()

        with open(output, 'w') as f:
            print(ast, file=f)
