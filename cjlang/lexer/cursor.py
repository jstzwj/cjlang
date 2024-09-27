import string
from typing import List, Literal, Optional

from cjlang.diagnostics.diagnostic import SourceLocation, get_line_column
from cjlang.diagnostics.engine import DiagnosticEngine
from cjlang.keywords import OPERATOR_CHARACTERS
from cjlang.utils.unicode_xid import is_xid_continue, is_xid_start

LEXICAL_CATEGORY = "Lexical Issue"

from enum import Enum

class Token(Enum):
    INT = 1
    FLOAT = 2
    STRING = 3
    PLUS = 4
    MINUS = 5
    MULTIPLY = 6
    DIVIDE = 7
    LPAREN = 8
    RPAREN = 9

def is_whitespace(c):
    # This is Pattern_White_Space.
    #
    # Note that this set is stable (ie, it doesn't change with different
    # Unicode versions), so it's ok to just hard-code the values.
    return c in {
        # Usual ASCII suspects
        "\u0009",  # \t
        "\u000A",  # \n
        "\u000B",  # vertical tab
        "\u000C",  # form feed
        "\u000D",  # \r
        "\u0020",  # space
        # NEXT LINE from latin1
        "\u0085",
        # Bidi markers
        "\u200E",  # LEFT-TO-RIGHT MARK
        "\u200F",  # RIGHT-TO-LEFT MARK
        # Dedicated whitespace characters from Unicode
        "\u2028",  # LINE SEPARATOR
        "\u2029",  # PARAGRAPH SEPARATOR
    }


def is_id_start(c):
    # This is XID_Start OR '_' (which formally is not a XID_Start).
    return c == "_" or is_xid_start(c)


def is_id_continue(c):
    return is_xid_continue(c)


def is_hex_char(char: str) -> bool:
    char = char.upper()
    return char.isdigit() or ("A" <= char <= "F")


def is_oct_char(char: str) -> bool:
    return "0" <= char <= "7"


class Token:
    def __init__(self, type, value=None, start_pos=None, end_pos=None):
        self.type = type
        self.value = value
        self.start_pos = start_pos  # Start position of the token
        self.end_pos = end_pos  # End position of the token

    def __eq__(self, other):
        if not isinstance(other, Token):
            return False
        return (self.type, self.value, self.start_pos, self.end_pos) == (
            other.type,
            other.value,
            other.start_pos,
            other.end_pos,
        )

    def __repr__(self):
        if self.value is not None:
            return (
                f"Token({self.type}, {self.value!r}, {self.start_pos}, {self.end_pos})"
            )
        return f"Token({self.type}, {self.value!r}, {self.start_pos}, {self.end_pos})"


class Cursor:
    def __init__(
        self,
        text: str,
        filepath: Optional[str] = None,
        diagnostics: Optional[DiagnosticEngine] = None,
    ):
        self.text: str = text
        self.filepath: Optional[str] = filepath
        self.pos: int = 0
        self.current_char: Optional[str] = self.text[self.pos] if self.text else None
        if diagnostics is None:
            self.diagnostics = DiagnosticEngine()
        else:
            self.diagnostics = diagnostics

    def advance(self) -> None:
        self.pos += 1
        if self.pos < len(self.text):
            self.current_char = self.text[self.pos]
        else:
            self.current_char = None

    def eat_while(self, condition) -> None:
        while self.current_char is not None and condition(self.current_char):
            self.advance()

    def is_eof(self) -> bool:
        return self.pos >= len(self.text)
    
    def clone(self) -> "Cursor":
        new_cursor = Cursor(self.text, self.filepath, self.diagnostics)
        new_cursor.pos = self.pos
        new_cursor.current_char = self.current_char
        return new_cursor

    def tokenize(self) -> List[Token]:
        tokens = []
        while True:
            token = self.advance_token()
            tokens.append(token)
            if token.type == "EOF":
                break
        return tokens

    def advance_token(self) -> Token:
        if self.current_char is None:
            return Token("EOF")

        if is_whitespace(self.current_char):
            return self.consume_whitespace()

        if self.current_char == "b" and self.peek() in ("'", '"'):
            if self.peek() == "'":
                single_char = True
            else:
                single_char = False

            return self.consume_string(
                self.peek(), single_char=single_char, byte_string=True
            )

        if self.current_char == '"':
            return self.consume_string('"', single_char=False)

        if self.current_char == "'":
            return self.consume_string("'", single_char=True)

        if self.current_char == ".":
            if self.peek() == ".":
                if self.first_n(2) == "=":
                    token_name = "RANGE_EQ"
                    self.advance()  # Move past the first '.'
                    self.advance()  # Move past the second '.'
                    self.advance()  # Move past the third '='
                    return self.create_token(
                        token_name,
                        value=None,
                        start_pos=self.pos - 3,
                        end_pos=self.pos,
                    )
                else:
                    token_name = "RANGE"
                    self.advance()  # Move past the first '.'
                    self.advance()  # Move past the second '.'
                    return self.create_token(
                        token_name,
                        value=None,
                        start_pos=self.pos - 2,
                        end_pos=self.pos,
                    )

        if self.current_char.isdigit() or (
            self.current_char == "." and self.peek().isdigit()
        ):
            return self.consume_number()

        if self.current_char.isalpha() or self.current_char == "_":
            return self.consume_identifier()

        if self.current_char == "`":
            return self.consume_identifier(is_raw=True)

        if self.current_char == ";":
            token = self.create_token("SEMICOLON")
            self.advance()
            return token

        if self.current_char == ",":
            token = self.create_token("COMMA")
            self.advance()
            return token

        if self.current_char == ":":
            token = self.create_token("COLON")
            self.advance()
            return token

        # Comments
        if self.current_char == "/" and self.peek() == "/":
            token = self.consume_line_comment()
            return token

        if self.current_char == "/" and self.peek() == "*":
            token = self.consume_block_comment()
            return token

        # Operatiors
        if self.current_char == "@":
            token = self.create_token("MACRO")
            self.advance()
            return token

        if self.current_char == ".":
            token = self.create_token("DOT")
            self.advance()
            return token

        if self.current_char == "[":
            token = self.create_token("LBRACKET")
            self.advance()
            return token

        if self.current_char == "]":
            token = self.create_token("RBRACKET")
            self.advance()
            return token

        if self.current_char == "(":
            token = self.create_token("LPAREN")
            self.advance()
            return token

        if self.current_char == ")":
            token = self.create_token("RPAREN")
            self.advance()
            return token

        if self.current_char == "+" and self.peek() == "+":
            self.advance()  # Move past the first '+'
            self.advance()  # Move past the second '+'
            return self.create_token(
                "POSTFIX_INCREMENT",
                value=None,
                start_pos=self.pos - 2,
                end_pos=self.pos,
            )

        if self.current_char == "-" and self.peek() == "-":
            self.advance()  # Move past the first '-'
            self.advance()  # Move past the second '-'
            return self.create_token(
                "POSTFIX_DECREMENT",
                value=None,
                start_pos=self.pos - 2,
                end_pos=self.pos,
            )

        if self.current_char == "?":
            if self.peek() == "?":
                self.advance()  # Move past the first '?'
                self.advance()  # Move past the second '?'
                return self.create_token(
                    "COALESCING",
                    value=None,
                    start_pos=self.pos - 2,
                    end_pos=self.pos,
                )
            else:
                token = self.create_token("QUESTION")
                self.advance()
                return token

        if self.current_char == "*":
            if self.peek() == "*":
                if self.first_n(2) == "=":
                    self.advance()  # Move past the first '*'
                    self.advance()  # Move past the second '*'
                    self.advance()  # Move past the second '='
                    return self.create_token(
                        "COMPOUND_ASSIGN",
                        value=None,
                        start_pos=self.pos - 3,
                        end_pos=self.pos,
                    )
                else:
                    self.advance()  # Move past the first '*'
                    self.advance()  # Move past the second '*'
                    return self.create_token(
                        "POWER",
                        value=None,
                        start_pos=self.pos - 2,
                        end_pos=self.pos,
                    )
            elif self.peek() == "=":
                self.advance()  # Move past the first '*'
                self.advance()  # Move past the second '='
                return self.create_token(
                    "MULTIPLY_ASSIGN",
                    value=None,
                    start_pos=self.pos - 2,
                    end_pos=self.pos,
                )
            else:
                token = self.create_token("STAR")
                self.advance()
                return token

        if self.current_char == "+":
            if self.peek() == "=":
                self.advance()  # Move past the first '+'
                self.advance()  # Move past the second '='
                return self.create_token(
                    "PLUS_ASSIGN",
                    value=None,
                    start_pos=self.pos - 2,
                    end_pos=self.pos,
                )
            else:
                token = self.create_token("PLUS")
                self.advance()
                return token

        if self.current_char == "-":
            if self.peek() == "=":
                self.advance()  # Move past the first '-'
                self.advance()  # Move past the second '='

                return self.create_token(
                    "MINUS_ASSIGN",
                    value=None,
                    start_pos=self.pos - 2,
                    end_pos=self.pos,
                )

            else:
                token = self.create_token("MINUS")
                self.advance()
                return token

        if self.current_char == "/":
            if self.peek() == "=":
                self.advance()  # Move past the first '/'
                self.advance()  # Move past the second '='
                return self.create_token(
                    "DIVIDE_ASSIGN",
                    value=None,
                    start_pos=self.pos - 2,
                    end_pos=self.pos,
                )
            else:
                token = self.create_token("SLASH")
                self.advance()
                return token

        if self.current_char == "{":
            token = self.create_token("LBRACE")
            self.advance()
            return token

        if self.current_char == "}":
            token = self.create_token("RBRACE")
            self.advance()
            return token

        if self.current_char == "%":
            if self.peek() == "=":
                self.advance()  # Move past the first '%'
                self.advance()  # Move past the second '='
                return self.create_token(
                    "REMAINDER_ASSIGN",
                    value=None,
                    start_pos=self.pos - 2,
                    end_pos=self.pos,
                )
            else:
                token = self.create_token("REMAINDER")
                self.advance()
                return token

        if self.current_char == "^":
            if self.peek() == "=":
                self.advance()  # Move past the first '^'
                self.advance()  # Move past the second '='
                return self.create_token(
                    "BITWISE_XOR_ASSIGN",
                    value=None,
                    start_pos=self.pos - 2,
                    end_pos=self.pos,
                )
            else:
                token = self.create_token("BITWISE_XOR")
                self.advance()
                return token

        if self.current_char == ">":
            if self.peek() == "=":
                self.advance()  # Move past the first '>'
                self.advance()  # Move past the second '='
                return self.create_token(
                    "NLT", value=None, start_pos=self.pos - 2, end_pos=self.pos
                )
            elif self.peek() == ">":
                self.advance()  # Move past the first '>'
                self.advance()  # Move past the second '>'
                return self.create_token(
                    "BITWISE_RIGHT_SHIFT",
                    value=None,
                    start_pos=self.pos - 2,
                    end_pos=self.pos,
                )
            else:
                token = self.create_token("GT")
                self.advance()
                return token

        if self.current_char == "<":
            if self.peek() == "=":
                self.advance()  # Move past the first '<'
                self.advance()  # Move past the second '='
                return self.create_token(
                    "NGT", value=None, start_pos=self.pos - 2, end_pos=self.pos
                )
            elif self.peek() == "<":
                if self.first_n(2) == "=":
                    self.advance()  # Move past the first '<'
                    self.advance()  # Move past the second '<'
                    self.advance()  # Move past the second '='
                    return self.create_token(
                        "BITWISE_LEFT_SHIFT_ASSIGN",
                        value=None,
                        start_pos=self.pos - 3,
                        end_pos=self.pos,
                    )
                else:
                    self.advance()  # Move past the first '<'
                    self.advance()  # Move past the second '<'
                    return self.create_token(
                        "BITWISE_LEFT_SHIFT",
                        value=None,
                        start_pos=self.pos - 2,
                        end_pos=self.pos,
                    )

            else:
                token = self.create_token("LT")
                self.advance()
                return token

        # Check for '==' (EQUAL_EQUAL)
        if self.current_char == "=":
            if self.peek() == "=":
                self.advance()  # Move past the first '='
                self.advance()  # Move past the second '='
                return self.create_token(
                    "EQUAL",
                    value=None,
                    start_pos=self.pos - 2,
                    end_pos=self.pos,
                )
            else:
                token = self.create_token("ASSIGN")
                self.advance()
                return token

        if self.current_char == "!":
            if self.peek() == "=":
                self.advance()  # Move past the first '!'
                self.advance()  # Move past the second '='
                return self.create_token(
                    "NOTEQUAL",
                    value=None,
                    start_pos=self.pos - 2,
                    end_pos=self.pos,
                )
            else:
                token = self.create_token("NOT")
                self.advance()
                return token

        if self.current_char == "&":
            if self.peek() == "&":
                if self.first_n(2) == "=":
                    self.advance()  # Move past the first '&'
                    self.advance()  # Move past the second '&'
                    self.advance()  # Move past the second '='
                    token = self.create_token(
                        "LOGICAL_AND_ASSIGN",
                        value=None,
                        start_pos=self.pos - 3,
                        end_pos=self.pos,
                    )
                else:
                    self.advance()  # Move past the first '&'
                    self.advance()  # Move past the second '&'
                    return self.create_token(
                        "LOGICAL_AND",
                        value=None,
                        start_pos=self.pos - 2,
                        end_pos=self.pos,
                    )
            elif self.peek() == "=":
                self.advance()  # Move past the first '&'
                self.advance()  # Move past the second '='
                return self.create_token(
                    "BITWISE_AND_ASSIGN",
                    value=None,
                    start_pos=self.pos - 2,
                    end_pos=self.pos,
                )

            else:
                token = self.create_token("BITWISE_AND")
                self.advance()
                return token

        if self.current_char == "|":
            if self.peek() == "|":
                if self.first_n(2) == "=":
                    self.advance()  # Move past the first '|'
                    self.advance()  # Move past the second '|'
                    self.advance()  # Move past the second '='
                    return self.create_token(
                        "LOGICAL_OR_ASSIGN",
                        value=None,
                        start_pos=self.pos - 3,
                        end_pos=self.pos,
                    )

                else:
                    self.advance()  # Move past the first '|'
                    self.advance()  # Move past the second '|'
                    return self.create_token(
                        "LOGICAL_OR",
                        value=None,
                        start_pos=self.pos - 2,
                        end_pos=self.pos,
                    )

            elif self.peek() == "=":
                self.advance()  # Move past the first '|'
                self.advance()  # Move past the second '='
                return self.create_token(
                    "BITWISE_OR_ASSIGN",
                    value=None,
                    start_pos=self.pos - 2,
                    end_pos=self.pos,
                )

            elif self.peek() == ">":
                self.advance()  # Move past the first '|'
                self.advance()  # Move past the second '>'
                return self.create_token(
                    "PIPELINE",
                    value=None,
                    start_pos=self.pos - 2,
                    end_pos=self.pos,
                )

            else:
                token = self.create_token("BITWISE_OR")
                self.advance()
                return token

        if self.current_char == "~" and self.peek() == ">":
            self.advance()  # Move past the first '~'
            self.advance()  # Move past the second '>'
            return self.create_token(
                "COMPOSITION",
                value=None,
                start_pos=self.pos - 2,
                end_pos=self.pos,
            )

        raise Exception(f"Unexpected character: {self.current_char}")

    def peek(self):
        """Peek at the next character without advancing the position."""
        if self.pos + 1 < len(self.text):
            return self.text[self.pos + 1]
        return None

    def first_n(self, n: int):
        """Peek at the top-n character without advancing the position."""
        if self.pos + n < len(self.text):
            return self.text[self.pos + n]
        return None

    def create_token(self, token_type, value=None, start_pos=None, end_pos=None):
        """Helper function to create a token with its start and end position."""
        if start_pos is None:
            start_pos = self.pos
        if end_pos is None:
            end_pos = self.pos + 1
        return Token(type=token_type, value=value, start_pos=start_pos, end_pos=end_pos)

    def consume_whitespace(self) -> Token:
        start_pos = self.pos
        while self.current_char is not None and is_whitespace(self.current_char):
            self.advance()
        return self.create_token("WHITESPACE", None, start_pos, self.pos)

    def consume_line_comment(self) -> Token:
        start_pos = self.pos
        self.advance()
        self.advance()

        while self.current_char is not None:
            if self.current_char in ["\n", "\r"]:
                break
            self.advance()
        return self.create_token("LINE_COMMENT", None, start_pos, self.pos)

    def consume_block_comment(self) -> Token:
        start_pos = self.pos
        self.advance()
        self.advance()
        while self.current_char is not None:
            if self.current_char == "*" and self.peek() == "/":
                self.advance()
                self.advance()
                break
            self.advance()
        return self.create_token("BLOCK_COMMENT", None, start_pos, self.pos)

    def consume_decimal_fragment(self):
        if self.current_char.isdigit():
            self.advance()
        else:
            raise Exception("Invalid fragment")

        while self.current_char is not None:
            if self.current_char.isdigit() or self.current_char == "_":
                self.advance()
            elif self.current_char in ("e", "E"):
                break
            elif is_whitespace(self.current_char):
                break
            elif self.current_char in OPERATOR_CHARACTERS:
                break
            elif self.current_char in ("f", "i", "u"):
                break
            else:
                self.diagnostics.error(
                    f"illegal digit in decimal literal '{self.text[self.pos:self.pos + 1]}'",
                    SourceLocation.from_tuple(
                        self.filepath, get_line_column(self.text, self.pos)
                    ),
                    LEXICAL_CATEGORY,
                )
                self.eat_while(lambda x: x.isdigit() or x.isalpha() or x == "_")
                break

    def consume_decimal_fraction(self):
        if self.current_char == "." and self.peek().isdigit():
            self.advance()
            self.consume_decimal_fragment()
        else:
            raise Exception("Invalid decimal fraction")

    def consume_decimal_exponent(self):
        if self.current_char in ("e", "E"):
            self.advance()
        else:
            raise Exception("Cannot find decimal exponent")

        if self.current_char == "-":
            self.advance()
        self.consume_decimal_fragment()

    def consume_hexadecimal_fraction(self):
        if self.current_char == "." and is_hex_char(self.peek()):
            self.advance()
            self.consume_hexadecimal_digits()
        else:
            raise Exception("Invalid hexadecimal fraction")

    def consume_hexadecimal_exponent(self):
        if self.current_char in ("p", "P"):
            self.advance()
        else:
            raise Exception("Cannot find hexadecimal exponent")

        if self.current_char == "-":
            self.advance()
        self.consume_decimal_fragment()

    def consume_hexadecimal_digits(self):
        if is_hex_char(self.current_char):
            self.advance()
        else:
            raise Exception("Cannot find hexadecimal digits")
        while self.current_char is not None:
            if is_hex_char(self.current_char) or self.current_char == "_":
                self.advance()
            elif self.current_char in ("p", "P"):
                break
            elif is_whitespace(self.current_char):
                break
            elif self.current_char in OPERATOR_CHARACTERS:
                break
            elif self.current_char in ("f", "i", "u"):
                break
            else:
                self.diagnostics.error(
                    f"illegal digit in hexadecimal literal '{self.text[self.pos:self.pos + 1]}'",
                    SourceLocation.from_tuple(
                        self.filepath, get_line_column(self.text, self.pos)
                    ),
                    LEXICAL_CATEGORY,
                )
                self.eat_while(lambda x: x.isdigit() or x.isalpha() or x == "_")
                break

    def consume_decimal_literal(self):
        allow_underline = True
        if self.current_char == "0":
            allow_underline = False
        while self.current_char is not None:
            if self.current_char.isdigit():
                self.advance()
            elif self.current_char == "_" and allow_underline:
                self.advance()
            elif self.current_char in ("e", "E"):
                break
            elif is_whitespace(self.current_char):
                break
            elif self.current_char in OPERATOR_CHARACTERS:
                break
            elif self.current_char in ("f", "i", "u"):
                break
            else:
                self.diagnostics.error(
                    f"illegal digit in decimal literal '{self.text[self.pos:self.pos + 1]}'",
                    SourceLocation.from_tuple(
                        self.filepath, get_line_column(self.text, self.pos)
                    ),
                    LEXICAL_CATEGORY,
                )
                self.eat_while(lambda x: x.isdigit() or x == "_")
                break

    def consume_integer_literal(
        self,
        literal_type: Literal["BinaryLiteral", "OctalLiteral", "HexadecimalLiteral"],
    ):
        if literal_type == "BinaryLiteral":
            if self.current_char in ("0", "1"):
                self.advance()
            while self.current_char is not None:
                if self.current_char in ("0", "1", "_"):
                    self.advance()
                else:
                    self.diagnostics.error(
                        f"illegal digit in binary literal '{self.text[self.pos:self.pos + 1]}'",
                        SourceLocation.from_tuple(
                            self.filepath, get_line_column(self.text, self.pos)
                        ),
                        LEXICAL_CATEGORY,
                    )
                    self.eat_while(lambda x: x.isdigit() or x == "_")
                    break
        elif literal_type == "OctalLiteral":
            if is_oct_char(self.current_char):
                self.advance()
            while self.current_char is not None:
                if is_oct_char(self.current_char):
                    self.advance()
                else:
                    self.diagnostics.error(
                        f"illegal digit in octal literal '{self.text[self.pos:self.pos + 1]}'",
                        SourceLocation.from_tuple(
                            self.filepath, get_line_column(self.text, self.pos)
                        ),
                        LEXICAL_CATEGORY,
                    )
                    self.eat_while(lambda x: x.isdigit() or x == "_")
                    break
        elif literal_type == "HexadecimalLiteral":
            if is_hex_char(self.current_char):
                self.advance()
            while self.current_char is not None:
                if is_hex_char(self.current_char):
                    self.advance()
                else:
                    self.diagnostics.error(
                        f"illegal digit in hexadecimal literal '{self.text[self.pos:self.pos + 1]}'",
                        SourceLocation.from_tuple(
                            self.filepath, get_line_column(self.text, self.pos)
                        ),
                        LEXICAL_CATEGORY,
                    )
                    self.eat_while(lambda x: x.isdigit() or x == "_")
                    break
        else:
            raise Exception("Invalid integer literal type.")

    def consume_decimal_number(self) -> str:
        if self.current_char == ".":
            self.consume_decimal_fraction()
            if self.current_char in ("e", "E"):
                self.consume_decimal_exponent()
        elif self.current_char.isdigit():
            self.consume_decimal_literal()
            if self.current_char == "." and self.peek().isdigit():
                self.consume_decimal_fraction()
                if self.current_char in ("e", "E"):
                    self.consume_decimal_exponent()
            elif self.current_char in ("e", "E"):
                self.consume_decimal_exponent()
            else:
                return "DecimalLiteral"
        else:
            raise Exception("Invalid literal.")
        return "FloatLiteral"

    def consume_hexadecimal_number(self) -> str:
        if self.current_char == ".":
            self.consume_hexadecimal_fraction()
        elif is_hex_char(self.current_char):
            self.consume_hexadecimal_digits()
            if self.current_char == "." and is_hex_char(self.peek()):
                self.consume_hexadecimal_fraction()
            else:
                return "HexadecimalLiteral"
            self.consume_hexadecimal_exponent()
        else:
            raise Exception("Invalid literal.")
        return "FloatLiteral"

    def consume_number(self) -> Token:
        """Handles both integers and floating point numbers, with possible type suffixes."""
        start_pos = self.pos
        number_str = ""
        dot_seen = False

        literal_type = None
        # Step 1: Parse prefix
        if self.current_char == "0":
            if self.peek() in ("b", "B"):
                literal_type = "BinaryLiteral"
                self.advance()
                self.advance()
            elif self.peek() in ("o", "O"):
                literal_type = "OctalLiteral"
                self.advance()
                self.advance()

        # Step2: Parse body
        if literal_type is None:
            if self.current_char == "0" and self.peek() in ("x", "X"):
                self.advance()
                self.advance()
                literal_type = self.consume_hexadecimal_number()
            else:
                literal_type = self.consume_decimal_number()
        else:
            self.consume_integer_literal(literal_type)

        # Step3: parse suffix
        if literal_type in [
            "BinaryLiteral",
            "OctalLiteral",
            "DecimalLiteral",
            "HexadecimalLiteral",
        ]:
            suffix_pos = self.pos
            if self.current_char in ("i", "u"):
                self.advance()

                if self.current_char == "8":
                    self.advance()
                elif self.current_char == "1" and self.peek() == "6":
                    self.advance()
                    self.advance()
                elif self.current_char == "3" and self.peek() == "2":
                    self.advance()
                    self.advance()
                elif self.current_char == "6" and self.peek() == "4":
                    self.advance()
                    self.advance()
                else:
                    self.eat_while(lambda x: x.isdigit())
                    self.diagnostics.error(
                        f"illegal integer literal suffix '{self.text[suffix_pos:self.pos]}'",
                        SourceLocation.from_tuple(
                            self.filepath, get_line_column(self.text, self.pos)
                        ),
                        LEXICAL_CATEGORY,
                    )

        elif literal_type == "FloatLiteral":
            suffix_pos = self.pos
            if self.current_char == "f":
                self.advance()

                if self.current_char == "1" and self.peek() == "6":
                    self.advance()
                    self.advance()
                elif self.current_char == "3" and self.peek() == "2":
                    self.advance()
                    self.advance()
                elif self.current_char == "6" and self.peek() == "4":
                    self.advance()
                    self.advance()
                else:
                    self.eat_while(lambda x: x.isdigit())
                    self.diagnostics.error(
                        f"illegal float literal suffix '{self.text[suffix_pos:self.pos]}'",
                        SourceLocation.from_tuple(
                            self.filepath, get_line_column(self.text, self.pos)
                        ),
                        LEXICAL_CATEGORY,
                    )

        return self.create_token(
            literal_type, self.text[start_pos : self.pos], start_pos, self.pos
        )

    def consume_identifier(self, is_raw=False) -> Token:
        """Consume an identifier (which may also include numbers after the first character)."""
        start_pos = self.pos
        id_str = ""

        if is_raw:
            if self.current_char == "`":
                id_str += self.current_char
                self.advance()
            else:
                raise Exception("expect '`' in the raw identifier")

        if self.current_char is not None and is_id_start(self.current_char):
            id_str += self.current_char
            self.advance()

        while self.current_char is not None and is_id_continue(self.current_char):
            id_str += self.current_char
            self.advance()

        if is_raw:
            if self.current_char == "`":
                id_str += self.current_char
                self.advance()
            else:
                self.diagnostics.error(
                    f"expected character '`', but character '{self.text[self.pos:self.pos + 1]}' found",
                    SourceLocation.from_tuple(
                        self.filepath, get_line_column(self.text, self.pos)
                    ),
                    LEXICAL_CATEGORY,
                )

        if is_raw:
            token_name = "RAW_IDENTIFIER"
        else:
            token_name = "IDENTIFIER"
        return self.create_token(token_name, id_str, start_pos, self.pos)

    def consume_string(self, quote_char, single_char=False, byte_string=False) -> Token:
        """Consume a string literal, handling escape sequences and matching quotes."""
        start_pos = self.pos
        string_value = ""
        if single_char:
            if byte_string:
                self.advance()  # Move past 'b'
                token_type = "BYTE_CHARACTER"
            else:
                token_type = "CHARACTER"
        else:
            if byte_string:
                self.advance()  # Move past 'b'
                token_type = "BYTE_STRING"
            else:
                token_type = "STRING"

        self.advance()  # Skip the opening quote

        while self.current_char is not None and self.current_char != quote_char:
            if self.current_char == "\\":  # Handle escape sequences
                self.advance()
                if self.current_char in {'"', "'", "\\"}:
                    string_value += self.current_char
                elif self.current_char == "n":
                    string_value += "\n"
                elif self.current_char == "t":
                    string_value += "\t"
                else:
                    raise Exception(f"Invalid escape sequence: \\{self.current_char}")
            else:
                string_value += self.current_char
            self.advance()

        if self.current_char != quote_char:
            raise Exception(
                f"Unterminated string literal starting at position {start_pos}"
            )

        self.advance()  # Skip the closing quote
        return self.create_token(token_type, string_value, start_pos, self.pos)
