from distutils.command.build_ext import build_ext


def get_export_symbols_fixed(self, ext):
    pass  # return [] also does the job!


# replace wrong version with the fixed:
build_ext.get_export_symbols = get_export_symbols_fixed

from setuptools import find_packages, setup, Extension
from Cython.Build import cythonize
from Cython.Compiler import Options

# These are optional
Options.docstrings = True
Options.annotate = False

# Modules to be compiled and include_dirs when necessary
extensions = [
    Extension(
        "*",
        [
            "src/cjlang/ast/node.py",
            "src/cjlang/ast/tree.py",
            "src/cjlang/diagnostics/diagnostic.py",
            "src/cjlang/diagnostics/engine.py",
            "src/cjlang/lexer/cursor.py",
            "src/cjlang/lexer/kinds.py",
            "src/cjlang/parser/parser.py",
            "src/cjlang/utils/__init__.py",
        ],
        include_dirs=[],
    ),
]


# This is the function that is executed
setup(
    name="cjlang",  # Required
    packages=find_packages("src"),
    package_dir={"": "src"},
    # A list of compiler Directives is available at
    # https://cython.readthedocs.io/en/latest/src/userguide/source_files_and_compilation.html#compiler-directives
    # external to be compiled
    ext_modules=cythonize(
        extensions,
        annotate=True,
        compiler_directives={"language_level": 3, "profile": False},
    ),
)
