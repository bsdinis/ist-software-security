'''
ast.py

convert json to an AST
'''

from typing import Any, Optional, Dict, List
from models import Pattern, Graph

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


def taint_propagate(node: Node , pattern: Pattern, graph: Optional[Graph] = None, vulns: Optional[list] = []):

    if graph == None:
        graph = Graph()

    if node.type == "AssignmentExpression":
        (graph, id) = get_right_argument(node.children["right"], pattern, graph)
        graph = get_left_argument(node.children["left"], graph, id)

        print(graph.nodes)
        print(graph.abstractNodes)
    #elif node.type == "VariableDeclaration":
        #print(get_left_argument(node.children["id"], graph))
        #print(get_right_argument(node.children["init"], pattern, graph))
    else:
        for _, child in node.children.items():
            if isinstance(child, dict) or isinstance(child, Node):
                taint_propagate(child, pattern, graph, vulns)
            elif isinstance(child, list):
                for c in child:
                    taint_propagate(c, pattern, graph, vulns)

def get_left_argument(node: Node, graph: Graph, id: str):
    '''if node.type == "Identifier":
        if len(path) > 0:
            path = [node.name] + path
            return ".".join(path)
        else:
            return node.name
    elif node.type == "MemberExpression":
        path = [node.children["property"].name] + path
        return get_left_argument(node["object"])'''
    if node.type == "Identifier":
        graph.addNode(node.name, id)
        return graph



def get_right_argument(node: Node, pattern: Pattern, graph: Graph, parent: str = None):
    '''if node.type == "Identifier":
        if len(path) > 0:
            path = [node.name] + path
            pathStr = ".".join(path)
            return pathStr
        else:
            return node.name
    elif node.type == "Literal":
        return node.children["value"]
    elif node.type == "MemberExpression":
        path = [node.children["property"].name] + path
        return get_right_argument(node["object"], pattern, graph, path)'''

    if node.type == "Identifier":
        if parent != None:
            graph.addAbstractNode(parent + "." + node.name)
            graph.addMemberNode(node.name)
            return (graph, parent + "." + node.name)
        else:   
            graph.addAbstractNode(node.name)    
            graph.addNode(node.name)
            return (graph, node.name)
    elif node.type == "Literal":
        graph.addAbstractNode(node.children["raw"])
        return (graph, node.children["raw"])
    elif node.type == "MemberExpression":
        (graph, name) = get_right_argument(node.children["object"], pattern, graph)
        return get_right_argument(node.children["property"], pattern, graph, name)


        
        
    

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
        self.root.visit(taint_propagate, pattern)
        return []

