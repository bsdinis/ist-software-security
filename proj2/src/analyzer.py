'''
analyzer.py

analyze a program
'''

from ast import AST, Node  # type: ignore
from callgraph import CallGraph  # type: ignore
from model import AccessPath, Pattern, Vulnerability  # type: ignore
from taint_map import TaintMap  # type: ignore


import json
from typing import Any, List, Optional, Dict, Set, Iterable, Tuple
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
        source_aps: Set[AccessPath],
        sanitized_aps: Set[AccessPath],
        sink_aps: Set[AccessPath]) -> Vulnerability:
    return Vulnerability(
        pattern.vuln, [
            str(ap) for ap in source_aps], [
            str(ap) for ap in sink_aps], [
                str(ap) for ap in sanitized_aps])


def taint_analysis(
        program: AST,
        pattern: Pattern) -> List[Vulnerability]:
    def analyze_node(
            cg_node: CallGraph.CGNode,
            pattern: Pattern) -> Set[Vulnerability]:
        def analyze_expr(
                stmt: Node,
                pattern: Pattern,
                taint_map: TaintMap) -> Iterable[Vulnerability]:
            if stmt == None: return []

            if stmt.type == 'AssignmentExpression':
                for a in analyze_expr(
                        stmt['right'],
                        pattern,
                        taint_map):
                    yield a
                for a in analyze_expr(
                        stmt['left'],
                        pattern,
                        taint_map):
                    yield a

                lvalue_aps = stmt['left'].get_lvalue_aps()
                usan_rvalue_aps = stmt['right'].get_usan_rvalue_aps(pattern)
                san_rvalue_aps = stmt['right'].get_san_rvalue_aps(pattern)

                logger.debug(stmt)
                logger.debug(
                    '\tlvalue aps = {} (sink? {})'.format(
                        lvalue_aps, any(
                            a.is_sink(pattern) for a in lvalue_aps)))
                logger.debug(
                    '\tusan rvalue aps = {} (tainted? {}\tsanitized? {})'.format(
                        usan_rvalue_aps, any(
                            taint_map.is_tainted(a) for a in usan_rvalue_aps), any(
                            taint_map.is_sanitized(a) for a in usan_rvalue_aps)))

                for src, san in san_rvalue_aps:
                    logger.debug(
                        '\tsan rvalue aps = {}({}) (tainted? {})'.format(
                            san, src, taint_map.is_tainted(src)))

                for ap in lvalue_aps:
                    taint_map.register_assignment(ap, list(usan_rvalue_aps), list(
                        san_rvalue_aps), destructive=(stmt['operator'] == '='))

                source_aps = set(sum(map(lambda x: taint_map.taints[x], filter(
                    lambda y: taint_map.is_tainted(y), lvalue_aps)), list()))

                sink_aps = set(
                    filter(
                        lambda x: x.is_sink(pattern),
                        lvalue_aps))

                if len(sink_aps) > 0:
                    if len(source_aps) > 0:
                        yield gen_vuln(pattern, source_aps, sink_aps)
                    logger.debug('sanitized = {}'.format(taint_map.sanitized))
                    for src, san in set(sum((taint_map.sanitized[ap] if ap in taint_map.keys else [
                    ] for ap in lvalue_aps), list())):
                        yield gen_sanitized_vuln(pattern, {src}, {san}, sink_aps)

            elif stmt.type == 'CallExpression':
                # only consider one level call, ie: all arguments are
                # convertable to access paths or literals
                for arg in stmt['arguments']:
                    for a in analyze_expr(
                            arg, pattern, taint_map):
                        yield a
                for a in analyze_expr(
                        stmt['callee'],
                        pattern,
                        taint_map):
                    yield a

                callee_aps = stmt['callee'].get_rvalue_aps()
                usan_args_aps: Set[AccessPath] = reduce(
                    lambda a,
                    b: a | b,
                    (arg.get_usan_rvalue_aps(pattern) for arg in stmt['arguments']),
                    set())
                san_args_aps: Set[Tuple[AccessPath, AccessPath]] = reduce(
                    lambda a, b: a | b, (arg.get_san_rvalue_aps(pattern) for arg in stmt['arguments']), set())

                logger.debug(stmt)
                logger.debug(
                    '\tcallee aps = {} (source? {} sink? {} sanitizer? {})'.format(
                        callee_aps, any(
                            a.is_source(pattern) for a in callee_aps), any(
                            a.is_sink(pattern) for a in callee_aps), any(
                            a.is_sanitizer(pattern) for a in callee_aps)))

                for arg in usan_args_aps:
                    logger.debug('\targ ap = {}  (source? {} sink? {} sanitizer? {})'.format(
                        arg, arg.is_source(pattern), arg.is_sink(pattern), arg.is_sanitizer(pattern)))

                for arg, san in san_args_aps:
                    logger.debug(
                        '\tsanitized ({}) arg ap = {}  (source? {} sink? {})'.format(
                            san, arg, arg.is_source(pattern), arg.is_sink(pattern)))

                sink_aps = set(
                    filter(
                        lambda x: x.is_sink(pattern),
                        callee_aps))
                source_aps = set(sum(map(lambda x: taint_map.taints[x], filter(
                    lambda y: taint_map.is_tainted(y), usan_args_aps)), list()))
                if len(sink_aps) > 0:
                    if len(source_aps) > 0:
                        yield gen_vuln(pattern, source_aps, sink_aps)

                    logger.debug('sanitized = {}'.format(taint_map.sanitized))
                    logger.debug('HELP = {}'.format(set(sum(
                        (taint_map.sanitized[ap] if ap in taint_map.keys else [] for ap in usan_args_aps), list()))))
                    for src, san in set(sum((taint_map.sanitized[ap] if ap in taint_map.keys else [
                    ] for ap in usan_args_aps), list())):
                        yield gen_sanitized_vuln(pattern, {src}, {san}, sink_aps)

                    for src, san in san_args_aps:
                        if taint_map.is_tainted(src):
                            for s in taint_map.taints[src]:
                                yield gen_sanitized_vuln(pattern, {s}, {san}, sink_aps)

            elif stmt.type in {'ConditionalExpression'}:
                for a in analyze_expr(stmt['test'], pattern, taint_map):
                    yield a
                for a in analyze_expr(stmt['consequent'], pattern, taint_map):
                    yield a
                if 'alternate' in stmt.children:
                    for v in analyze_expr(stmt['alternate'], pattern, taint_map):
                        yield v

                #TODO implicit flows

            elif stmt.type in {'UpdateExpression', 'UnaryExpression', 'SpreadElement'}:
                for a in analyze_expr(stmt['argument'], pattern, taint_map):
                    yield a
            elif stmt.type in {'BinaryExpression', 'LogicalExpression'}:
                for a in analyze_expr(stmt['left'], pattern, taint_map):
                    yield a
                for a in analyze_expr(stmt['right'], pattern, taint_map):
                    yield a
            elif stmt.type in {'SequenceExpression'}:
                for expr in stmt['expressions']:
                    for a in analyze_expr(expr, pattern, taint_map):
                        yield a

        def analyze_stmt(
                stmt: Node,
                pattern: Pattern,
                taint_map: TaintMap) -> Iterable[Vulnerability]:
            if stmt == None: return []
            if stmt.type == 'BlockStatement':
                for s in stmt['body']:
                    if s.type not in ['ExpressionStatement', 'IfStatement', 'WhileStatement', 'BlockStatement']:
                        continue

                    if s.type == 'ExpressionStatement':
                        s = s['expression']
                        logger.debug('analyzing expression: {}'.format(s))
                        for v in analyze_expr(s, pattern, taint_map):
                            yield v
                    else:
                        logger.debug('analyzing expression: {}'.format(s))
                        for v in analyze_stmt(s, pattern, taint_map):
                            yield v
            elif stmt.type == 'IfStatement':
                for v in analyze_expr(stmt['test'], pattern, taint_map):
                    yield v
                for v in analyze_stmt(stmt['consequent'], pattern, taint_map):
                    yield v
                if 'alternate' in stmt.children:
                    for v in analyze_stmt(stmt['alternate'], pattern, taint_map):
                        yield v
                # missing implicit flow
            elif stmt.type == 'WhileStatement':
                for v in analyze_expr(stmt['test'], pattern, taint_map):
                    yield v
                for v in analyze_stmt(stmt['body'], pattern, taint_map):
                    yield v
                # missing implicit flow


        if cg_node.node is None:
            return set()

        taint_map = TaintMap(pattern.sources, pattern.sanitizers)

        logger.debug('analyzing {}: {}'.format(cg_node.node, pattern))

        vulns: Set[Vulnerability] = set()
        stmts = cg_node.node['body']
        for stmt in stmts:
            if stmt.type not in ['ExpressionStatement', 'IfStatement', 'WhileStatement', 'BlockStatement']:
                continue

            if stmt.type == 'ExpressionStatement':
                stmt = stmt['expression']
                logger.debug('analyzing expression: {}'.format(stmt))
                for v in analyze_expr(stmt, pattern, taint_map):
                    vulns.add(v)
            else:
                logger.debug('analyzing expression: {}'.format(stmt))
                for v in analyze_stmt(stmt, pattern, taint_map):
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
