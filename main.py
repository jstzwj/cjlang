from cjlang.lexer.cursor import Cursor

cursor = Cursor("let width1: Int32 = 32 // The newline character is treated as a terminator.")
# cursor = Cursor("/**** this is a comment*/ let a = '\n'")
tokens = cursor.tokenize()

print(tokens)