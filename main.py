from cjlang.lexer.cursor import Cursor
test_case = "0b0001_1000"
test_case = "0o30"
test_case = "0x18FFGG"
test_case = "0x1.1p0"
test_case = "1.1e3"
test_case = "let 仓颉: Float64 = 1.1e3"
test_case = "s[0..=5]"
test_case = "let a = 3.0f"
test_case = "hex = hexDigits[(Int64(num & 0xf))] + hex"
# with open("test.cj", "r", encoding="utf-8") as f:
#     test_case = f.read()
cursor = Cursor(test_case)
tokens = cursor.tokenize()
cursor.diagnostics.show_diagnostics()

print(tokens)