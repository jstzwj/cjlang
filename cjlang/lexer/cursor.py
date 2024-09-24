


KEYWORDS = [
    "as", "break", "Bool",
    "case", "catch", "class",
    "const", "continue", "Rune",
    "do", "else", "enum",
    "extend", "for", "from",
    "func", "false", "finally",
    "foreign", "Float16", "Float32",
    "Float64", "if", "in",
    "is", "init", "inout",
    "import", "interface", "Int8",
    "Int16", "Int32", "Int64",
    "IntNative", "let", "mut",
    "main", "macro", "match",
    "Nothing", "operator", "prop",
    "package", "quote", "return",
    "spawn", "super", "static",
    "struct", "synchronized", "try",
    "this", "true", "type",
    "throw", "This", "unsafe",
    "Unit", "UInt8", "UInt16",
    "UInt32", "UInt64", "UIntNative",
    "var", "VArray", "where",
    "while",
]

CONTEXTUAL_KEYWORDS = [
    "abstract", "open", "override",
    "private", "protected", "public",
    "redef", "get", "set",
    "sealed",
]

class Token:
    def __init__(self, type, value=None, start_pos=None, end_pos=None):
        self.type = type
        self.value = value
        self.start_pos = start_pos  # Start position of the token
        self.end_pos = end_pos      # End position of the token

    def __eq__(self, other):
        if not isinstance(other, Token):
            return False
        return (self.type, self.value, self.start_pos, self.end_pos) == (other.type, other.value, other.start_pos, other.end_pos)
    
    def __repr__(self):
        if self.value is not None:
            return f"Token({self.type}, {self.value!r}, {self.start_pos}, {self.end_pos})"
        return f"Token({self.type}, {self.value!r}, {self.start_pos}, {self.end_pos})"

class Cursor:
    def __init__(self, text):
        self.text = text
        self.pos = 0
        self.current_char = self.text[self.pos] if self.text else None

    def advance(self):
        self.pos += 1
        if self.pos < len(self.text):
            self.current_char = self.text[self.pos]
        else:
            self.current_char = None

    def eat_while(self, condition):
        while self.current_char is not None and condition(self.current_char):
            self.advance()

    def skip_whitespace(self):
        while self.current_char is not None and self.current_char.isspace():
            self.advance()

    def tokenize(self):
        tokens = []
        while self.current_char is not None:
            if self.current_char.isspace():
                self.skip_whitespace()
                continue
            
            if self.current_char == 'b' and self.peek() in ("'", '"'):
                if self.peek() == "'":
                    single_char = True
                else:
                    single_char = False
                tokens.append(self.consume_string(self.peek(), single_char=single_char, byte_string=True))
                continue
            
            if self.current_char == '"':
                tokens.append(self.consume_string('"', single_char=False))
                continue

            if self.current_char == "'":
                tokens.append(self.consume_string("'", single_char=True))
                continue

            if self.current_char == '.':
                if self.peek() == '.':
                    if self.first_n(2) == '=':
                        token_name = "RANGE_EQ"
                        self.advance()  # Move past the first '.'
                        self.advance()  # Move past the second '.'
                        self.advance()  # Move past the third '='
                        tokens.append(self.create_token(token_name, value=None, start_pos=self.pos-3, end_pos=self.pos))
                    else:
                        token_name = "RANGE"
                        self.advance()  # Move past the first '.'
                        self.advance()  # Move past the second '.'
                        tokens.append(self.create_token(token_name, value=None, start_pos=self.pos-2, end_pos=self.pos))
                    continue
                    

            if self.current_char.isdigit() or (self.current_char == '.' and self.peek().isdigit()):
                tokens.append(self.consume_number())
                continue

            if self.current_char.isalpha() or self.current_char == '_':
                tokens.append(self.consume_identifier())
                continue
            
            if self.current_char == ';':
                tokens.append(self.create_token('SEMICOLON'))
                self.advance()
                continue
            
            if self.current_char == ',':
                tokens.append(self.create_token('COMMA'))
                self.advance()
                continue
            
            if self.current_char == ':':
                tokens.append(self.create_token('COLON'))
                self.advance()
                continue
            
            # Comments
            if self.current_char == '/' and self.peek() == '/':
                tokens.append(self.consume_line_comment())
                continue
            
            if self.current_char == '/' and self.peek() == '*':
                tokens.append(self.consume_block_comment())
                continue
            
            # Operatiors
            if self.current_char == '@':
                tokens.append(self.create_token('MACRO'))
                self.advance()
                continue
            
            if self.current_char == '.':
                tokens.append(self.create_token('DOT'))
                self.advance()
                continue
            
            if self.current_char == '[':
                tokens.append(self.create_token('LBRACKET'))
                self.advance()
                continue

            if self.current_char == ']':
                tokens.append(self.create_token('RBRACKET'))
                self.advance()
                continue
            
            if self.current_char == '(':
                tokens.append(self.create_token('LPAREN'))
                self.advance()
                continue

            if self.current_char == ')':
                tokens.append(self.create_token('RPAREN'))
                self.advance()
                continue
            
            if self.current_char == '+' and self.peek() == '+':
                self.advance()  # Move past the first '+'
                self.advance()  # Move past the second '+'
                tokens.append(self.create_token('POSTFIX_INCREMENT', value=None, start_pos=self.pos-2, end_pos=self.pos))
                continue
            
            if self.current_char == '-' and self.peek() == '-':
                self.advance()  # Move past the first '-'
                self.advance()  # Move past the second '-'
                tokens.append(self.create_token('POSTFIX_DECREMENT', value=None, start_pos=self.pos-2, end_pos=self.pos))
                continue
            
            if self.current_char == '?':
                if self.peek() == '?':
                    self.advance()  # Move past the first '?'
                    self.advance()  # Move past the second '?'
                    tokens.append(self.create_token('COALESCING', value=None, start_pos=self.pos-2, end_pos=self.pos))
                else:
                    tokens.append(self.create_token('QUESTION'))
                    self.advance()
                continue
            
            if self.current_char == '*':
                if self.peek() == '*':
                    if self.first_n(2) == '=':
                        self.advance()  # Move past the first '*'
                        self.advance()  # Move past the second '*'
                        self.advance()  # Move past the second '='
                        tokens.append(self.create_token('COMPOUND_ASSIGN', value=None, start_pos=self.pos-3, end_pos=self.pos))
                    else:
                        self.advance()  # Move past the first '*'
                        self.advance()  # Move past the second '*'
                        tokens.append(self.create_token('POWER', value=None, start_pos=self.pos-2, end_pos=self.pos))
                elif self.peek() == '=':
                    self.advance()  # Move past the first '*'
                    self.advance()  # Move past the second '='
                    tokens.append(self.create_token('MULTIPLY_ASSIGN', value=None, start_pos=self.pos-2, end_pos=self.pos))
                else:
                    tokens.append(self.create_token('STAR'))
                    self.advance()
                continue

            if self.current_char == '+':
                if self.peek() == '=':
                    self.advance()  # Move past the first '+'
                    self.advance()  # Move past the second '='
                    tokens.append(self.create_token('PLUS_ASSIGN', value=None, start_pos=self.pos-2, end_pos=self.pos))
                else:
                    tokens.append(self.create_token('PLUS'))
                    self.advance()
                continue

            if self.current_char == '-':
                if self.peek() == '=':
                    self.advance()  # Move past the first '-'
                    self.advance()  # Move past the second '='
                    tokens.append(self.create_token('MINUS_ASSIGN', value=None, start_pos=self.pos-2, end_pos=self.pos))
                else:
                    tokens.append(self.create_token('MINUS'))
                    self.advance()
                continue

            if self.current_char == '/':
                if self.peek() == '=':
                    self.advance()  # Move past the first '/'
                    self.advance()  # Move past the second '='
                    tokens.append(self.create_token('DIVIDE_ASSIGN', value=None, start_pos=self.pos-2, end_pos=self.pos))
                else:
                    tokens.append(self.create_token('SLASH'))
                    self.advance()
                continue
            
            if self.current_char == '{':
                tokens.append(self.create_token('LBRACE'))
                self.advance()
                continue

            if self.current_char == '}':
                tokens.append(self.create_token('RBRACE'))
                self.advance()
                continue
            
            if self.current_char == '%':
                if self.peek() == '=':
                    self.advance()  # Move past the first '%'
                    self.advance()  # Move past the second '='
                    tokens.append(self.create_token('REMAINDER_ASSIGN', value=None, start_pos=self.pos-2, end_pos=self.pos))
                else:
                    tokens.append(self.create_token('REMAINDER'))
                    self.advance()
                continue
            
            if self.current_char == '^':
                if self.peek() == '=':
                    self.advance()  # Move past the first '^'
                    self.advance()  # Move past the second '='
                    tokens.append(self.create_token('BITWISE_XOR_ASSIGN', value=None, start_pos=self.pos-2, end_pos=self.pos))
                else:
                    tokens.append(self.create_token('BITWISE_XOR'))
                    self.advance()
                continue
            
            if self.current_char == '>':
                if self.peek() == '=':
                    self.advance()  # Move past the first '>'
                    self.advance()  # Move past the second '='
                    tokens.append(self.create_token('NLT', value=None, start_pos=self.pos-2, end_pos=self.pos))
                elif self.peek() == '>':
                    self.advance()  # Move past the first '>'
                    self.advance()  # Move past the second '>'
                    tokens.append(self.create_token('BITWISE_RIGHT_SHIFT', value=None, start_pos=self.pos-2, end_pos=self.pos))
                else:
                    tokens.append(self.create_token('GT'))
                    self.advance()
                continue

            if self.current_char == '<':
                if self.peek() == '=':
                    self.advance()  # Move past the first '<'
                    self.advance()  # Move past the second '='
                    tokens.append(self.create_token('NGT', value=None, start_pos=self.pos-2, end_pos=self.pos))
                elif self.peek() == '<':
                    if self.first_n(2) == '=':
                        self.advance()  # Move past the first '<'
                        self.advance()  # Move past the second '<'
                        self.advance()  # Move past the second '='
                        tokens.append(self.create_token('BITWISE_LEFT_SHIFT_ASSIGN', value=None, start_pos=self.pos-3, end_pos=self.pos))
                    else:
                        self.advance()  # Move past the first '<'
                        self.advance()  # Move past the second '<'
                        tokens.append(self.create_token('BITWISE_LEFT_SHIFT', value=None, start_pos=self.pos-2, end_pos=self.pos))
                else:
                    tokens.append(self.create_token('LT'))
                    self.advance()
                continue

            # Check for '==' (EQUAL_EQUAL)
            if self.current_char == '=':
                if self.peek() == '=':
                    self.advance()  # Move past the first '='
                    self.advance()  # Move past the second '='
                    tokens.append(self.create_token('EQUAL', value=None, start_pos=self.pos-2, end_pos=self.pos))
                else:
                    tokens.append(self.create_token('ASSIGN'))
                    self.advance()
                continue
            
            if self.current_char == '!':
                if self.peek() == '=':
                    self.advance()  # Move past the first '!'
                    self.advance()  # Move past the second '='
                    tokens.append(self.create_token('NOTEQUAL', value=None, start_pos=self.pos-2, end_pos=self.pos))
                else:
                    tokens.append(self.create_token('NOT'))
                    self.advance()
                continue
            
            if self.current_char == '&':
                if self.peek() == '&':
                    if self.first_n(2) == '=':
                        self.advance()  # Move past the first '&'
                        self.advance()  # Move past the second '&'
                        self.advance()  # Move past the second '='
                        tokens.append(self.create_token('LOGICAL_AND_ASSIGN', value=None, start_pos=self.pos-3, end_pos=self.pos))
                    else:
                        self.advance()  # Move past the first '&'
                        self.advance()  # Move past the second '&'
                        tokens.append(self.create_token('LOGICAL_AND', value=None, start_pos=self.pos-2, end_pos=self.pos))
                elif self.peek() == '=':
                    self.advance()  # Move past the first '&'
                    self.advance()  # Move past the second '='
                    tokens.append(self.create_token('BITWISE_AND_ASSIGN', value=None, start_pos=self.pos-2, end_pos=self.pos))
                else:
                    tokens.append(self.create_token('BITWISE_AND'))
                    self.advance()
                continue
            
            if self.current_char == '|':
                if self.peek() == '|':
                    if self.first_n(2) == '=':
                        self.advance()  # Move past the first '|'
                        self.advance()  # Move past the second '|'
                        self.advance()  # Move past the second '='
                        tokens.append(self.create_token('LOGICAL_OR_ASSIGN', value=None, start_pos=self.pos-3, end_pos=self.pos))
                    else:
                        self.advance()  # Move past the first '|'
                        self.advance()  # Move past the second '|'
                        tokens.append(self.create_token('LOGICAL_OR', value=None, start_pos=self.pos-2, end_pos=self.pos))
                elif self.peek() == '=':
                    self.advance()  # Move past the first '|'
                    self.advance()  # Move past the second '='
                    tokens.append(self.create_token('BITWISE_OR_ASSIGN', value=None, start_pos=self.pos-2, end_pos=self.pos))
                elif self.peek() == '>':
                    self.advance()  # Move past the first '|'
                    self.advance()  # Move past the second '>'
                    tokens.append(self.create_token('PIPELINE', value=None, start_pos=self.pos-2, end_pos=self.pos))
                else:
                    tokens.append(self.create_token('BITWISE_OR'))
                    self.advance()
                continue
            
            if self.current_char == '~' and self.peek() == '>':
                self.advance()  # Move past the first '~'
                self.advance()  # Move past the second '>'
                tokens.append(self.create_token('COMPOSITION', value=None, start_pos=self.pos-2, end_pos=self.pos))
                continue

            raise Exception(f"Unexpected character: {self.current_char}")

        tokens.append(Token('EOF'))
        return tokens

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

    def consume_line_comment(self):
        start_pos = self.pos
        self.advance()
        self.advance()
        
        while self.current_char is not None:
            if self.current_char in ['\n', '\r']:
                break
            self.advance()
        return self.create_token("LINE_COMMENT", None, start_pos, self.pos)

    def consume_block_comment(self):
        start_pos = self.pos
        self.advance()
        self.advance()
        while self.current_char is not None:
            if self.current_char == '*' and self.peek() == '/':
                self.advance()
                self.advance()
                break
            self.advance()
        return self.create_token("BLOCK_COMMENT", None, start_pos, self.pos)

    def consume_number(self):
        """Handles both integers and floating point numbers, with possible type suffixes."""
        start_pos = self.pos
        number_str = ''
        dot_seen = False

        # Step 1: Parse the number (either integer or float)
        while self.current_char is not None and (self.current_char.isdigit() or self.current_char == '.'):
            if self.current_char == '.':
                if self.peek() == '.':
                    break
                if dot_seen:
                    raise Exception("Invalid number with multiple decimal points")
                dot_seen = True
            number_str += self.current_char
            self.advance()

        # Step 2: Check for a possible type suffix (e.g., i32, f64)
        suffix_str = ''
        while self.current_char is not None and (self.current_char.isalpha() or self.current_char.isdigit()):
            suffix_str += self.current_char
            self.advance()

        # Step 3: Determine the token type
        if dot_seen:
            token_type = 'FLOAT'
            value = float(number_str)
        else:
            token_type = 'NUMBER'
            value = int(number_str)

        # Step 4: If there is a suffix, include it in the token type
        if suffix_str:
            token_type += f"_{suffix_str}"

        return self.create_token(token_type, value, start_pos, self.pos)

    def consume_identifier(self):
        """Consume an identifier (which may also include numbers after the first character)."""
        start_pos = self.pos
        id_str = ''
        while self.current_char is not None and (self.current_char.isalnum() or self.current_char == '_'):
            id_str += self.current_char
            self.advance()
        return self.create_token('IDENTIFIER', id_str, start_pos, self.pos)

    def consume_string(self, quote_char, single_char=False, byte_string=False):
        """Consume a string literal, handling escape sequences and matching quotes."""
        start_pos = self.pos
        string_value = ''
        if single_char:
            if byte_string:
                self.advance()  # Move past 'b'
                token_type = 'BYTE_CHARACTER'
            else:
                token_type = 'CHARACTER'
        else:
            if byte_string:
                self.advance()  # Move past 'b'
                token_type = 'BYTE_STRING'
            else:
                token_type = 'STRING'

        self.advance()  # Skip the opening quote

        while self.current_char is not None and self.current_char != quote_char:
            if self.current_char == '\\':  # Handle escape sequences
                self.advance()
                if self.current_char in {'"', "'", '\\'}:
                    string_value += self.current_char
                elif self.current_char == 'n':
                    string_value += '\n'
                elif self.current_char == 't':
                    string_value += '\t'
                else:
                    raise Exception(f"Invalid escape sequence: \\{self.current_char}")
            else:
                string_value += self.current_char
            self.advance()

        if self.current_char != quote_char:
            raise Exception(f"Unterminated string literal starting at position {start_pos}")

        self.advance()  # Skip the closing quote
        return self.create_token(token_type, string_value, start_pos, self.pos)
