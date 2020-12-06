'''
analyzer.py

analyze a program
'''

from ast import AST, Node  # type: ignore
from callgraph import CallGraph  # type: ignore
from model import AccessPath, Pattern, Vulnerability  # type: ignore
from taint_map import TaintMap  # type: ignore


import json
from typing import Any, List, Optional, Dict, Set, Iterable
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


def gen_sanitized_vuln(
        pattern: Pattern,
        sanitized_aps: Set[AccessPath],
        sink_aps: Set[AccessPath]) -> Vulnerability:
    return Vulnerability(
        pattern.vuln, list(), [
            str(ap) for ap in sink_aps], [str(ap) for ap in sanitized_aps])


def taint_analysis(
        program: AST,
        pattern: Pattern) -> List[Vulnerability]:
    def analyze_node(
            cg_node: CallGraph.CGNode,
            pattern: Pattern) -> Set[Vulnerability]:
        def analyze_expr(
                stmt: Node,
                pattern: Pattern,
                taint_map: TaintMap,
                sanitized_map: TaintMap) -> Iterable[Vulnerability]:

            # a = sink(src)
            if stmt.type == 'AssignmentExpression':
                for a in analyze_expr(
                        stmt['right'],
                        pattern,
                        taint_map,
                        sanitized_map):
                    yield a
                for a in analyze_expr(
                        stmt['left'],
                        pattern,
                        taint_map,
                        sanitized_map):
                    yield a

                lvalue_aps = stmt['left'].get_lvalue_aps()
                usan_rvalue_aps = stmt['right'].get_usan_rvalue_aps(pattern)
                san_rvalue_aps = stmt['right'].get_san_rvalue_aps(pattern)
                sanitizers_aps = stmt['right'].get_rvalue_sanitizers(pattern)

                rvalue_aps = usan_rvalue_aps | san_rvalue_aps

                logger.debug(stmt)
                logger.debug(
                    '\tlvalue aps = {} (sink? {})'.format(
                        lvalue_aps, any(
                            a.is_sink(pattern) for a in lvalue_aps)))
                logger.debug(
                    '\trvalue aps = {} (tainted? {}\tsanitized? {})'.format(
                        rvalue_aps, any(
                            taint_map.is_tainted(a) for a in rvalue_aps), any(
                            sanitized_map.is_tainted(a) for a in rvalue_aps)))

                if len(rvalue_aps) > 0:
                    for ap in lvalue_aps:
                        taint_map.register_assignment(
                            ap, rvalue_aps, destructive=(
                                stmt['operator'] == '='))
                        sanitized_map.register_assignment(
                            ap, rvalue_aps, destructive=(stmt['operator'] == '='))

                    if stmt['operator'] == '=' or all(
                            not taint_map.is_tainted(lval) for lval in lvalue_aps):
                        if all(not taint_map.is_tainted(usan_rval)
                               for usan_rval in rvalue_aps):
                            for lval in lvalue_aps:
                                taint_map.pop_taint(lval)
                                sanitized_map.add_batch_taints(
                                    lval, sanitizers_aps)

                    source_aps = set(sum(map(lambda x: taint_map[x], filter(
                        lambda y: taint_map.is_tainted(y), lvalue_aps)), list()))
                    sanitized_aps = set(sum(map(lambda x: sanitized_map[x], filter(
                        lambda y: sanitized_map.is_tainted(y), lvalue_aps)), list()))
                    sink_aps = set(
                        filter(
                            lambda x: x.is_sink(pattern),
                            lvalue_aps))

                    if len(sink_aps) > 0 and len(source_aps) > 0:
                        yield gen_vuln(pattern, source_aps, sink_aps)
                    elif len(sanitized_aps) > 0:
                        if len(sink_aps) > 0:
                            yield gen_sanitized_vuln(pattern, sanitized_aps, sink_aps)

            elif stmt.type == 'CallExpression':
                # only consider one level call, ie: all arguments are
                # convertable to access paths or literals
                for arg in stmt['arguments']:
                    for a in analyze_expr(
                            arg, pattern, taint_map, sanitized_map):
                        yield a
                for a in analyze_expr(
                        stmt['callee'],
                        pattern,
                        taint_map,
                        sanitized_map):
                    yield a

                callee_aps = stmt['callee'].get_rvalue_aps()
                args_aps: Set[AccessPath] = reduce(
                    lambda a, b: a | b, (arg.get_rvalue_aps() for arg in stmt['arguments']), set())

                logger.debug(stmt)
                logger.debug(
                    '\tcallee aps = {} (source? {} sink? {} sanitizer? {})'.format(
                        callee_aps, any(
                            a.is_source(pattern) for a in callee_aps), any(
                            a.is_sink(pattern) for a in callee_aps), any(
                            a.is_sanitizer(pattern) for a in callee_aps)))
                for arg in args_aps:
                    logger.debug('\targ ap = {}  (source? {} sink? {} sanitizer? {})'.format(
                        arg, arg.is_source(pattern), arg.is_sink(pattern), arg.is_sanitizer(pattern)))

                sink_aps = set(
                    filter(
                        lambda x: x.is_sink(pattern),
                        callee_aps))
                source_aps = set(sum(map(lambda x: taint_map[x], filter(
                    lambda y: taint_map.is_tainted(y), args_aps)), list()))
                if len(sink_aps) > 0 and len(source_aps) > 0:
                    yield gen_vuln(pattern, source_aps, sink_aps)

        if cg_node.node is None:
            return set()

        taint_map = TaintMap(pattern.sources)
        sanitized_map = TaintMap(pattern.sanitizers)

        logger.debug('analyzing {}: {}'.format(cg_node.node, pattern))

        vulns: Set[Vulnerability] = set()
        stmts = cg_node.node['body']
        for stmt in stmts:
            if stmt.type != 'ExpressionStatement':
                continue

            stmt = stmt['expression']
            logger.debug('analyzing statement: {}'.format(stmt))
            for v in analyze_expr(stmt, pattern, taint_map, sanitized_map):
                vulns.add(v)

        return vulns

    cg = CallGraph(program)
    vulns: Set[Vulnerability] = reduce(
        lambda a, b: a | b, (analyze_node(
            node, pattern) for node in cg.nodes.values()), set())

    return [a for a in vulns]


def analyze(program: AST, patterns: List[Pattern]) -> List[Vulnerability]:
    vulns = []

    for p in patterns:
        vulns += taint_analysis(program, p)

    logger.debug('\n'.join(repr(v) for v in vulns))
    return vulns
