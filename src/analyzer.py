'''
analyzer.py

analyze a program
'''

from ast import AST  # type: ignore
from callgraph import CallGraph  # type: ignore
from model import AccessPath, Pattern, Vulnerability  # type: ignore
import json
from typing import Any, List, Optional, Dict, Set
from functools import reduce

import logging
VERBOSE = True
logging.basicConfig(format='%(module)s: %(funcName)s\t%(message)s')
logger = logging.getLogger(__name__)
logger.setLevel(level=logging.DEBUG if VERBOSE else logging.INFO)


def gen_vuln(
        pattern: Pattern,
        source_aps: Set[AccessPath],
        sink_aps: Set[AccessPath]) -> Vulnerability:
    return Vulnerability(
        pattern.vuln, [
            str(ap) for ap in source_aps], [
            str(ap) for ap in sink_aps])


def basic_taint_analysis(
        program: AST,
        pattern: Pattern) -> List[Vulnerability]:
    def analyze_node(
            cg_node: CallGraph.CGNode,
            pattern: Pattern) -> Set[Vulnerability]:
        tainted_aps: Dict[AccessPath, Set[AccessPath]] = dict()
        if cg_node.node is None:
            return set()

        logger.debug('analyzing {}: {}'.format(cg_node.node, pattern))

        vulns: Set[Vulnerability] = set()
        stmts = cg_node.node['body']
        for stmt in stmts:
            if stmt.type != 'ExpressionStatement':
                continue

            stmt = stmt['expression']

            if stmt.type == 'AssignmentExpression':
                lvalue_aps = stmt['left'].get_lvalue_aps()
                rvalue_aps = stmt['right'].get_tainted_sources(
                    tainted_aps, pattern)

                logger.debug(stmt)
                logger.debug(
                    '\tlvalue aps = {} (sink? {})'.format(
                        lvalue_aps, any(
                            a.is_sink(pattern) for a in lvalue_aps)))
                logger.debug('\trvalue aps = {}'.format(str(rvalue_aps)))

                if len(rvalue_aps) > 0:
                    for ap in lvalue_aps:
                        tainted_aps[ap] = rvalue_aps

                    source_aps = set(
                        filter(
                            lambda x: x.is_source(pattern),
                            rvalue_aps))
                    sink_aps = set(filter(
                        lambda x: x.is_sink(pattern),
                        lvalue_aps))

                    if len(sink_aps) > 0 and len(source_aps) > 0:
                        vulns.add(gen_vuln(pattern, source_aps, sink_aps))
                else:
                    for ap in lvalue_aps:
                        if ap in tainted_aps:
                            del(tainted_aps[ap])

            elif stmt.type == 'CallExpression':
                # only consider one level call, ie: all arguments are
                # convertable to access paths or literals
                callee_aps = stmt['callee'].get_rvalue_aps()
                source_aps = set(
                    filter(
                        lambda x: x.is_source(pattern),
                        reduce(
                            lambda a,
                            b: a | b,
                            (arg.get_tainted_sources(
                                tainted_aps,
                                pattern) for arg in stmt['arguments']),
                            set())))

                logger.debug(stmt)
                logger.debug(
                    '\tcallee aps = {} (sink? {})'.format(
                        callee_aps, any(
                            a.is_sink(pattern) for a in callee_aps)))
                logger.debug('\tsource aps = {}'.format(str(source_aps)))

                sink_aps = set(filter(
                    lambda x: x.is_sink(pattern),
                    callee_aps))
                if len(sink_aps) > 0 and len(source_aps) > 0:
                    vulns.add(
                        gen_vuln(
                            pattern,
                            source_aps,
                            sink_aps))

        return vulns

    cg = CallGraph(program)
    vulns: Set[Vulnerability] = reduce(
        lambda a, b: a | b, (analyze_node(
            node, pattern) for node in cg.nodes.values()), set())

    return [a for a in vulns]


def analyze(program: AST, patterns: List[Pattern]) -> List[Vulnerability]:
    vulns = []

    for p in patterns:
        vulns += basic_taint_analysis(program, p)

    logger.debug('\n'.join(repr(v) for v in vulns))
    return vulns
