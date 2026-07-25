"""Utility: AST-based code validation for Blender code execution.

Stateless standalone functions that analyze Python code using the
ast module to detect blocked patterns. More reliable than regex.
Domain-agnostic — reusable across modules.
"""

import ast
from typing import Final

from ..common.taxonomy_core_vo import ErrorMessage
from .taxonomy_server_error import SecurityViolationError

# Blocked module names — dangerous system-level imports
_BLOCKED_MODULES: Final[frozenset[str]] = frozenset({
    "os",
    "subprocess",
    "shutil",
    "importlib",
    "sys",
    "socket",
    "urllib",
    "requests",
    "ctypes",
    "multiprocessing",
    "threading",
    "signal",
    "pickle",
    "shelve",
})

# Blocked function names — dangerous builtins and system calls
_BLOCKED_FUNCTIONS: Final[frozenset[str]] = frozenset({
    "eval",
    "exec",
    "compile",
    "__import__",
    "breakpoint",
    "exit",
    "quit",
    "open",
})

# Blocked attribute names — unsafe dunder access
_BLOCKED_ATTRIBUTES: Final[frozenset[str]] = frozenset({
    "__subclasses__",
    "__bases__",
    "__mro__",
    "__globals__",
    "__builtins__",
    "__import__",
    "__loader__",
    "__spec__",
    "__file__",
    "__name__",
    "__package__",
})


def validate_code_ast(code: str) -> None:
    """Validate Python code using AST analysis for blocked patterns.

    Raises SecurityViolationError if code contains forbidden constructs.
    This is a pre-filter, not a security boundary — Blender addon
    enforces runtime restrictions.
    """
    if not code or not code.strip():
        raise SecurityViolationError(ErrorMessage("Code cannot be empty"))

    try:
        tree = ast.parse(code)
    except SyntaxError as e:
        raise SecurityViolationError(
            ErrorMessage(f"Syntax error in code: {e.msg} at line {e.lineno}")
        ) from e

    for node in ast.walk(tree):
        _check_node(node)


def _check_node(node: ast.AST) -> None:
    """Check a single AST node for blocked patterns."""
    if isinstance(node, ast.Import):
        for alias in node.names:
            mod = alias.name.split(".")[0]
            if mod in _BLOCKED_MODULES:
                raise SecurityViolationError(
                    ErrorMessage(f"Blocked import: {alias.name}")
                )

    elif isinstance(node, ast.ImportFrom):
        if node.module:
            mod = node.module.split(".")[0]
            if mod in _BLOCKED_MODULES:
                raise SecurityViolationError(
                    ErrorMessage(f"Blocked import from: {node.module}")
                )

    elif isinstance(node, ast.Call):
        func = node.func
        if isinstance(func, ast.Name) and func.id in _BLOCKED_FUNCTIONS:
            raise SecurityViolationError(
                ErrorMessage(f"Blocked function call: {func.id}()")
            )
        elif isinstance(func, ast.Attribute) and func.attr in _BLOCKED_FUNCTIONS:
            raise SecurityViolationError(
                ErrorMessage(f"Blocked method call: .{func.attr}()")
            )

    elif isinstance(node, ast.Attribute):
        if node.attr in _BLOCKED_ATTRIBUTES:
            raise SecurityViolationError(
                ErrorMessage(f"Blocked attribute access: .{node.attr}")
            )


def check_payload_size(code: str, max_bytes: int) -> None:
    """Validate code payload size. Raises SecurityViolationError if too large."""
    code_bytes = len(code.encode("utf-8"))
    if code_bytes > max_bytes:
        raise SecurityViolationError(
            ErrorMessage(
                f"Code payload exceeds maximum size: {code_bytes} bytes "
                f"(max: {max_bytes})"
            )
        )
