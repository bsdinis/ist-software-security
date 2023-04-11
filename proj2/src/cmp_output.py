#!/usr/bin/env python3

# cmp_output.py: compares two outputs of the tool
# prints diff


from model import Vulnerability  # type: ignore
from functools import reduce
from typing import Set
import argparse
import sys
import json


def cmp_solution(first, second, error_type: str, modifier: str):
    equal = True
    for vuln in first:
        same_vulns = list(filter(lambda x: x.vuln == vuln.vuln, second))
        if len(same_vulns) == 0:
            print(
                '[{}]: vulnerability {} is not present in {} solution\n{}'.format(
                    error_type,
                    vuln.vuln,
                    modifier,
                    vuln))
            equal = False
            continue

        present_srcs: Set[str] = reduce(
            lambda a, b: a | b, map(
                lambda x: set(
                    x.sources) & set(
                    vuln.sources), same_vulns), set())
        same_src = list(filter(lambda x: len(
            set(x.sources) & set(vuln.sources)) > 0, same_vulns))
        if len(set(vuln.sources)) > 0 and len(same_src) == 0:
            print(
                '[{}]: vulnerability {} with source in {} is not present in {} solution\n{}'.format(
                    error_type, vuln.vuln, set(
                        vuln.sources) - present_srcs, modifier, vuln))
            equal = False
            continue

        present_sinks: Set[str] = reduce(
            lambda a, b: a | b, map(
                lambda x: set(
                    x.sinks) & set(
                    vuln.sinks), same_src), set())
        same_sink = list(filter(lambda x: len(
            set(x.sinks) & set(vuln.sinks)) > 0, same_src))
        if len(set(vuln.sinks)) > 0 and len(same_sink) == 0:
            print('[{}]: vulnerability {} with source in {} and sink in {} is not present in {} solution\n{}'.format(
                error_type, vuln.vuln, present_srcs, set(vuln.sinks) - present_sinks, modifier, vuln))
            equal = False
            continue

        present_sanitizers: Set[str] = reduce(
            lambda a, b: a | b, map(
                lambda x: set(
                    x.sanitizers) & set(
                    vuln.sanitizers), same_src), set())
        same_sanitizer = list(filter(lambda x: len(
            set(x.sanitizers) & set(vuln.sanitizers)) > 0, same_sink))
        if len(set(vuln.sanitizers)) > 0 and len(same_sanitizer) == 0:
            print('[{}]: vulnerability {} with source in {} and sanitizer in {} is not present in {} solution\n{}'.format(
                error_type, vuln.vuln, present_sinks, set(vuln.sanitizers) - present_sanitizers, modifier, vuln))
            equal = False
            continue

    return equal


def main(baseline_fname: str, tentative_fname: str):
    with open(baseline_fname, 'r') as f:
        baseline = [Vulnerability.from_json(v) for v in json.load(f)]

    with open(tentative_fname, 'r') as f:
        tentative = [Vulnerability.from_json(v) for v in json.load(f)]

    equal = cmp_solution(
        baseline,
        tentative,
        'ERROR',
        'tentative') and cmp_solution(
        tentative,
        baseline,
        'WARNING',
        'baseline')

    return 0 if equal else 1


if __name__ == '__main__':
    assert len(sys.argv) == 3, 'argv: {}'.format(sys.argv)
    exit(main(sys.argv[1], sys.argv[2]))
