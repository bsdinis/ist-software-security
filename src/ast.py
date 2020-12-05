'''
ast.py

convert json to an AST
'''

from typing import Any, Optional, Dict, List
from models import Pattern

class Node:
    def __init__(self, type: str, name: Optional[str] = None, children: Dict[str, Any] = dict()):
        self.type = type
        self.name = name
        self.children = children

    def __getitem__(self, key: str):
        ''' emulate dictionary '''
        return self.children[key]

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
                raise RuntimeError('Cannot parse child `{}` with type {}'.format(tag, obj))

        return cls(type, name=name, children=children)


    def visit(self, f, pattern) -> Any:
        return f(self,pattern)


def taint_propagate(node: Node , pattern: Pattern, spaces: Optional[str] = "", vars: Optional[dict] = {}, funcs: Optional[dict] = {}, vulns: Optional[list] = []):
   
    if (node.name == None):
        print(spaces + node.type)
    else:
        print(spaces + node.type + " " + node.name)

    if node.type == "AssignmentExpression":
        left = get_left_argument(node.children["left"])
        right = get_right_argument(node.children["right"], pattern, vars=vars)

        if right[1]:
            vars[left] = {
                'tainted': True,
                'source': right[0]
            }
        else:
            vars[left] = { 'tainted': False }
        print(left)
        print(right)
    elif node.type == "VariableDeclaration":
        print(get_left_argument(node.children["id"]))
        print(get_right_argument(node.children["init"], pattern, vars=vars))
    else:
        for _, child in node.children.items():
            if isinstance(child, dict):
                taint_propagate(child, pattern, spaces + " ", vars, funcs, vulns)
            elif isinstance(child, list):
                for c in child:
                    taint_propagate(c, pattern, spaces + " ", vars, funcs, vulns)
            elif isinstance(child, Node):
                taint_propagate(child, pattern, spaces + " ", vars, funcs, vulns)
      
def get_left_argument(node: Node, path: list = []):
    if node.type == "Identifier":
        if len(path) > 0:
            path = [node.name] + path
            return ".".join(path)
        else:
            return node.name
    elif node.type == "MemberExpression":
        path = [node.children["property"].name] + path
        return get_left_argument(node["object"], path)

def get_right_argument(node: Node, pattern: Pattern, path: list = [], vars: dict = {}, tainted: bool = False):
    if node.type == "Identifier":
        if len(path) > 0:
            path = [node.name] + path
            pathStr = ".".join(path)
            isTainted = tainted or pathStr in pattern.getSources() or pathStr in vars and vars[pathStr]['tainted']
            return (pathStr, isTainted)
        else:
            return node.name
    elif node.type == "Literal":
        return (node.children["value"], False)
    elif node.type == "MemberExpression":
        if not tainted and path in pattern.getSources():
            tainted = True
        path = [node.children["property"].name] + path
        return get_right_argument(node["object"], pattern, path, vars, tainted)
        
        
    

class AST:
    def __init__(self, root: Node):
        assert root.type == 'Program', 'Root must by `Program`, not {}'.format(root.type)
        self.root = root

    @classmethod
    def from_json(cls, json_file: Dict[str, Any]):
        ''' convert json to ast '''
        root = Node.from_json(json_file)
        return cls(root)

    
    def taint_analysis(self, pattern: Pattern) -> List:
        ''' detect all ilegal flows with a specific Pattern'''
        self.root.visit(taint_propagate,pattern)
        return []

