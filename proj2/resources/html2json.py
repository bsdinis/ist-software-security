#!/usr/bin/env python3
'''
html2js.py

extract javascript scripts from html
convert immediately to esprima format
'''

from typing import Any, Dict
import esprima # type: ignore
import sys
import json

def extract(html_file: str) -> str:
    html_file = html_file.replace('<SCRIPT>', '<script>').replace('</SCRIPT>', '</script>')
    scripts = [ a.split('</script>')[0].strip() for a in html_file.split('<script>')[1:] ]
    unified = '\n'.join(scripts)
    return json.dumps(esprima.parseScript(unified).toDict())

if __name__ == '__main__':
    nargs = len(sys.argv)
    if nargs == 1: # read from stdin, write to stdout
        html = sys.stdin.read()
        print(extract(html))
    elif nargs in [2, 3]: # read from file
        with open(sys.argv[1], 'r') as f:
            ast = extract(f.read())

        if nargs == 2: # write to file with ext switched
            output_split = sys.argv[1].strip().split('.html')
            if len(output_split) == 1:
                output = ''.join(output_split) + '.json'
            else:
                output = ''.join(output_split[:-1]) + '.json'
        else:
            output = sys.argv[2].strip()

        with open(output, 'w') as f:
            print(ast, file=f)
