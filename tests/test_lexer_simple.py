from typing import List
import unittest

from cjlang.lexer.cursor import Cursor, Token
from cjlang.lexer.kinds import TokenKind


class TestLexerSimple(unittest.TestCase):
    def get_tokens(self, text: str) -> List[Token]:
        cursor = Cursor(text)
        tokens = cursor.tokenize()
        return tokens

    def test1(self):
        test_case = "let width1: Int32 = 32 // The newline character is treated as a terminator."
        tokens = self.get_tokens(test_case)
        taret_tokens = [
            Token(TokenKind.IDENT, "let", 0, 3),
            Token(TokenKind.WS, None, 3, 4),
            Token(TokenKind.IDENT, "width1", 4, 10),
            Token(TokenKind.COLON, None, 10, 11),
            Token(TokenKind.WS, None, 11, 12),
            Token(TokenKind.IDENT, "Int32", 12, 17),
            Token(TokenKind.WS, None, 17, 18),
            Token(TokenKind.ASSIGN, None, 18, 19),
            Token(TokenKind.WS, None, 19, 20),
            Token(TokenKind.DECIMAL_LITERAL, "32", 20, 22),
            Token(TokenKind.WS, None, 22, 23),
            Token(TokenKind.LINE_COMMENT, None, 23, 75),
            Token(TokenKind.EOF, None, None, None),
        ]
        self.assertEqual(
            tokens,
            taret_tokens,
        )

    def test_unicode(self):
        test_case = "let 仓颉: Float64 = 1.1e3"
        tokens = self.get_tokens(test_case)
        taret_tokens = [
            Token(TokenKind.IDENT, "let", 0, 3),
            Token(TokenKind.WS, None, 3, 4),
            Token(TokenKind.IDENT, "仓颉", 4, 6),
            Token(TokenKind.COLON, None, 6, 7),
            Token(TokenKind.WS, None, 7, 8),
            Token(TokenKind.IDENT, "Float64", 8, 15),
            Token(TokenKind.WS, None, 15, 16),
            Token(TokenKind.ASSIGN, None, 16, 17),
            Token(TokenKind.WS, None, 17, 18),
            Token(TokenKind.FLOAT_LITERAL, "1.1e3", 18, 23),
            Token(TokenKind.EOF, None, None, None),
        ]
        self.assertEqual(
            tokens,
            taret_tokens,
        )

    def test_raw_ident(self):
        test_case = "var `a` = 5;"
        tokens = self.get_tokens(test_case)
        taret_tokens = [
            Token(TokenKind.IDENT, "var", 0, 3),
            Token(TokenKind.WS, None, 3, 4),
            Token(TokenKind.RAW_IDENT, "`a`", 4, 7),
            Token(TokenKind.WS, None, 7, 8),
            Token(TokenKind.ASSIGN, None, 8, 9),
            Token(TokenKind.WS, None, 9, 10),
            Token(TokenKind.DECIMAL_LITERAL, "5", 10, 11),
            Token(TokenKind.COLON, None, 11, 12),
            Token(TokenKind.EOF, None, None, None),
        ]
        self.assertEqual(
            tokens,
            taret_tokens,
        )


if __name__ == "__main__":
    unittest.main()
