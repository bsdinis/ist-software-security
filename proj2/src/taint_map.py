'''
taint_map.py

organize taint maps
'''

from model import Pattern, AccessPath
from typing import Tuple, Dict, List, Set
from functools import reduce

import logging
VERBOSE = False
logging.basicConfig(format='%(module)s: %(funcName)s\t%(message)s')
logger = logging.getLogger(__name__)
logger.setLevel(level=logging.DEBUG if VERBOSE else logging.INFO)


class TaintMap:
    def __init__(self, sources: List[str], sanitizers: List[str]):
        self.taints: Dict[AccessPath, List[AccessPath]] = dict()
        self.sanitized: Dict[AccessPath,
                             List[Tuple[AccessPath, AccessPath]]] = dict()
        self.alias: Dict[AccessPath, List[AccessPath]] = dict()

        self.sources = [AccessPath.from_str(s) for s in sources]
        self.sanitizers = [AccessPath.from_str(s) for s in sanitizers]

        for s in self.sources:
            self.taints[s] = [s]
            self.sanitized[s] = []
            self.alias[s] = []
        for s in self.sanitizers:
            if s not in self.taints:
                self.taints[s] = []
                self.sanitized[s] = [s]
                self.alias[s] = []
            else:
                self.sanitized[s] += [s]

    @property
    def keys(self):
        assert self.taints.keys() == self.sanitized.keys() == self.alias.keys()
        return self.taints.keys()

    def is_tainted(self, ap: AccessPath) -> bool:
        return ap in self.keys and len(self.taints) > 0

    def is_sanitized(self, ap: AccessPath) -> bool:
        return ap in self.keys and len(self.taints) == 0

    def potentials(
            self,
            ap: AccessPath,
            l: List[AccessPath]) -> List[AccessPath]:
        return list(
            filter(
                lambda x: x in self.keys and any(
                    ap <= a for a in self.alias[x]),
                l))

    def create_alias(self, lval: AccessPath, rval: AccessPath) -> bool:
        rpotentials = self.potentials(rval, self.sources + self.sanitizers)
        lpotentials = self.potentials(lval, self.sources + self.sanitizers)
        if rval in self.keys:
            self.taints[lval], self.sanitized[lval], self.alias[lval] = self.taints[rval], self.sanitized[rval], self.alias[rval]
        elif rval in self.sources:
            self.taints[lval] = [rval]
            self.sanitized[lval] = []
            self.alias[lval] = []
        elif len(rpotentials) > 0:
            self.taints[lval] = []
            self.sanitized[lval] = []
            self.alias[lval] = rpotentials
        else:
            return False

        for p in lpotentials:
            if p in self.sources:
                self.sources.remove(p)
            if p in self.sanitizers:
                self.sanitizers.remove(p)

        return True

    def get_taints(self, rvals: List[AccessPath]) -> List[AccessPath]:
        prop_taints: Set[AccessPath] = reduce(lambda a, b: a | b, map(
            lambda x: set(self.taints[x]) if x in self.keys else set(), rvals), set())
        orig_taints: Set[AccessPath] = reduce(
            lambda a, b: a | b, map(
                lambda x: set(
                    self.potentials(
                        x, rvals)), self.sources), set())
        return list(prop_taints | orig_taints)

    def register_assignment(
            self,
            lval: AccessPath,
            usan_rval: List[AccessPath],
            san_rval: List[Tuple[AccessPath, AccessPath]],
            destructive: bool = True):

        rval = usan_rval + [x[0] for x in san_rval]
        logger.debug('{} = {} ({})'.format(lval, rval, destructive))

        if destructive:
            if len(rval) == 0:
                if lval in self.sources:
                    self.sources.remove(lval)
                if lval in self.sanitizers:
                    self.sanitizers.remove(lval)
                if lval in self.keys:
                    self.alias[lval] = []
                    self.taints[lval] = []
                    self.sanitized[lval] = []

            elif len(rval) == 1:
                if self.create_alias(lval, rval[0]):
                    return

        tainted = self.get_taints(usan_rval)
        possibly_tainted = self.get_taints(rval)
        if len(tainted) == 0 and (
                self.is_tainted(lval) or len(possibly_tainted) > 0):
            if lval not in self.keys:
                self.taints[lval] = list()
                self.sanitized[lval] = list()
                self.alias[lval] = list()

            for src, san in san_rval:
                logger.debug('{}'.format((src, san)))
                if src in self.taints:
                    for s in self.taints[src]:
                        self.sanitized[lval].append((s, san))
                elif src in self.sources:
                    self.sanitized[lval].append((src, san))

        elif len(tainted) > 0:
            if lval not in self.keys:
                self.taints[lval] = list()
                self.sanitized[lval] = list()
                self.alias[lval] = list()

            self.taints[lval] += tainted
            self.taints[lval] = list(set(self.taints[lval]))

        if destructive:
            potentials = self.potentials(lval, self.sources + self.sanitizers)
            for p in potentials:
                if p in self.sources:
                    self.sources.remove(p)
                if p in self.sanitizers:
                    self.sanitizers.remove(p)
