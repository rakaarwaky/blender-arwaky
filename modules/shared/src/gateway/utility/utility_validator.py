"""Utility: AST-based code validation for Blender code execution.

Stateless standalone functions that analyze Python code using the
ast module to detect blocked patterns. More reliable than regex.
Domain-agnostic — reusable across modules.
Implements v2.0.0 security policy with CodeSecurityPolicy VO.
"""

from __future__ import annotations

import ast
import hashlib
from typing import Final

from modules.shared.src.gateway.taxonomy_gateway_error import SecurityViolationError
from modules.shared.src.gateway.taxonomy_gateway_vo import CodeSecurityPolicy

# ─── Blocked Modules ──────────────────────────────────────────────

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

# ─── Blocked Functions ────────────────────────────────────────────

_BLOCKED_FUNCTIONS: Final[frozenset[str]] = frozenset({
    "eval",
    "exec",
    "compile",
    "__import__",
    "breakpoint",
    "exit",
    "quit",
    "globals",
    "locals",
    "vars",
    "getattr",
    "setattr",
    "delattr",
})

# ─── Blocked Attributes ──────────────────────────────────────────

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

# ─── File Write Modes ────────────────────────────────────────────

_WRITE_MODES: Final[frozenset[str]] = frozenset({"w", "a", "x", "+", "wb", "wa", "wx", "w+b", "a+b", "x+b"})


def validate_code_ast(code: str, policy: CodeSecurityPolicy | None = None) -> None:
    """Validate Python code using AST analysis for blocked patterns.

    Raises SecurityViolationError if code contains forbidden constructs.
    This is a pre-filter, not a security boundary — Blender addon
    enforces runtime restrictions.

    Args:
        code: The Python code string to validate.
        policy: Optional security policy with allowed directories and payload limits.

    Raises:
        SecurityViolationError: If code contains blocked patterns or writes outside allowed dirs.
    """
    if not code or not code.strip():
        raise SecurityViolationError(details={"rule": "empty_code"})

    try:
        tree = ast.parse(code)
    except SyntaxError as e:
        raise SecurityViolationError(
            message=f"Syntax error in code: {e.msg} at line {e.lineno}",
            details={"rule": "syntax_error", "line": e.lineno},
        ) from e

    allowed_dirs = set(policy.allowed_directories) if policy else set()

    for node in ast.walk(tree):
        _check_node(node, allowed_dirs)


def _check_node(node: ast.AST, allowed_dirs: set[str]) -> None:
    """Check a single AST node for blocked patterns."""
    # Check imports
    if isinstance(node, ast.Import):
        for alias in node.names:
            mod = alias.name.split(".")[0]
            if mod in _BLOCKED_MODULES:
                raise SecurityViolationError(
                    message=f"Blocked import: {alias.name}",
                    details={"rule": "blocked_module_import", "module": alias.name},
                )

    elif isinstance(node, ast.ImportFrom):
        if node.module:
            mod = node.module.split(".")[0]
            if mod in _BLOCKED_MODULES:
                raise SecurityViolationError(
                    message=f"Blocked import from: {node.module}",
                    details={"rule": "blocked_module_import", "module": node.module},
                )

    # Check function calls and attribute access
    elif isinstance(node, ast.Call):
        func = node.func
        # Direct function call: eval(), exec(), open(), etc.
        if isinstance(func, ast.Name):
            if func.id in _BLOCKED_FUNCTIONS:
                raise SecurityViolationError(
                    message=f"Blocked function call: {func.id}()",
                    details={"rule": "blocked_function_call", "function": func.id},
                )
            # Check open() with write mode — validate against allowed directories
            if func.id == "open":
                _check_file_write(node, allowed_dirs)
        # Attribute call: os.system(), getattr(...), etc.
        elif isinstance(func, ast.Attribute):
            if func.attr in _BLOCKED_FUNCTIONS:
                raise SecurityViolationError(
                    message=f"Blocked method call: .{func.attr}()",
                    details={"rule": "blocked_function_call", "function": func.attr},
                )
            # Check .open() with write mode — validate against allowed directories
            if func.attr == "open":
                _check_file_write(node, allowed_dirs)

    # Check attribute access (dunder methods, etc.)
    elif isinstance(node, ast.Attribute):
        if node.attr in _BLOCKED_ATTRIBUTES:
            raise SecurityViolationError(
                message=f"Blocked attribute access: .{node.attr}",
                details={"rule": "blocked_attribute_access", "attribute": node.attr},
            )


def _check_file_write(call_node: ast.Call, allowed_dirs: set[str]) -> None:
    """Check open() calls for write mode against allowed directories.

    Read-only open is always allowed. Write operations must be inside
    an allowed directory (literal path only). Dynamic paths always rejected.
    """
    import os

    mode_val = ""
    path_arg = None

    # Extract path and mode from open(path, mode) or open(path, mode=...)
    # Correct: open(path, mode) — args[0] is path
    if call_node.args:
        path_arg = call_node.args[0]
    for kw in call_node.keywords:
        if kw.arg == "mode" and isinstance(kw.value, ast.Constant):
            mode_val = str(kw.value.value)

    # If we have a positional mode argument (args[1])
    if len(call_node.args) >= 2 and not mode_val:
        if isinstance(call_node.args[1], ast.Constant):
            mode_val = str(call_node.args[1].value)

    # Check if this is a write operation
    if any(m in mode_val for m in _WRITE_MODES):
        # If path is a string literal, check against allowed directories
        if isinstance(path_arg, ast.Constant) and isinstance(path_arg.value, str):
            file_path = path_arg.value
            normalized = os.path.normpath(os.path.abspath(file_path))

            # Check if path is inside any allowed directory
            for allowed_dir in allowed_dirs:
                normalized_allowed = os.path.normpath(os.path.abspath(allowed_dir))
                if normalized.startswith(normalized_allowed + os.sep) or normalized == normalized_allowed:
                    return  # Path is inside allowed directory — permit

            # Path not inside any allowed directory
            raise SecurityViolationError(
                message=f"File write to '{file_path}' — path must be inside allowed directory",
                details={"rule": "file_write_outside_allowed_directory", "path": file_path},
            )
        elif path_arg is not None:
            # Dynamic path — always reject
            raise SecurityViolationError(
                message="Dynamic file write path not allowed",
                details={"rule": "dynamic_file_write_path_not_allowed"},
            )


def check_payload_size(code: str, max_bytes: int) -> None:
    """Validate code payload size. Raises SecurityViolationError if too large."""
    code_bytes = len(code.encode("utf-8"))
    if code_bytes > max_bytes:
        raise SecurityViolationError(
            message=(
                f"Code payload exceeds maximum size: {code_bytes} bytes "
                f"(max: {max_bytes})"
            ),
            details={"rule": "payload_too_large", "size": code_bytes, "max": max_bytes},
        )


def code_fingerprint(code: str) -> str:
    """Return SHA-256 hex digest prefix of code (max 16 chars).

    Never returns raw code. Used for logging code identity without
    exposing user content.
    """
    digest = hashlib.sha256(code.encode("utf-8")).hexdigest()
    return digest[:16]
