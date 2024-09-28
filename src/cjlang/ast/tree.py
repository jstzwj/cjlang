from .node import Node
from .node import NodeKind
class TranslationUnit(Node):
    def __init__(self, token_start: int, token_end: int):
        super().__init__(NodeKind.TranslationUnit, token_start, token_end)
