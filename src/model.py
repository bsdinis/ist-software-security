'''
model.py

'''

from typing import Any, Dict, List
import json

import logging
VERBOSE = True
logging.basicConfig(format='%(module)s: %(funcName)s\t%(message)s')
logger = logging.getLogger(__name__)
logger.setLevel(level=logging.DEBUG if VERBOSE else logging.INFO)

class Pattern:
    def __init__(self, pattern: Dict[str, Any]):
        self.vuln = pattern['vulnerability']
        self.sources = pattern['sources']
        self.sinks = pattern['sinks']
        self.sanitizers = pattern['sanitizers']

    def __repr__(self) -> str:
        return '<Pattern: {} ===> {} [ {} ]>'.format(self.sources, self.sinks, self.sanitizers)


class Vulnerability:
    def __init__(
            self,
            vuln: str,
            sources: List[str],
            sinks: List[str],
            sanitizers: List[str] = list()):
        self.vuln = vuln
        self.sources = sources
        self.sinks = sinks
        self.sanitizers = sanitizers

    @classmethod
    def from_json(cls, json: Dict[str, Any]):
        assert 'vulnerability' in json
        assert 'source' in json
        assert 'sink' in json
        assert len(json) in [3, 4]
        return cls(
            json['vulnerability'],
            json['source'],
            json['sink'],
            json['sanitizer'] if 'sanitizer' in json else list())

    def json(self):
        return {'vulnerability': self.vuln,
                'source': self.sources,
                'sink': self.sinks,
                'sanitizer': self.sanitizers}

    def __repr__(self) -> str:
        return json.dumps(self.json())


class AccessPath:
    # 5 is heuristic set by paper
    def __init__(self, var: str, field_idents: List[str], k: int = 5):
        self.var = var
        if len(field_idents) <= k:
            self.field_idents = tuple(field_idents)
        else:
            self.field_idents = tuple(field_idents[:k] + ['*'])

    @classmethod
    def from_str(cls, id: str):
        fields = id.strip().split('.')
        return cls(fields[0], fields[1:])

    def __hash__(self) -> int:
        return hash(self.var) ^ hash(self.field_idents)

    def __le__(self, other) -> bool:
        return self.var == other.var and len(self.field_idents) <= len(
            other.field_idents) and self.field_idents == other.field_idents[:len(self.field_idents)]

    def __eq__(self, other) -> bool:
        return self.var == other.var and self.field_idents == other.field_idents

    def __ne__(self, other) -> bool:
        return not (self == other)

    def __lt__(self, other) -> bool:
        return self <= other and not (self == other)

    def __gt__(self, other) -> bool:
        return not (self <= other)

    def __ge__(self, other) -> bool:
        return not(self == other) and not (self <= other)

    def is_sink(self, pattern: Pattern) -> bool:
        # TODO: fix
        # ```
        # a = document
        # is_sink(a.innerHTML, ...)
        # ```

        return any(self == AccessPath.from_str(s) for s in pattern.sinks)

    def is_potential_source(self, pattern: Pattern) -> bool:
        return any(self <= AccessPath.from_str(s) for s in pattern.sources)

    def is_source(self, pattern: Pattern) -> bool:
        return any(self == AccessPath.from_str(s) for s in pattern.sources)

    def __add__(self, other):
        return AccessPath(self.var, list(self.field_idents) +
                          [other.var] + list(other.field_idents))

    def __repr__(self) -> str:
        return '.'.join((self.var, ) + self.field_idents)
