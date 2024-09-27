from typing import List
import unittest

from cjlang.lexer.cursor import Cursor, Token


class TestLexerSimple(unittest.TestCase):
    def get_tokens(self, text: str) -> List[Token]:
        cursor = Cursor(text)
        tokens = cursor.tokenize()
        return tokens

    def test1(self):
        test_case = "let width1: Int32 = 32 // The newline character is treated as a terminator."
        tokens = self.get_tokens(test_case)
        taret_tokens = [
            Token("IDENTIFIER", "let", 0, 3),
            Token("WHITESPACE", None, 3, 4),
            Token("IDENTIFIER", "width1", 4, 10),
            Token("COLON", None, 10, 11),
            Token("WHITESPACE", None, 11, 12),
            Token("IDENTIFIER", "Int32", 12, 17),
            Token("WHITESPACE", None, 17, 18),
            Token("ASSIGN", None, 18, 19),
            Token("WHITESPACE", None, 19, 20),
            Token("DecimalLiteral", "32", 20, 22),
            Token("WHITESPACE", None, 22, 23),
            Token("LINE_COMMENT", None, 23, 75),
            Token("EOF", None, None, None),
        ]
        self.assertEqual(
            tokens,
            taret_tokens,
        )

    def test_unicode(self):
        test_case = "let 仓颉: Float64 = 1.1e3"
        tokens = self.get_tokens(test_case)
        taret_tokens = [
            Token('IDENTIFIER', "let", 0, 3),
            Token('WHITESPACE', None, 3, 4),
            Token('IDENTIFIER', "仓颉", 4, 6),
            Token('COLON', None, 6, 7),
            Token('WHITESPACE', None, 7, 8),
            Token('IDENTIFIER', "Float64", 8, 15),
            Token('WHITESPACE', None, 15, 16),
            Token('ASSIGN', None, 16, 17),
            Token('WHITESPACE', None, 17, 18),
            Token('FloatLiteral', "1.1e3", 18, 23),
            Token('EOF', None, None, None),
        ]
        self.assertEqual(
            tokens,
            taret_tokens,
        )

    def test_raw_ident(self):
        test_case = "var `a` = 5;"
        tokens = self.get_tokens(test_case)
        taret_tokens = [
            Token("IDENTIFIER", "var", 0, 3),
            Token("WHITESPACE", None, 3, 4),
            Token("RAW_IDENTIFIER", "`a`", 4, 7),
            Token("WHITESPACE", None, 7, 8),
            Token("ASSIGN", None, 8, 9),
            Token("WHITESPACE", None, 9, 10),
            Token("DecimalLiteral", "5", 10, 11),
            Token("SEMICOLON", None, 11, 12),
            Token("EOF", None, None, None),
        ]
        self.assertEqual(
            tokens,
            taret_tokens,
        )


if __name__ == "__main__":
    unittest.main()
