from cjlang.lexer.cursor import Cursor
test_case = "0b0001_1000"
test_case = "0o30"
test_case = "0x18FFGG"
test_case = "0x1.1p0"
test_case = "1.1e3"

cursor = Cursor(test_case)
tokens = cursor.tokenize()
cursor.diagnostics.show_diagnostics()

print(tokens)