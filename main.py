from cjlang.lexer.cursor import Cursor

cursor = Cursor("let width1: Int32 = 32 // The newline character is treated as a terminator.")
tokens = cursor.tokenize()

print(tokens)