from typing import List

from cjlang.diagnostics.diagnostic import Diagnostic, Level, SourceLocation


class DiagnosticEngine:

    def __init__(self):
        self.diagnostics: List[Diagnostic] = []

    def report(
        self,
        severity: Level,
        message: str,
        position: SourceLocation,
        category: str,
    ):
        self.diagnostics.append(
            Diagnostic(
                severity=severity, message=message, position=position, category=category
            )
        )
    
    def note(
        self,
        message: str,
        position: SourceLocation,
        category: str,
    ):
        self.diagnostics.append(
            Diagnostic(
                severity=Level.NOTE, message=message, position=position, category=category
            )
        )


    def warning(
        self,
        message: str,
        position: SourceLocation,
        category: str,
    ):
        self.diagnostics.append(
            Diagnostic(
                severity=Level.WARNING, message=message, position=position, category=category
            )
        )

    def error(
        self,
        message: str,
        position: SourceLocation,
        category: str,
    ):
        self.diagnostics.append(
            Diagnostic(
                severity=Level.ERROR, message=message, position=position, category=category
            )
        )

    def has_errors(self) -> bool:
        return any(
            diagnostic.severity == Level.ERROR
            for diagnostic in self.diagnostics
        )

    def show_diagnostics(self):
        for diagnostic in self.diagnostics:
            print(f"{diagnostic.severity.name.upper()}: {diagnostic.message}")
