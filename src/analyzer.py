'''
analyzer.py

analyze a program
'''

from ast import AST # type: ignore

import json
from typing import Any, List, Optional, Dict

class Vulnerability:
    def __init__(self):
        pass # TODO

    def json(self):
        return {'vulnerability': 'TODO'}

    def __repr__(self) -> str:
        return json.dumps(self.json())


def analyze(program: AST, patterns: Any) -> List[Vulnerability]:
    return [Vulnerability()]
