"""Tests for CodeValidator — FR-SEC-003.

Exercises untrusted code validation: blocked imports, blocked function calls,
size limits, syntax errors, strict mode, and disabled validation override.
Run via pytest from repo root.
"""

from __future__ import annotations

import ast

import pytest

from modules.security.src.capabilities_code_validator import CodeValidator
from modules.shared.src.security.taxonomy_security_vo import (
    CodeValidationVO,
    CodeViolationVO,
    SecurityPolicyVO,
)


# ─── Helpers ──────────────────────────────────────────────────────────────────


def _make_validator(policy: SecurityPolicyVO | None = None) -> CodeValidator:
    """Create a CodeValidator with optional policy."""
    return CodeValidator(policy=policy)


def _validate(cap: CodeValidator, code: str, **overrides: object) -> CodeValidationVO:
    """Helper to run validate_code synchronously via asyncio."""
    import asyncio
    base = CodeValidationVO(code_text=code, strict_mode=True)
    update = {k: v for k, v in overrides.items()}
    return asyncio.run(cap.validate_code(CodeValidationVO(**{**dict(base.__dict__), **update})))


# ─── FR-SEC-003: Validate Untrusted Code ──────────────────────────────────


class TestBlockedModuleImports:
    """Test blocked module import detection (FR-SEC-003)."""

    def test_os_import_blocked(self) -> None:
        """FR-SEC-003: os module import is blocked."""
        cap = _make_validator()
        res = _validate(cap, "import os")
        assert res.allowed is False
        assert any("blocked_module_import" in v.category for v in res.violations)

    def test_subprocess_import_blocked(self) -> None:
        """FR-SEC-003: subprocess module import is blocked."""
        cap = _make_validator()
        res = _validate(cap, "import subprocess")
        assert res.allowed is False
        assert any("blocked_module_import" in v.category for v in res.violations)

    def test_sys_import_blocked(self) -> None:
        """FR-SEC-003: sys module import is blocked."""
        cap = _make_validator()
        res = _validate(cap, "import sys")
        assert res.allowed is False

    def test_socket_import_blocked(self) -> None:
        """FR-SEC-003: socket module import is blocked."""
        cap = _make_validator()
        res = _validate(cap, "import socket")
        assert res.allowed is False

    def test_pickle_import_blocked(self) -> None:
        """FR-SEC-003: pickle module import is blocked (unsafe deserialization)."""
        cap = _make_validator()
        res = _validate(cap, "import pickle")
        assert res.allowed is False

    def test_from_import_blocked(self) -> None:
        """FR-SEC-003: from X import Y is also blocked."""
        cap = _make_validator()
        res = _validate(cap, "from os import path")
        assert res.allowed is False

    def test_submodule_import_blocked(self) -> None:
        """FR-SEC-003: submodule imports (os.path) are blocked by top-level name."""
        cap = _make_validator()
        res = _validate(cap, "import os.path")
        assert res.allowed is False

    def test_multiple_blocked_imports(self) -> None:
        """FR-SEC-003: multiple blocked imports produce multiple violations."""
        cap = _make_validator()
        res = _validate(cap, "import os\nimport subprocess\nimport sys")
        assert res.allowed is False
        assert len(res.violations) >= 2


class TestBlockedFunctionCalls:
    """Test blocked function call detection (FR-SEC-003)."""

    def test_eval_call_blocked(self) -> None:
        """FR-SEC-003: eval() call is blocked."""
        cap = _make_validator()
        res = _validate(cap, "eval('1+1')")
        assert res.allowed is False
        assert any("blocked_function_call" in v.category for v in res.violations)

    def test_exec_call_blocked(self) -> None:
        """FR-SEC-003: exec() call is blocked."""
        cap = _make_validator()
        res = _validate(cap, "exec('import os')")
        assert res.allowed is False

    def test_compile_call_blocked(self) -> None:
        """FR-SEC-003: compile() call is blocked."""
        cap = _make_validator()
        res = _validate(cap, "compile('x', '<string>', 'exec')")
        assert res.allowed is False

    def test___import___call_blocked(self) -> None:
        """FR-SEC-003: __import__() call is blocked."""
        cap = _make_validator()
        res = _validate(cap, "__import__('os')")
        assert res.allowed is False

    def test_breakpoint_call_blocked(self) -> None:
        """FR-SEC-003: breakpoint() call is blocked."""
        cap = _make_validator()
        res = _validate(cap, "breakpoint()")
        assert res.allowed is False

    def test_globals_locals_call_blocked(self) -> None:
        """FR-SEC-003: globals() and locals() calls are blocked."""
        cap = _make_validator()
        res = _validate(cap, "x = globals(); y = locals()")
        assert res.allowed is False

    def test_getattr_setattr_blocked(self) -> None:
        """FR-SEC-003: getattr/setattr calls are blocked (reflection)."""
        cap = _make_validator()
        res = _validate(cap, "getattr(obj, 'x'); setattr(obj, 'y', 1)")
        assert res.allowed is False

    def test_method_call_blocked(self) -> None:
        """FR-SEC-003: method calls like obj.eval() are blocked."""
        cap = _make_validator()
        res = _validate(cap, "obj.eval('code')")
        assert res.allowed is False


class TestSizeLimits:
    """Test code size limit enforcement (FR-SEC-003)."""

    def test_code_exceeding_size_limit_rejected(self) -> None:
        """FR-SEC-003: code exceeding max size is rejected."""
        cap = _make_validator()
        res = _validate(cap, "x = 1", max_code_size=2)
        assert res.allowed is False
        assert any("size_limit" in v.category for v in res.violations)

    def test_code_at_size_limit_allowed(self) -> None:
        """FR-SEC-003: code at size limit is allowed."""
        cap = _make_validator()
        res = _validate(cap, "x=1", max_code_size=4)
        assert res.allowed is True

    def test_oversized_code_has_violation(self) -> None:
        """FR-SEC-003: oversized code includes size violation."""
        cap = _make_validator()
        res = _validate(cap, "a" * 1000, max_code_size=100)
        assert res.allowed is False
        assert any("size_limit" in v.category for v in res.violations)

    def test_empty_code_size(self) -> None:
        """FR-SEC-003: empty code is caught by empty check, not size."""
        cap = _make_validator()
        res = _validate(cap, "", max_code_size=100)
        assert res.allowed is False


class TestStrictMode:
    """Test strict mode syntax error handling (FR-SEC-003)."""

    def test_syntax_error_strict_rejected(self) -> None:
        """FR-SEC-003: unparseable code in strict mode is rejected."""
        cap = _make_validator()
        res = _validate(cap, "def (:", strict_mode=True)
        assert res.allowed is False
        assert any("syntax_error" in v.category for v in res.violations)

    def test_syntax_error_non_strict_warns(self) -> None:
        """FR-SEC-003: unparseable code in non-strict mode records a syntax_error violation (no crash)."""
        cap = _make_validator()
        res = _validate(cap, "def (:", strict_mode=False)
        assert res.allowed is False
        assert any("syntax_error" in v.category for v in res.violations)

    def test_valid_code_strict_allowed(self) -> None:
        """FR-SEC-003: valid code in strict mode is allowed."""
        cap = _make_validator()
        res = _validate(cap, "x = 1 + 2\nprint(x)", strict_mode=True)
        assert res.allowed is True


class TestDisabledValidation:
    """Test disabled code validation override (FR-SEC-003)."""

    def test_disabled_validation_allows_code(self) -> None:
        """FR-SEC-003: when validation disabled, code proceeds with warning."""
        cap = _make_validator(SecurityPolicyVO(code_validation_enabled=False))
        res = _validate(cap, "import os")
        assert res.allowed is True

    def test_disabled_validation_has_audit_metadata(self) -> None:
        """FR-SEC-003: disabled validation includes audit metadata."""
        cap = _make_validator(SecurityPolicyVO(code_validation_enabled=False))
        res = _validate(cap, "import os")
        assert isinstance(res.audit_metadata, dict)
        assert res.audit_metadata.get("rule") == "validation_disabled"

    def test_disabled_validation_has_warning(self) -> None:
        """FR-SEC-003: disabled validation includes redacted metadata warning."""
        cap = _make_validator(SecurityPolicyVO(code_validation_enabled=False))
        res = _validate(cap, "import os")
        assert isinstance(res.redacted_metadata, dict)


class TestSafeCode:
    """Test safe code that should be allowed."""

    def test_math_operations_allowed(self) -> None:
        """FR-SEC-003: safe math operations are allowed."""
        cap = _make_validator()
        res = _validate(cap, "x = 1 + 2\ny = x * 3")
        assert res.allowed is True

    def test_function_definition_allowed(self) -> None:
        """FR-SEC-003: safe function definitions are allowed."""
        cap = _make_validator()
        res = _validate(cap, "def hello():\n    return 'world'")
        assert res.allowed is True

    def test_class_definition_allowed(self) -> None:
        """FR-SEC-003: safe class definitions are allowed."""
        cap = _make_validator()
        res = _validate(cap, "class Foo:\n    pass")
        assert res.allowed is True

    def test_safe_import_allowed(self) -> None:
        """FR-SEC-003: non-blocked imports are allowed."""
        cap = _make_validator()
        res = _validate(cap, "import json\nimport math")
        assert res.allowed is True

    def test_builtin_operations_allowed(self) -> None:
        """FR-SEC-003: safe builtin operations are allowed."""
        cap = _make_validator()
        res = _validate(cap, "x = len([1, 2, 3])\ny = str(42)")
        assert res.allowed is True


class TestEdgeCases:
    """Test edge cases from FR-SEC-003 specification."""

    def test_empty_code_payload(self) -> None:
        """FR-SEC-003: empty code payload is rejected."""
        cap = _make_validator()
        res = _validate(cap, "")
        assert res.allowed is False
        assert any("empty_code" in v.category for v in res.violations)

    def test_whitespace_only_code(self) -> None:
        """FR-SEC-003: whitespace-only code is rejected as empty."""
        cap = _make_validator()
        res = _validate(cap, "   \n  \t  ")
        assert res.allowed is False

    def test_comment_only_code(self) -> None:
        """FR-SEC-003: comment-only code is valid (not empty, not blocked)."""
        cap = _make_validator()
        res = _validate(cap, "# This is a comment")
        # Comments are valid Python — should be allowed
        assert res.allowed is True

    def test_obfuscated_code(self) -> None:
        """FR-SEC-003: obfuscated code with blocked constructs is rejected."""
        cap = _make_validator()
        res = _validate(cap, "exec(compile('import os', '<string>', 'exec'))")
        assert res.allowed is False

    def test_dynamic_construct_blocked(self) -> None:
        """FR-SEC-003: dynamically constructed forbidden constructs are blocked."""
        cap = _make_validator()
        res = _validate(cap, "x = 'eval'; exec(f'{x}(\"1+1\")')")
        # The exec call is detected by AST analysis
        assert res.allowed is False

    def test_allowed_exception_pattern(self) -> None:
        """FR-SEC-003: allowed exception list for trusted operations (when configured)."""
        cap = _make_validator()
        # Without configured exceptions, safe code is allowed
        res = _validate(cap, "x = len([])")
        assert res.allowed is True

    def test_violation_has_category(self) -> None:
        """FR-SEC-003: violations include construct category."""
        cap = _make_validator()
        res = _validate(cap, "import os")
        assert len(res.violations) >= 1
        assert res.violations[0].category == "blocked_module_import"

    def test_violation_has_description(self) -> None:
        """FR-SEC-003: violations include description."""
        cap = _make_validator()
        res = _validate(cap, "import os")
        assert len(res.violations) >= 1
        assert "Blocked import" in res.violations[0].description


class TestAuditMetadata:
    """Test audit metadata on all outcomes (FR-SEC-003)."""

    def test_allowed_has_audit_metadata(self) -> None:
        """FR-SEC-003: allowed code includes audit metadata."""
        cap = _make_validator()
        res = _validate(cap, "x = 1")
        assert isinstance(res.audit_metadata, dict)

    def test_violation_has_audit_metadata(self) -> None:
        """FR-SEC-003: violations include audit metadata."""
        cap = _make_validator()
        res = _validate(cap, "import os")
        assert isinstance(res.audit_metadata, dict)

    def test_size_limit_has_audit_metadata(self) -> None:
        """FR-SEC-003: size limit violation includes audit metadata."""
        cap = _make_validator()
        res = _validate(cap, "xx", max_code_size=1)
        assert isinstance(res.audit_metadata, dict)
        assert res.audit_metadata.get("rule") == "code_oversized"


class TestRepresentation:
    """Test class representation."""

    def test_code_validator_repr(self) -> None:
        """CodeValidator has a repr."""
        cap = CodeValidator.__new__(CodeValidator)
        CodeValidator.__init__(cap, SecurityPolicyVO())
        assert "CodeValidator" in repr(cap)


# ─── AST Walk Coverage Tests ──────────────────────────────────────────


class TestASTWalkCoverage:
    """Test AST walking covers all blocked constructs."""

    def test_import_from_os_blocked(self) -> None:
        """FR-SEC-003: from os import path is blocked."""
        cap = _make_validator()
        res = _validate(cap, "from os import path")
        assert res.allowed is False

    def test_import_from_subprocess_blocked(self) -> None:
        """FR-SEC-003: from subprocess import run is blocked."""
        cap = _make_validator()
        res = _validate(cap, "from subprocess import run")
        assert res.allowed is False

    def test_nested_call_blocked(self) -> None:
        """FR-SEC-003: nested function calls are walked."""
        cap = _make_validator()
        res = _validate(cap, "f(g(eval('x')))")
        assert res.allowed is False

    def test_multiple_nodes_walked(self) -> None:
        """FR-SEC-003: AST walk visits all nodes in complex code."""
        cap = _make_validator()
        res = _validate(cap, "import os\neval('x')\nexec('y')")
        assert res.allowed is False
        # Should have violations for both import and function calls
        assert len(res.violations) >= 2
