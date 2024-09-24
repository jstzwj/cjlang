import unittest

from cjlang.lexer.cursor import Cursor
class TestLexerSimple(unittest.TestCase):

    def test1(self):
        cursor = Cursor("let width1: Int32 = 32 // The newline character is treated as a terminator.")
        tokens = cursor.tokenize()

if __name__ == '__main__':
    unittest.main()