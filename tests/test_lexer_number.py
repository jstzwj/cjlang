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
        self.assertEqual(
            tokens[0],
            Token("DecimalLiteral", "32", 0, 2)
        )

    def test2(self):
        tokens = self.get_tokens("32.0")
        self.assertEqual(
            tokens[0],
            Token("FloatLiteral", '32.0', 0, 4)
        )
    
    def test3(self):
        tokens = self.get_tokens(".05")
        self.assertEqual(
            tokens[0],
            Token("FloatLiteral", '.05', 0, 3)
        )
    
    def test4(self):
        tokens = self.get_tokens("7634.08889e-05f64")
        self.assertEqual(
            tokens[0],
            Token("FloatLiteral", '7634.08889e-05f64', 0, 17)
        )

if __name__ == "__main__":
    unittest.main()
