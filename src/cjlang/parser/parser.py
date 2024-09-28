from typing import List, Optional

from cjlang.lexer.cursor import Cursor, Token
from cjlang.ast.node import Node, NodeKind

class CangjieParser:
    def __init__(self, cursor: Cursor):
        self._cursor = cursor

    def lookahead(self) -> Token:
        """Returns the current token without consuming it."""
        c = self._cursor.clone()
        return c.advance_token()

    def match_token(self, expected_token: str) -> Token:
        """Matches and consumes the expected token."""
        if self.position < len(self.tokens) and self.tokens[self.position] == expected_token:
            self.position += 1
            return expected_token
        raise SyntaxError(f"Expected {expected_token}, but found {self.tokens[self.position]}")

    def end_of_tokens(self) -> bool:
        """Checks if all tokens have been consumed."""
        return self._cursor.is_eof()

    def parse_translation_unit(self) -> Node:
        """Parses a translation unit."""
        token_start = self.current_position()
        token_end = len(self.tokens)  # Final position after parsing

        unit = Node(NodeKind.TranslationUnit, token_start, token_end)

        # Parse preamble
        preamble_node = self.parse_preamble()
        if preamble_node:
            unit.add_child(preamble_node)

        # Parse top-level objects
        while not self.end_of_tokens():
            top_level_object_node = self.parse_top_level_object()
            if top_level_object_node:
                unit.add_child(top_level_object_node)

        return unit

    def parse_preamble(self) -> Optional[Node]:
        """Parses the preamble section."""
        token_start = self.current_position()
        if self.lookahead() == 'PACKAGE':
            package_header_node = self.parse_package_header()
            if package_header_node:
                preamble_node = Node(NodeKind.Preamble, token_start, self.current_position())
                preamble_node.add_child(package_header_node)
                return preamble_node
        return None

    def parse_package_header(self) -> Optional[Node]:
        """Parses the package header."""
        token_start = self.current_position()
        self.match_token('PACKAGE')

        package_name_node = self.parse_package_name_identifier()
        if package_name_node:
            package_header_node = Node(NodeKind.PackageHeader, token_start, self.current_position())
            package_header_node.add_child(package_name_node)
            return package_header_node
        return None

    def parse_package_name_identifier(self) -> Node:
        """Parses the package name identifier."""
        token_start = self.current_position()
        self.match_token('IDENTIFIER')  # Parse the package identifier (simple case)
        return Node(NodeKind.PackageHeader, token_start, self.current_position())

    def parse_top_level_object(self) -> Optional[Node]:
        """Parses a top-level object."""
        token_start = self.current_position()
        kind = None

        if self.lookahead() == 'CLASS':
            kind = NodeKind.ClassDefinition
            self.match_token('CLASS')
            # Parsing of class definition body (omitted)
        elif self.lookahead() == 'FUNCTION':
            kind = NodeKind.FunctionDefinition
            self.match_token('FUNCTION')
            # Parsing of function definition body (omitted)

        if kind:
            return Node(kind, token_start, self.current_position())

        return None
