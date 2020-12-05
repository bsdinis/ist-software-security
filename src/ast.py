'''
ast.py

convert json to an AST
'''

from typing import Any, Optional, Dict, List
from models import Pattern

def taint_propagate(node, spaces = ""):
   
    if (node.name == None):
        print(spaces + node.type),
    else:
        print(spaces + node.type + " " + node.name),
  
    for key,childs in node.children.items():
        if (isinstance(childs,dict)):
            taint_propagate(childs,spaces+" ")
        elif(isinstance(childs,list)):
            for child in childs:
                taint_propagate(child,spaces+" ")
        elif(isinstance(childs,Node)):
            taint_propagate(childs,spaces+" ")


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


    def visit(self, f) -> Any:
        f(self)

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
        vars = {}
        self.root.visit(taint_propagate)
        return []

