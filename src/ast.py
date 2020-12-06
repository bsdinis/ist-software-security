'''
ast.py

convert json to an AST
'''

from typing import Any, Optional, Dict, List, Set
from model import AccessPath, Pattern

from functools import reduce

import logging
VERBOSE = False
logging.basicConfig(format='%(module)s: %(funcName)s\t%(message)s')
logger = logging.getLogger(__name__)
logger.setLevel(level=logging.DEBUG if VERBOSE else logging.INFO)


class Node:
    @classmethod
    def from_json(cls, node_json: Dict[str, Any]):
        ''' convert json to node '''
        type = node_json['type']
        del(node_json['type'])
        name = None
        if 'name' in node_json:
            name = node_json['name']
            del(node_json['name'])

        children = dict()
        for tag, obj in node_json.items():
            assert tag not in children, 'Duplicate child: {}'.format(tag)
            if isinstance(obj, dict):
                children[tag] = cls.from_json(obj)
            elif isinstance(obj, list):
                children[tag] = [cls.from_json(o) for o in obj]
            elif isinstance(obj, str):
                children[tag] = obj
            elif isinstance(obj, int):
                children[tag] = obj
            elif isinstance(obj, bool):
                children[tag] = obj
            else:
                raise RuntimeError(
                    'Cannot parse child `{}` with type {}'.format(
                        tag, obj))

        return cls(type, name=name, children=children)

    def __init__(self,
                 type: str,
                 name: Optional[str] = None,
                 children: Dict[str,
                                Any] = dict()):
        self.type = type
        self.name = name
        self.children = children

    def __getitem__(self, key: str):
        ''' emulate dictionary '''
        return self.children[key]

    def __repr__(self) -> str:
        if self.type == 'AssignmentExpression':
            return '<{}: `{} = {}`>'.format(
                self.type, self['left'], self['right'])
        elif self.type == 'CallExpression':
            return '<{}: `{}({})`>'.format(
                self.type, self['callee'], ', '.join(
                    repr(a) for a in self['arguments']))
        elif self.type == 'MemberExpression':
            return '<{}: `{}`>'.format(self.type, str(list(self.get_rvalue_aps())[0]))

        return '<{}: `{}`>'.format(
            self.type,
            self.name) if self.name else '<{}>'.format(
            self.type)

    def ap(self) -> AccessPath:
        assert self.name is not None, 'Node {} has no name, thus it has no AccessPath'.format(
            self)
        return AccessPath.from_str(self.name)

    def get_aps(self) -> Set[AccessPath]:
        return self.get_rvalue_aps() | self.get_lvalue_aps()

    def get_lvalue_aps(self) -> Set[AccessPath]:
        if self.type in {'Identifier'}:
            return {self.ap()}
        elif self.type in {'AssignmentExpression'}:
            return self['left'].get_rvalue_aps()
        elif self.type in {'CallExpression'}:
            return self['callee'].get_rvalue_aps() | self.get_rvalue_aps()

        return set()

    def get_rvalue_aps(self) -> Set[AccessPath]:
        if self.type in {'Identifier'}:
            return {self.ap()}
        elif self.type in {'CallExpression'}:
            return reduce(lambda x, y: x | y, (expr.get_aps()
                                               for expr in self['arguments']), set())
        elif self.type in {'MemberExpression'}:
            left = self['object'].get_rvalue_aps()
            right = self['property'].get_rvalue_aps()
            if len(right) > 0:
                return set(l + r for l in left for r in right)
            else:
                return left

        elif self.type in {'UpdateExpression', 'UnaryExpression', 'SpreadElement'}:
            return self['argument'].get_rvalue_aps()
        elif self.type in {'BinaryExpression', 'LogicalExpression'}:
            return self['left'].get_rvalue_aps(
            ) | self['right'].get_rvalue_aps()
        elif self.type in {'ConditionalExpression'}:
            # TODO: implicit flows
            return self['consequent'].get_rvalue_aps(
            ) | self['alternate'].get_rvalue_aps()
        elif self.type in {'SequenceExpression'}:
            if len(self['expressions']) == 0:
                return set()
            else:
                return self['expressions'][0].get_rvalue_aps()

        return set()

    def get_tainted_sources(self,
                            tainted_aps: Dict[AccessPath,
                                              Set[AccessPath]],
                            pattern: Pattern) -> Set[AccessPath]:
        def ap_to_src_ap(ap: AccessPath,
                         tainted_aps: Dict[AccessPath,
                                           Set[AccessPath]],
                         pattern: Pattern) -> Set[AccessPath]:
            if ap in tainted_aps:
                return tainted_aps[ap]
            elif ap.is_potential_source(pattern):
                return {ap}
            return None

        logger.debug('involved aps [{}]: {}'.format(self, '\t'.join('({}, {})'.format(ap, ap.is_source(pattern)) for ap in self.get_rvalue_aps())))
        return reduce(
            lambda a, b: a | b, filter(
                lambda x: x is not None, map(
                    lambda y: ap_to_src_ap(
                        y, tainted_aps, pattern), self.get_rvalue_aps())), set())

    def is_sink(self, pattern: Pattern) -> bool:
        return any(ap.is_sink(pattern) for ap in self.get_lvalue_aps())


class AST:
    def __init__(self, root: Node):
        assert root.type == 'Program', 'Root must by `Program`, not {}'.format(
            root.type)
        self.root = root
        self.fdecls: Dict[str, Optional[Node]] = dict()

    @classmethod
    def from_json(cls, json_file: Dict[str, Any]):
        ''' convert json to ast '''
        root = Node.from_json(json_file)
        return cls(root)

    def find_fdecl(self, fname: str) -> Optional[Node]:
        if fname in self.fdecls:
            return self.fdecls[fname]

        def find(node: Node, name: str) -> Optional[Node]:
            if node.type in [
                'FunctionDeclaration',
                'FunctionExpression',
                    'ArrowFunctionExpression'] and node.name == name:
                return node

            for n in node.children.values():
                if not isinstance(n, Node):
                    continue

                a = find(n, name)
                if a is not None:
                    return a

            return None

        fdecl = find(self.root, fname)
        self.fdecls[fname] = fdecl
        return fdecl
