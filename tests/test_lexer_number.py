from typing import List
import unittest

from cjlang.lexer.cursor import Cursor, Token


class TestLexerNumber(unittest.TestCase):
    def get_tokens(self, text: str) -> List[Token]:
        cursor = Cursor(text)
        tokens = cursor.tokenize()
        return tokens

    def test1(self):
        tokens = self.get_tokens("32")
        self.assertEqual(tokens[0], Token("DecimalLiteral", "32", 0, 2))

    def test2(self):
        tokens = self.get_tokens("32.0")
        self.assertEqual(tokens[0], Token("FloatLiteral", "32.0", 0, 4))

    def test3(self):
        tokens = self.get_tokens(".05")
        self.assertEqual(tokens[0], Token("FloatLiteral", ".05", 0, 3))

    def test4(self):
        tokens = self.get_tokens("7634.08889e-05f64")
        self.assertEqual(tokens[0], Token("FloatLiteral", "7634.08889e-05f64", 0, 17))

    def test5(self):
        tokens = self.get_tokens("s[0..(s.size - k)]")
        self.assertEqual(
            tokens,
            [
                Token("IDENTIFIER", "s", 0, 1),
                Token("LBRACKET", None, 1, 2),
                Token("DecimalLiteral", "0", 2, 3),
                Token("RANGE", None, 3, 5),
                Token("LPAREN", None, 5, 6),
                Token("IDENTIFIER", "s", 6, 7),
                Token("DOT", None, 7, 8),
                Token("IDENTIFIER", "size", 8, 12),
                Token("MINUS", None, 13, 14),
                Token("IDENTIFIER", "k", 15, 16),
                Token("RPAREN", None, 16, 17),
                Token("RBRACKET", None, 17, 18),
                Token("EOF", None, None, None),
            ],
        )

        tokens = self.get_tokens("s[0..=5]")
        self.assertEqual(
            tokens,
            [
                Token("IDENTIFIER", "s", 0, 1),
                Token("LBRACKET", None, 1, 2),
                Token("DecimalLiteral", "0", 2, 3),
                Token("RANGE_EQ", None, 3, 6),
                Token("DecimalLiteral", "5", 6, 7),
                Token("RBRACKET", None, 7, 8),
                Token("EOF", None, None, None),
            ],
        )


if __name__ == "__main__":
    unittest.main()
