from cjlang.lexer.cursor import Cursor
test_case = "-7634.08889e-05f64 + 56"

cursor = Cursor(test_case)
tokens = cursor.tokenize()
cursor.diagnostics.show_diagnostics()

print(tokens)