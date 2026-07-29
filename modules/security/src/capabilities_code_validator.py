"""Capabilities: Code validator — FR-SEC-003.

Validates untrusted code using AST analysis and blocked construct policy.
Implements ValidateCodeProtocol.
"""

from __future__ import annotations

import ast

from modules.shared.src.security.contract_validate_code_protocol import ValidateCodeProtocol
from modules.shared.src.security.taxonomy_security_vo import (
    CodeValidationVO,
    CodeViolationVO,
    SecurityPolicyVO,
)


class CodeValidator(ValidateCodeProtocol):
    """Validates untrusted code before execution using static AST analysis."""

    # ─── Block 1: Class Definition & Constructor ──────────────
    def __init__(
        self,
        policy: SecurityPolicyVO | None = None,
    ) -> None:
        self._policy = policy

    # ─── Block 2: Public Contract  ────────────────────────
    async def validate_code(self, request: CodeValidationVO) -> CodeValidationVO:
        """Validate untrusted code using static analysis and blocked construct policy."""
        violations: list[CodeViolationVO] = []

        code_bytes = len(request.code_text.encode("utf-8"))
        if code_bytes > request.max_code_size:
            return CodeValidationVO(
                code_text=request.code_text,
                max_code_size=request.max_code_size,
                strict_mode=request.strict_mode,
                execution_context=request.execution_context,
                allowed=False,
                violations=(CodeViolationVO(category="size_limit", description=f"Code too large: {code_bytes} > {request.max_code_size}"),),
                audit_metadata={"rule": "code_oversized", "size": code_bytes},
            )

        if not request.code_text or not request.code_text.strip():
            return CodeValidationVO(
                code_text=request.code_text,
                max_code_size=request.max_code_size,
                strict_mode=request.strict_mode,
                allowed=False,
                violations=(CodeViolationVO(category="empty_code", description="Empty code payload"),),
                audit_metadata={"rule": "empty_code"},
            )

        if self._policy and not self._policy.code_validation_enabled:
            return CodeValidationVO(
                code_text=request.code_text,
                max_code_size=request.max_code_size,
                strict_mode=request.strict_mode,
                execution_context=request.execution_context,
                allowed=True,
                redacted_metadata={"warning": "Code validation disabled by policy"},
                audit_metadata={"rule": "validation_disabled"},
            )

        try:
            tree = ast.parse(request.code_text)
        except SyntaxError as exc:
            if request.strict_mode:
                return CodeValidationVO(
                    code_text=request.code_text,
                    max_code_size=request.max_code_size,
                    strict_mode=request.strict_mode,
                    allowed=False,
                    violations=(CodeViolationVO(category="syntax_error", description=f"Syntax error: {exc.msg} at line {exc.lineno}", location_hint=f"line {exc.lineno}"),),
                    audit_metadata={"rule": "syntax_error", "line": exc.lineno},
                )
            violations.append(CodeViolationVO(category="syntax_error", description=f"Syntax error: {exc.msg}", location_hint=f"line {exc.lineno}"))
            # Non-strict mode records the syntax error as a violation and stops:
            # an unparseable tree cannot be walked, so do not fall through to ast.walk.
            return CodeValidationVO(
                code_text=request.code_text,
                max_code_size=request.max_code_size,
                strict_mode=request.strict_mode,
                allowed=False,
                violations=tuple(violations),
                audit_metadata={"rule": "syntax_error", "line": exc.lineno},
            )

        blocked_modules, blocked_functions = self._build_blocked_set()

        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    mod = alias.name.split(".")[0]
                    if mod in blocked_modules:
                        violations.append(CodeViolationVO(category="blocked_module_import", description=f"Blocked import: {alias.name}"))
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    mod = node.module.split(".")[0]
                    if mod in blocked_modules:
                        violations.append(CodeViolationVO(category="blocked_module_import", description=f"Blocked import from: {node.module}"))
            elif isinstance(node, ast.Call):
                func = node.func
                if isinstance(func, ast.Name) and func.id in blocked_functions:
                    violations.append(CodeViolationVO(category="blocked_function_call", description=f"Blocked function call: {func.id}()"))
                elif isinstance(func, ast.Attribute) and func.attr in blocked_functions:
                    violations.append(CodeViolationVO(category="blocked_function_call", description=f"Blocked method call: .{func.attr}()"))

        allowed = len(violations) == 0
        return CodeValidationVO(
            code_text=request.code_text,
            max_code_size=request.max_code_size,
            strict_mode=request.strict_mode,
            execution_context=request.execution_context,
            allowed=allowed,
            violations=tuple(violations),
            audit_metadata={"violation_count": len(violations)},
        )

    # ─── Block 3: Dunder Methods, Factories & Helpers ─────
    def _build_blocked_set(self) -> tuple[frozenset[str], frozenset[str]]:
        """Build blocked modules/functions from policy, falling back to defaults."""
        if self._policy and self._policy.blocked_code_constructs:
            modules = set()
            functions = set()
            for construct in self._policy.blocked_code_constructs:
                if construct in {
                    "os", "subprocess", "shutil", "importlib", "sys",
                    "socket", "ctypes", "multiprocessing", "threading",
                    "signal", "pickle",
                }:
                    modules.add(construct)
                else:
                    functions.add(construct)
            return frozenset(modules), frozenset(functions)

        # Defaults (preserved for backward compatibility)
        return (
            frozenset({"os", "subprocess", "shutil", "importlib", "sys",
                        "socket", "ctypes", "multiprocessing", "threading",
                        "signal", "pickle"}),
            frozenset({"eval", "exec", "compile", "__import__", "breakpoint",
                       "globals", "locals", "getattr", "setattr", "delattr"}),
        )

    def __repr__(self) -> str:
        return "CodeValidator()"
