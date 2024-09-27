
from typing import List

from enum import Enum

class NodeKind(Enum):
    TranslationUnit = 1
    Preamble = 2
    PackageHeader = 3
    ImportList = 4
    TopLevelObject = 5
    ClassDefinition = 6
    FunctionDefinition = 7
    VariableDeclaration = 8
    EnumDefinition = 9
    StructDefinition = 10

class Node(object):
    def __init__(self, kind: NodeKind, token_start: int, token_end: int):
        self._kind = kind
        self._children = []
        self._token_start: int = token_start
        self._token_end: int = token_end
        

    def __iter__(self):
        return walk_tree(self)

    def filter(self, pattern):
        for path, node in self:
            if ((isinstance(pattern, type) and isinstance(node, pattern)) or
                (node == pattern)):
                yield path, node
    @property
    def children(self) -> List["Node"]:
        return self._children

def walk_tree(root: Node):
    children = None

    if isinstance(root, Node):
        yield (), root
        children = root.children
    else:
        children = root

    for child in children:
        if isinstance(child, (Node, list, tuple)):
            for path, node in walk_tree(child):
                yield (root,) + path, node
