
from enum import Enum

class TokenKind(Enum):
    EOF = "EOF"
    WS = "WHITESPACE"
    NL = "NL"
    
    RAW_IDENT = "RAW_IDENT"
    IDENT = "IDENT"
    
    LINE_COMMENT = "LINE_COMMENT"
    DELIMITED_COMMENT = "DELIMITED_COMMENT"
    
    BINARY_LITERAL = "BINARY_LITERAL"
    OCTAL_LITERAL = "OCTAL_LITERAL"
    DECIMAL_LITERAL = "DECIMAL_LITERAL"
    HEXADECIMAL_LITERAL = "HEXADECIMAL_LITERAL"
    FLOAT_LITERAL = "FLOAT_LITERAL"
    
    LINE_STRING_LITERAL = "LINE_STRING_LITERAL"
    MULTI_LINE_STRING_LITERAL = "MULTI_LINE_STRING_LITERAL"
    BYTE_STRING = "BYTE_STRING"
    BYTE_STRING_ARRAY_LITERAL = "BYTE_STRING_ARRAY_LITERAL"
    BYTE_LITERAL = "BYTE_LITERAL"
    RUNE_LITERAL = "RUNE_LITERAL"
    
    COALESCING = '??'
    
    DOT = '.'
    COMMA = ','
    LPAREN = '('
    RPAREN = ')'
    LSQUARE = '['
    RSQUARE = ']'
    LCURL = '{'
    RCURL = '}'
    EXP = '**'
    MUL = '*'
    MOD = '%'
    DIV = '/'
    ADD = '+'
    SUB = '-'
    PIPELINE = '|>'
    COMPOSITION = '~>'
    INC = '++'
    DEC = '--'
    AND = '&&'
    OR = '||'
    NOT = '!'
    BITAND = '&'
    BITOR = '|'
    BITXOR = '^'
    LSHIFT = '<<'
    RSHIFT = '>>'
    COLON = ':'
    SEMI = ';'
    ASSIGN = '='
    ADD_ASSIGN = '+='
    SUB_ASSIGN = '-='
    MUL_ASSIGN = '*='
    EXP_ASSIGN = '**='
    DIV_ASSIGN = '/='
    MOD_ASSIGN = '%='
    AND_ASSIGN = '&&='
    OR_ASSIGN = '||='
    BITAND_ASSIGN = '&='
    BITOR_ASSIGN = '|='
    BITXOR_ASSIGN = '^='
    LSHIFT_ASSIGN = '<<='
    RSHIFT_ASSIGN = '>>='
    ARROW = '->'
    BACKARROW = '<-'
    DOUBLE_ARROW = '=>'
    ELLIPSIS = '...'
    CLOSEDRANGEOP = '..='
    RANGEOP = '..'
    HASH = '#'
    AT = '@'
    QUEST = '?'
    UPPERBOUND = '<:'
    LT = '<'
    GT = '>'
    LE = '<='
    GE = '>='
    NOTEQUAL = '!='
    EQUAL = '=='
    WILDCARD = '_'
    BACKSLASH = '\\'
    QUOTESYMBOL = '`'
    DOLLAR = '$'
    QUOTE_OPEN = '"'
    TRIPLE_QUOTE_OPEN = '"""'
    QUOTE_CLOSE = '"'
    TRIPLE_QUOTE_CLOSE = '"""'
    LineStrExprStart = '${'
    MultiLineStrExprStart = '${'
