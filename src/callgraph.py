'''
callgraph.py
'''

from typing import Any, Dict, List, Set, Optional, Tuple, Iterable

from ast import Node, AST
from model import Pattern, Vulnerability

import logging
VERBOSE = True
logging.basicConfig(format='%(module)s: %(funcName)s\t%(message)s')
logger = logging.getLogger(__name__)
logger.setLevel(level=logging.DEBUG if VERBOSE else logging.INFO)


class CallGraph:
    class CGNode:
        def __init__(self, n: Optional[Node]):
            # tuples are cgnode, arguments
            self.node = n
            self.children: Set[Tuple[Any, Node]] = set()
            self.parents: Set[Any] = set()

        def add_child(self, n: Any, call_expr: Node):
            self.children.add((n, call_expr))
            n.add_parent(self)

        def add_parent(self, n: Any):
            self.parents.add(n)

    def __init__(self, ast: AST):
        self.nodes: Dict[str, CallGraph.CGNode] = dict()

        def construct_nodes(ast_node: Node) -> None:
            logger.debug(ast_node)
            if ast_node.type == 'Program':
                self.nodes[''] = CallGraph.CGNode(ast_node)
            elif ast_node.type in ['FunctionDeclaration', 'FunctionExpression', 'ArrowFunctionExpression']:
                self.nodes[ast_node.name] = CallGraph.CGNode(ast_node)

            for node in ast_node.children.values():
                if not isinstance(node, Node):
                    continue
                construct_nodes(node)

        def construct_cg(ast_node: Node) -> List[Node]:
            called_exprs: List[Node] = list()
            for c in ast_node.children.values():
                if isinstance(c, Node):
                    called_exprs += construct_cg(c)

            if ast_node.type == 'Program':
                node = self.nodes['']
            elif ast_node.type == 'CallExpression':
                fname = ast_node['callee'].name
                node = self.nodes[fname]

            if node is not None:
                for child in called_exprs:
                    fname = child['callee'].name
                    node.add_child(self.nodes[fname], child)
                return [ast_node]

            return called_exprs

        construct_nodes(ast.root)
        construct_cg(ast.root)
        self.root = self.nodes['']

    def traverse(self, f) -> Any:
        def visit(n: CallGraph.CGNode, f):
            returns = [f(n)]
            for c in f.children:
                returns += visit(c, f)

            return returns

        return visit(self.root, f)
