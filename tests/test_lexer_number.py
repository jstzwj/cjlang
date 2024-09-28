from typing import List
import unittest

from cjlang.lexer.cursor import Cursor, Token
from cjlang.lexer.kinds import TokenKind


class TestLexerNumber(unittest.TestCase):
    def get_tokens(self, text: str) -> List[Token]:
        cursor = Cursor(text)
        tokens = cursor.tokenize()
        return tokens

    def test1(self):
        tokens = self.get_tokens("32")
        self.assertEqual(tokens[0], Token(TokenKind.DECIMAL_LITERAL, '32', 0, 2))

    def test2(self):
        tokens = self.get_tokens("32.0")
        self.assertEqual(tokens[0], Token(TokenKind.FLOAT_LITERAL, '32.0', 0, 4))

    def test3(self):
        tokens = self.get_tokens(".05")
        self.assertEqual(tokens[0], Token(TokenKind.FLOAT_LITERAL, '.05', 0, 3))

    def test4(self):
        tokens = self.get_tokens("7634.08889e-05f64")
        self.assertEqual(tokens[0], Token(TokenKind.FLOAT_LITERAL, '7634.08889e-05f64', 0, 17))

    def test5(self):
        tokens = self.get_tokens("s[0..(s.size - k)]")
        self.assertEqual(
            tokens,
            [
                Token(TokenKind.IDENT, "s", 0, 1),
                Token(TokenKind.LSQUARE, None, 1, 2),
                Token(TokenKind.DECIMAL_LITERAL, "0", 2, 3),
                Token(TokenKind.RANGEOP, None, 3, 5),
                Token(TokenKind.LPAREN, None, 5, 6),
                Token(TokenKind.IDENT, "s", 6, 7),
                Token(TokenKind.DOT, None, 7, 8),
                Token(TokenKind.IDENT, "size", 8, 12),
                Token(TokenKind.WS, None, 12, 13),
                Token(TokenKind.SUB, None, 13, 14),
                Token(TokenKind.WS, None, 14, 15),
                Token(TokenKind.IDENT, "k", 15, 16),
                Token(TokenKind.RPAREN, None, 16, 17),
                Token(TokenKind.RSQUARE, None, 17, 18),
                Token(TokenKind.EOF, None, None, None),
            ],
        )

        tokens = self.get_tokens("s[0..=5]")
        self.assertEqual(
            tokens,
            [
                Token(TokenKind.IDENT, "s", 0, 1),
                Token(TokenKind.LSQUARE, None, 1, 2),
                Token(TokenKind.DECIMAL_LITERAL, "0", 2, 3),
                Token(TokenKind.CLOSEDRANGEOP, None, 3, 6),
                Token(TokenKind.DECIMAL_LITERAL, "5", 6, 7),
                Token(TokenKind.RSQUARE, None, 7, 8),
                Token(TokenKind.EOF, None, None, None),
            ],
        )


if __name__ == "__main__":
    unittest.main()
