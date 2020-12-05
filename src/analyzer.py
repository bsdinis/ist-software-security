'''
analyzer.py

analyze a program
'''

from ast import AST # type: ignore
from models import Pattern #type: ignore
import json
from typing import Any, List, Optional, Dict

class Vulnerability:
    def __init__(self, vuln: str, sources: List, sinks: List, sanitizers: List):
    	self.vuln = vuln
    	self.sources = sources
    	self.sinks = sinks
    	self.sanitizers = sanitizers

    def json(self):
        return {'vulnerability': self.vuln, 'source': self.sources, 'sink': self.sinks, 'sanitizers': self.sanitizers}

    def __repr__(self) -> str:
        return json.dumps(self.json())


def analyze(program: AST, patterns: dict) -> List[Vulnerability]:
	vulns = []
	vulns.append(Vulnerability("Test",[],[],[]))
	for vuln,pattern in patterns.items():
		found_vulns = program.taint_analysis(pattern)
		if (len(found_vulns) > 0):
			for found_vuln in found_vulns:
				vulns.append(Vulnerability(vuln,sources,sinks,sanitizers))

	return vulns


