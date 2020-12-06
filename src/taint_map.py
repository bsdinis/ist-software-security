'''
taint_map.py

organize taint maps
'''

from model import Pattern, AccessPath
from typing import Tuple, Dict, List

import logging
VERBOSE = False
logging.basicConfig(format='%(module)s: %(funcName)s\t%(message)s')
logger = logging.getLogger(__name__)
logger.setLevel(level=logging.DEBUG if VERBOSE else logging.INFO)


class TaintMap:
    def __init__(self, original_taints: List[str]):
        self._map: Dict[AccessPath, List[AccessPath]] = dict()
        self._potential_map: Dict[AccessPath, List[AccessPath]] = dict()
        self.sources = original_taints
        for s in map(AccessPath.from_str, self.sources):
            self._map[s] = [s]
            self._potential_map[s] = []

    def __getitem__(self, ap: AccessPath) -> List[AccessPath]:
        return self._map[ap]

    def is_tainted(self, ap: AccessPath) -> bool:
        return ap in self._map

    def is_potential(self, ap: AccessPath) -> bool:
        return any(ap < a for a in self._map) or ap in self._potential_map

    def generate_tainted(self, rvals: List[AccessPath]) -> List[AccessPath]:
        tainted = list()
        for rval in rvals:
            if self.is_tainted(rval):
                tainted.append(rval)
            else:
                for p in rval.prefixes():
                    if self.is_tainted(p):
                        tainted.append(p)
                    elif self.is_potential(p):
                        suff = rval.rem_prefix(p)
                        if self.is_tainted(self._potential_map[p] + suff):
                            tainted.append(self._potential_map[p] + suff)

        return tainted

    def pop_taint(self,
                  ap: AccessPath) -> Tuple[List[AccessPath],
                                           List[AccessPath]]:
        if not self.is_tainted(ap):
            return list(), list()

        taint = self[ap]
        possible = self._potential_map[ap]
        del(self._map[ap])
        del(self._potential_map[ap])

        return taint, possible

    def register_assignment(
            self,
            lval: AccessPath,
            rval: List[AccessPath],
            destructive: bool = True):
        logger.debug('{} = {} ({})'.format(lval, rval, destructive))
        tainted_rvals = self.generate_tainted(rval)
        possible_rvals = list(filter(lambda x: self.is_potential(x), rval))

        if len(tainted_rvals) == 0:
            self.pop_taint(lval)

        if destructive or lval not in self._map:
            self._map[lval] = list()
            self._potential_map[lval] = list()

        for r in tainted_rvals:
            for tainted_src in self[r]:
                logger.debug('inserting {} -> {}'.format(lval, r))
                self._map[lval].append(tainted_src)

        for p in possible_rvals:
            for possible_src in self[p]:
                self._potential_map[lval].append(possible_src)

        if len(self._map[lval]) == 0:
            del(self._map[lval])
        if len(self._potential_map[lval]) == 0:
            del(self._potential_map[lval])

    def add_batch_taints(
            self,
            ap: AccessPath,
            sanitizers_aps: List[AccessPath]):
        if ap not in self._map:
            self._map[ap] = list()

        for s in sanitizers_aps:
            self._map[ap].append(ap)
