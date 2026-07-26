"""Unit tests for server utility functions.

Tests AST validation, payload size checking, code fingerprinting,
command schema validation, config loading, and ID generation.
"""

from __future__ import annotations

import os
import time
from unittest.mock import MagicMock, patch

import pytest

from modules.shared.src.server import (
    CodeSecurityPolicy,
    ExecutionTimeoutError,
    SecurityViolationError,
    ServerCommandSpec,
    ValidationError,
    check_payload_size,
    code_fingerprint,
    effective_command_timeout_ms,
    get_command_spec,
    is_scene_mutating,
    load_server_config,
    new_request_id,
    validate_code_ast,
    validate_command_args,
)


# ─── Code Security Validator Tests ──────────────────────────────


class TestCodeSecurityValidator:
    """Test AST-based code security validation."""

    def test_safe_code_passes(self) -> None:
        """Verify safe code passes validation."""
        safe_code = "x = 1 + 2\nprint(x)"
        policy = CodeSecurityPolicy()
        validate_code_ast(safe_code, policy)

    def test_import_builtin_module_blocked(self) -> None:
        """Verify importing builtin modules is blocked."""
        code = "import sys"
        policy = CodeSecurityPolicy()
        with pytest.raises(SecurityViolationError):
            validate_code_ast(code, policy)

    def test_import_os_blocked(self) -> None:
        """Verify importing os module is blocked."""
        code = "import os\nos.system('ls')"
        policy = CodeSecurityPolicy()
        with pytest.raises(SecurityViolationError):
            validate_code_ast(code, policy)

    def test_import_pickle_blocked(self) -> None:
        """Verify importing pickle module is blocked."""
        code = "import pickle\npickle.loads(b'data')"
        policy = CodeSecurityPolicy()
        with pytest.raises(SecurityViolationError):
            validate_code_ast(code, policy)

    def test_subprocess_blocked(self) -> None:
        """Verify subprocess usage is blocked."""
        code = "import subprocess\nsubprocess.run(['ls'])"
        policy = CodeSecurityPolicy()
        with pytest.raises(SecurityViolationError):
            validate_code_ast(code, policy)

    def test_exec_blocked(self) -> None:
        """Verify exec() usage is blocked."""
        code = "exec('x = 1')"
        policy = CodeSecurityPolicy()
        with pytest.raises(SecurityViolationError):
            validate_code_ast(code, policy)

    def test_eval_blocked(self) -> None:
        """Verify eval() usage is blocked."""
        code = "eval('1 + 1')"
        policy = CodeSecurityPolicy()
        with pytest.raises(SecurityViolationError):
            validate_code_ast(code, policy)

    def test_dynamic_attr_blocked(self) -> None:
        """Verify dynamic attribute access is blocked."""
        code = "obj = object()\ngetattr(obj, 'attr')"
        policy = CodeSecurityPolicy()
        with pytest.raises(SecurityViolationError):
            validate_code_ast(code, policy)

    def test_file_write_blocked(self) -> None:
        """Verify file write operations are blocked."""
        code = "open('/tmp/test.txt', 'w').write('hello')"
        policy = CodeSecurityPolicy()
        with pytest.raises(SecurityViolationError):
            validate_code_ast(code, policy)

    def test_allowed_directory_file_write_passes(self) -> None:
        """Verify file write to allowed directory passes."""
        code = "open('/home/user/projects/test.txt', 'w').write('hello')"
        policy = CodeSecurityPolicy(allowed_directories=("/home/user/projects",))
        validate_code_ast(code, policy)

    def test_disallowed_directory_file_write_blocked(self) -> None:
        """Verify file write to non-allowed directory is blocked."""
        code = "open('/tmp/test.txt', 'w').write('hello')"
        policy = CodeSecurityPolicy(allowed_directories=("/home/user/projects",))
        with pytest.raises(SecurityViolationError):
            validate_code_ast(code, policy)

    def test_empty_code_raises_error(self) -> None:
        """Verify empty code raises SecurityViolationError."""
        policy = CodeSecurityPolicy()
        with pytest.raises(SecurityViolationError):
            validate_code_ast("", policy)


# ─── Payload Size Check Tests ──────────────────────────────────


class TestPayloadSizeCheck:
    """Test payload size enforcement."""

    def test_within_limit(self) -> None:
        """Verify code within limit passes."""
        code = "x = 1" * 100  # Small code
        check_payload_size(code, max_bytes=1024)

    def test_at_limit(self) -> None:
        """Verify code at exact limit passes."""
        code = "a" * 100  # Exactly 100 bytes
        check_payload_size(code, max_bytes=len(code.encode("utf-8")))

    def test_exceeds_limit_raises_error(self) -> None:
        """Verify oversized code raises SecurityViolationError."""
        large_code = "x = 1\n" * 1000
        with pytest.raises(SecurityViolationError):
            check_payload_size(large_code, max_bytes=100)


# ─── Code Fingerprint Tests ────────────────────────────────────


class TestCodeFingerprint:
    """Test code fingerprinting utility."""

    def test_fingerprint_is_deterministic(self) -> None:
        """Verify same code produces same fingerprint."""
        code = "print('hello')"
        fp1 = code_fingerprint(code)
        fp2 = code_fingerprint(code)
        assert fp1 == fp2

    def test_different_codes_different_fingerprints(self) -> None:
        """Verify different codes produce different fingerprints."""
        fp1 = code_fingerprint("x = 1")
        fp2 = code_fingerprint("y = 2")
        assert fp1 != fp2

    def test_fingerprint_not_raw_code(self) -> None:
        """Verify fingerprint is not the raw code."""
        code = "print('sensitive data')"
        fp = code_fingerprint(code)
        assert fp != code
        assert len(fp) < len(code)


# ─── Command Schema Validation Tests ────────────────────────────


class TestCommandSchemaValidation:
    """Test command catalog validation."""

    def test_valid_command_spec(self) -> None:
        """Verify known command spec is found."""
        spec = get_command_spec("ping")
        assert spec.name == "ping"
        assert spec.idempotent is True

    def test_unknown_command_raises_error(self) -> None:
        """Verify unknown command raises ValidationError."""
        with pytest.raises(ValidationError) as exc_info:
            get_command_spec("unknown_command")
        assert "Unknown command" in str(exc_info.value)

    def test_is_scene_mutating_true(self) -> None:
        """Verify scene-mutating command detection."""
        assert is_scene_mutating("execute_code") is True

    def test_is_scene_mutating_false(self) -> None:
        """Verify non-scene-mutating command detection."""
        assert is_scene_mutating("ping") is False
        assert is_scene_mutating("get_status") is False

    def test_validate_required_params(self) -> None:
        """Verify required parameters are validated."""
        # execute_code requires 'code' parameter
        with pytest.raises(ValidationError) as exc_info:
            validate_command_args("execute_code", {})
        assert "Missing required parameter" in str(exc_info.value)

    def test_validate_optional_params(self) -> None:
        """Verify optional parameters are accepted."""
        validate_command_args("ping", None)  # No params for ping

    def test_validate_unknown_param(self) -> None:
        """Verify unknown parameters are rejected."""
        with pytest.raises(ValidationError):
            validate_command_args("ping", {"unknown_key": "value"})


# ─── Timeout Calculation Tests ────────────────────────────────


class TestTimeoutCalculation:
    """Test effective timeout calculation."""

    def test_default_timeout(self) -> None:
        """Verify default timeout when none provided."""
        timeout = effective_command_timeout_ms("ping", None)
        assert timeout == 5000.0

    def test_requested_timeout(self) -> None:
        """Verify requested timeout is used when within limits."""
        timeout = effective_command_timeout_ms("ping", 3000.0)
        assert timeout == 3000.0

    def test_exceeds_max_raises_error(self) -> None:
        """Verify timeout exceeding max raises ValidationError."""
        with pytest.raises(ValidationError):
            effective_command_timeout_ms("ping", 100_000.0)


# ─── Config Loading Tests ──────────────────────────────────────


class TestConfigLoading:
    """Test configuration file loading."""

    def test_default_config(self) -> None:
        """Verify default config loads without file."""
        config = load_server_config(config_path=None)
        assert config.host == "localhost"
        assert config.port == 9876

    @patch('os.environ', {
        'BLENDER_HOST': '192.168.1.100',
        'BLENDER_PORT': '9877',
        'SERVER_QUEUE_MAX_DEPTH': '100',
    })
    def test_env_overrides(self) -> None:
        """Verify environment variables override defaults."""
        config = load_server_config(config_path=None)
        assert config.host == "192.168.1.100"
        assert config.port == 9877
        assert config.queue_max_depth == 100

    def test_programmatic_overrides(self) -> None:
        """Verify programmatic overrides take highest priority."""
        config = load_server_config(overrides={"host": "override.local", "port": 9999})
        assert config.host == "override.local"
        assert config.port == 9999


# ─── Request ID Generation Tests ──────────────────────────────


class TestRequestIdGeneration:
    """Test UUID4 request ID generation."""

    def test_id_is_uuid4_format(self) -> None:
        """Verify generated ID is valid UUID4 format."""
        import uuid
        id1 = new_request_id()
        parsed = uuid.UUID(id1)
        assert parsed.version == 4  # UUID4

    def test_ids_are_unique(self) -> None:
        """Verify each ID is unique."""
        id1 = new_request_id()
        id2 = new_request_id()
        assert id1 != id2

    def test_id_is_string(self) -> None:
        """Verify ID is a string."""
        id1 = new_request_id()
        assert isinstance(id1, str)


# ─── ExecutionTimeoutError Tests ──────────────────────────────


class TestExecutionTimeoutError:
    """Test ExecutionTimeoutError exception."""

    def test_error_attributes(self) -> None:
        """Verify error has correct message and details."""
        error = ExecutionTimeoutError(30_000.0)
        assert "30000.0" in str(error.message) or "30000" in str(error.message)
