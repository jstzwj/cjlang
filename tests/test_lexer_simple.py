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
            Token("IDENTIFIER", "width1", 4, 10),
            Token("COLON", None, 10, 11),
            Token("IDENTIFIER", "Int32", 12, 17),
            Token("ASSIGN", None, 18, 19),
            Token("DecimalLiteral", "32", 20, 22),
            Token("LINE_COMMENT", None, 23, 75),
            Token("EOF", None, None, None),
        ]
        self.assertEqual(
            tokens,
            taret_tokens,
        )


if __name__ == "__main__":
    unittest.main()
