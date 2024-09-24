from enum import Enum
from typing import Tuple


class Level(Enum):
    NOTE = 1
    WARNING = 2
    EXTENSION = 3
    EXTWARN = 4
    ERROR = 5

def get_line_column(input_str, char_pos) -> Tuple[int, int]:
    lines = input_str.split('\n')
    
    line_count = 1
    for index, line in enumerate(lines):
        if char_pos <= len(line):
            column = char_pos
            break
        char_pos -= len(line) + 1
        line_count += 1

    return line_count, column

class SourceLocation:
    def __init__(self, file_name: str, line: int, column: int):
        self.file_name: str = file_name
        self.line: str = line
        self.column: str = column
    
    @staticmethod
    def from_tuple(file_name: str, lc: Tuple[int, int]) -> "SourceLocation":
        return SourceLocation(file_name=file_name, line=lc[0], column=lc[1])

    def __str__(self):
        return f"File: {self.file_name}, Line: {self.line}, Column: {self.column}"

    def __eq__(self, other):
        if isinstance(other, SourceLocation):
            return self.file_name == other.file_name and self.line == other.line and self.column == other.column
        return False

    def __lt__(self, other):
        if isinstance(other, SourceLocation):
            if self.file_name == other.file_name:
                if self.line == other.line:
                    return self.column < other.column
                return self.line < other.line
            return self.file_name < other.file_name
        raise NotImplementedError

class Diagnostic:
    def __init__(
        self,
        severity: Level,
        message: str,
        position: SourceLocation,
        category: str,
    ):
        self.severity = severity
        self.message = message
        self.position = position
        self.category = category
    
    # "Semantic Issue", "Parse Issue", "Lexical Issue", "Preprocessor Issue", 
    
    
    def __str__(self):
        return f"Severity: {self.severity}, Message: {self.message}, Position: {self.position}, Category: {self.category}"

    def __eq__(self, other):
        if isinstance(other, Diagnostic):
            return self.severity == other.severity and self.message == other.message and self.position == other.position and self.category == other.category
        return False
