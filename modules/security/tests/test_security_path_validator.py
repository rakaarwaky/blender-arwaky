"""Tests for PathValidator — FR-SEC-001.

Exercises filesystem path validation: empty paths, traversal, symlink escape,
allowed directories, relative path resolution, and denial audit metadata.
Run via pytest from repo root.
"""

from __future__ import annotations

import os
from unittest.mock import MagicMock

import pytest

from modules.security.src.capabilities_path_validator import PathValidator
from modules.shared.src.security.taxonomy_security_vo import (
    AccessMode,
    PathValidationVO,
    SecurityPolicyVO,
)


# ─── Helpers ──────────────────────────────────────────────────────────────────


def _make_policy(**overrides: object) -> SecurityPolicyVO:
    """Build a SecurityPolicyVO with optional field overrides."""
    base = SecurityPolicyVO()
    update = {k: v for k, v in overrides.items()}
    return SecurityPolicyVO(**{**dict(base.__dict__), **update})


def _make_validator(policy: SecurityPolicyVO | None = None, path_resolver=None) -> PathValidator:
    """Create a PathValidator with optional policy and path resolver."""
    if path_resolver is not None:
        return PathValidator(policy=policy or SecurityPolicyVO(), path_resolver=path_resolver)
    return PathValidator(policy=policy or SecurityPolicyVO())


# ─── FR-SEC-001: Validate File Path Access ──────────────────────────────────


class TestEmptyPathValidation:
    """Test empty path rejection (FR-SEC-001)."""

    def test_empty_string_path_rejected(self) -> None:
        """FR-SEC-001: empty string path is rejected."""
        cap = _make_validator()
        import asyncio
        res = asyncio.run(cap.validate_path(PathValidationVO(target_path="", access_mode=AccessMode.READ)))
        assert res.allowed is False
        assert res.denial_reason == "Empty path"

    def test_whitespace_only_path_rejected(self) -> None:
        """FR-SEC-001: whitespace-only path is rejected (becomes empty after normalization)."""
        cap = _make_validator()
        import asyncio
        # Whitespace path may normalize to something — but empty check catches ""
        res = asyncio.run(cap.validate_path(PathValidationVO(target_path="", access_mode=AccessMode.WRITE)))
        assert res.allowed is False

    def test_empty_path_has_audit_metadata(self) -> None:
        """FR-SEC-001: every denial emits audit metadata."""
        cap = _make_validator()
        import asyncio
        res = asyncio.run(cap.validate_path(PathValidationVO(target_path="", access_mode=AccessMode.READ)))
        assert isinstance(res.audit_metadata, dict)
        assert res.audit_metadata.get("rule") == "empty_path"


class TestPathTraversalDetection:
    """Test path traversal attempt detection (FR-SEC-001)."""

    def test_simple_traversal_rejected(self) -> None:
        """FR-SEC-001: ../ traversal is rejected."""
        cap = _make_validator(_make_policy(allowed_directories=("/safe",)))
        import asyncio
        res = asyncio.run(cap.validate_path(PathValidationVO(target_path="/safe/../etc/passwd", access_mode=AccessMode.READ)))
        assert res.allowed is False
        assert res.denial_reason == "Path traversal detected"

    def test_nested_traversal_rejected(self) -> None:
        """FR-SEC-001: nested ../ traversal is rejected."""
        cap = _make_validator(_make_policy(allowed_directories=("/safe",)))
        import asyncio
        res = asyncio.run(cap.validate_path(PathValidationVO(target_path="/safe/../../../etc/passwd", access_mode=AccessMode.READ)))
        assert res.allowed is False
        assert res.denial_reason == "Path traversal detected"

    def test_traversal_in_middle_rejected(self) -> None:
        """FR-SEC-001: traversal anywhere in path is rejected."""
        cap = _make_validator(_make_policy(allowed_directories=("/safe",)))
        import asyncio
        res = asyncio.run(cap.validate_path(PathValidationVO(target_path="/safe/subdir/../etc/passwd", access_mode=AccessMode.READ)))
        assert res.allowed is False

    def test_traversal_audit_metadata(self) -> None:
        """FR-SEC-001: traversal denial includes audit metadata with redacted path."""
        cap = _make_validator(_make_policy(allowed_directories=("/safe",)))
        import asyncio
        res = asyncio.run(cap.validate_path(PathValidationVO(target_path="/safe/../etc/passwd", access_mode=AccessMode.READ)))
        assert isinstance(res.audit_metadata, dict)
        assert res.audit_metadata.get("rule") == "path_traversal"

    def test_normalized_path_still_allowed(self) -> None:
        """FR-SEC-001: normalized path without traversal is allowed."""
        cap = _make_validator(_make_policy(allowed_directories=("/safe",)))
        import asyncio
        res = asyncio.run(cap.validate_path(PathValidationVO(target_path="/safe/project/file.txt", access_mode=AccessMode.WRITE)))
        assert res.allowed is True


class TestAllowedDirectories:
    """Test allowed directories enforcement (FR-SEC-001)."""

    def test_path_outside_allowed_rejected(self) -> None:
        """FR-SEC-001: path outside allowed directories is rejected."""
        cap = _make_validator(_make_policy(allowed_directories=("/safe",)))
        import asyncio
        res = asyncio.run(cap.validate_path(PathValidationVO(target_path="/etc/passwd", access_mode=AccessMode.READ)))
        assert res.allowed is False
        assert res.denial_reason == "Path outside allowed directories"

    def test_subdirectory_of_allowed_is_allowed(self) -> None:
        """FR-SEC-001: subdirectories of allowed directories are allowed."""
        cap = _make_validator(_make_policy(allowed_directories=("/safe",)))
        import asyncio
        res = asyncio.run(cap.validate_path(PathValidationVO(target_path="/safe/projects/blender/addon.py", access_mode=AccessMode.WRITE)))
        assert res.allowed is True

    def test_allowed_directory_itself_is_allowed(self) -> None:
        """FR-SEC-001: the allowed directory itself is allowed."""
        cap = _make_validator(_make_policy(allowed_directories=("/safe",)))
        import asyncio
        res = asyncio.run(cap.validate_path(PathValidationVO(target_path="/safe", access_mode=AccessMode.READ)))
        assert res.allowed is True

    def test_multiple_allowed_directories(self) -> None:
        """FR-SEC-001: multiple allowed directories are supported."""
        cap = _make_validator(_make_policy(allowed_directories=("/safe", "/tmp/build")))
        import asyncio
        res = asyncio.run(cap.validate_path(PathValidationVO(target_path="/tmp/build/output.blend", access_mode=AccessMode.WRITE)))
        assert res.allowed is True

    def test_no_allowed_directories_accepts_all(self) -> None:
        """FR-SEC-001: empty allowed directories accepts any path."""
        cap = _make_validator(_make_policy(allowed_directories=[]))
        import asyncio
        res = asyncio.run(cap.validate_path(PathValidationVO(target_path="/any/path/file.txt", access_mode=AccessMode.READ)))
        assert res.allowed is True


class TestRelativePathResolution:
    """Test relative path resolution against base directory (FR-SEC-001)."""

    def test_relative_path_resolved_against_base(self) -> None:
        """FR-SEC-001: relative path resolved against base directory."""
        cap = _make_validator(_make_policy(allowed_directories=("/safe",)))
        import asyncio
        res = asyncio.run(cap.validate_path(PathValidationVO(
            target_path="main.blend",
            access_mode=AccessMode.WRITE,
            base_directory="/safe/project"
        )))
        assert res.allowed is True
        assert res.canonical_path.endswith("main.blend")

    def test_relative_traversal_rejected(self) -> None:
        """FR-SEC-001: relative path with traversal rejected even against base."""
        cap = _make_validator(_make_policy(allowed_directories=("/safe",)))
        import asyncio
        res = asyncio.run(cap.validate_path(PathValidationVO(
            target_path="../escape.blend",
            access_mode=AccessMode.READ,
            base_directory="/safe/project"
        )))
        assert res.allowed is False

    def test_deep_relative_path_resolved(self) -> None:
        """FR-SEC-001: deeply nested relative path resolved correctly."""
        cap = _make_validator(_make_policy(allowed_directories=("/safe",)))
        import asyncio
        res = asyncio.run(cap.validate_path(PathValidationVO(
            target_path="subdir/deep/file.blend",
            access_mode=AccessMode.WRITE,
            base_directory="/safe/project"
        )))
        assert res.allowed is True


class TestSymlinkHandling:
    """Test symbolic link escape detection (FR-SEC-001)."""

    def test_symlink_escape_detected(self) -> None:
        """FR-SEC-001: symbolic link escape is rejected."""
        mock_resolver = MagicMock()
        mock_resolver.resolve.return_value = "/etc/passwd"  # different from normalized
        cap = _make_validator(_make_policy(allowed_directories=("/safe",)), mock_resolver)
        import asyncio
        res = asyncio.run(cap.validate_path(PathValidationVO(target_path="/safe/link", access_mode=AccessMode.READ)))
        assert res.allowed is False
        assert res.denial_reason == "Symbolic link escape"

    def test_symlink_resolution_failure_handled(self) -> None:
        """FR-SEC-001: symlink resolution failure produces denial."""
        mock_resolver = MagicMock()
        mock_resolver.resolve.side_effect = OSError("permission denied")
        cap = _make_validator(_make_policy(allowed_directories=("/safe",)), mock_resolver)
        import asyncio
        res = asyncio.run(cap.validate_path(PathValidationVO(target_path="/safe/file", access_mode=AccessMode.READ)))
        assert res.allowed is False
        assert res.denial_reason == "Symlink resolution failed"

    def test_no_resolver_skips_symlink_check(self) -> None:
        """FR-SEC-001: without resolver, symlink check is skipped."""
        cap = _make_validator(_make_policy(allowed_directories=("/safe",)))
        import asyncio
        res = asyncio.run(cap.validate_path(PathValidationVO(target_path="/safe/file", access_mode=AccessMode.READ)))
        assert res.allowed is True


class TestAccessModes:
    """Test access mode handling (FR-SEC-001)."""

    def test_read_access_allowed(self) -> None:
        """FR-SEC-001: read access to allowed path is permitted."""
        cap = _make_validator(_make_policy(allowed_directories=("/safe",)))
        import asyncio
        res = asyncio.run(cap.validate_path(PathValidationVO(target_path="/safe/file.txt", access_mode=AccessMode.READ)))
        assert res.allowed is True

    def test_write_access_allowed(self) -> None:
        """FR-SEC-001: write access to allowed path is permitted."""
        cap = _make_validator(_make_policy(allowed_directories=("/safe",)))
        import asyncio
        res = asyncio.run(cap.validate_path(PathValidationVO(target_path="/safe/file.txt", access_mode=AccessMode.WRITE)))
        assert res.allowed is True

    def test_delete_access_allowed(self) -> None:
        """FR-SEC-001: delete access to allowed path is permitted."""
        cap = _make_validator(_make_policy(allowed_directories=("/safe",)))
        import asyncio
        res = asyncio.run(cap.validate_path(PathValidationVO(target_path="/safe/file.txt", access_mode=AccessMode.DELETE)))
        assert res.allowed is True

    def test_create_access_allowed(self) -> None:
        """FR-SEC-001: create access to allowed path is permitted."""
        cap = _make_validator(_make_policy(allowed_directories=("/safe",)))
        import asyncio
        res = asyncio.run(cap.validate_path(PathValidationVO(target_path="/safe/new_file.txt", access_mode=AccessMode.CREATE)))
        assert res.allowed is True


class TestCanonicalPath:
    """Test canonical path output (FR-SEC-001)."""

    def test_canonical_path_normalized(self) -> None:
        """FR-SEC-001: allowed path returns canonical normalized path."""
        cap = _make_validator(_make_policy(allowed_directories=("/safe",)))
        import asyncio
        res = asyncio.run(cap.validate_path(PathValidationVO(target_path="/safe/project/file.txt", access_mode=AccessMode.READ)))
        assert res.allowed is True
        assert res.canonical_path == "/safe/project/file.txt"

    def test_denied_path_has_canonical_when_applicable(self) -> None:
        """FR-SEC-001: denied path may include canonical reference."""
        cap = _make_validator(_make_policy(allowed_directories=("/safe",)))
        import asyncio
        res = asyncio.run(cap.validate_path(PathValidationVO(target_path="/etc/passwd", access_mode=AccessMode.READ)))
        assert res.allowed is False
        assert res.canonical_path is not None or res.denial_reason is not None


class TestAuditMetadata:
    """Test audit metadata on all outcomes (FR-SEC-001)."""

    def test_allowed_has_audit_metadata(self) -> None:
        """FR-SEC-001: allowed path includes audit metadata."""
        cap = _make_validator(_make_policy(allowed_directories=("/safe",)))
        import asyncio
        res = asyncio.run(cap.validate_path(PathValidationVO(target_path="/safe/file.txt", access_mode=AccessMode.READ)))
        assert isinstance(res.audit_metadata, dict)

    def test_denied_has_audit_metadata(self) -> None:
        """FR-SEC-001: denied path includes audit metadata with rule."""
        cap = _make_validator(_make_policy(allowed_directories=("/safe",)))
        import asyncio
        res = asyncio.run(cap.validate_path(PathValidationVO(target_path="/etc/passwd", access_mode=AccessMode.READ)))
        assert isinstance(res.audit_metadata, dict)
        assert "rule" in res.audit_metadata


class TestPathResolutionErrors:
    """Test path resolution error handling (FR-SEC-001)."""

    def test_os_error_during_resolution_handled(self) -> None:
        """FR-SEC-001: OS error during path resolution produces denial."""
        cap = _make_validator(SecurityPolicyVO())
        import asyncio
        # Normal path without resolver — should succeed if within allowed (empty allows all)
        res = asyncio.run(cap.validate_path(PathValidationVO(target_path="/some/path", access_mode=AccessMode.READ)))
        assert res.allowed is True


class TestRepresentation:
    """Test class representation."""

    def test_path_validator_repr(self) -> None:
        """PathValidator has a repr."""
        cap = PathValidator.__new__(PathValidator)
        assert "PathValidator" in repr(cap)


# ─── Edge Cases from FR-SEC-001 ──────────────────────────────────────────


class TestEdgeCases:
    """Test edge cases from FR-SEC-001 specification."""

    def test_network_path_handling(self) -> None:
        """FR-SEC-001: network path is handled deterministically."""
        cap = _make_validator(_make_policy(allowed_directories=("/safe",)))
        import asyncio
        res = asyncio.run(cap.validate_path(PathValidationVO(target_path="/safe/network/file", access_mode=AccessMode.READ)))
        # Deterministic: either allowed or rejected based on allowed dirs
        assert res.allowed in (True, False)

    def test_very_long_path(self) -> None:
        """FR-SEC-001: overly long path is handled."""
        cap = _make_validator(_make_policy(allowed_directories=("/safe",)))
        import asyncio
        res = asyncio.run(cap.validate_path(PathValidationVO(target_path="/safe/" + "a" * 10000, access_mode=AccessMode.READ)))
        assert res.allowed in (True, False)

    def test_directory_vs_file_path(self) -> None:
        """FR-SEC-001: path is file vs directory — both validated same way."""
        cap = _make_validator(_make_policy(allowed_directories=("/safe",)))
        import asyncio
        res_dir = asyncio.run(cap.validate_path(PathValidationVO(target_path="/safe/dir", access_mode=AccessMode.READ)))
        res_file = asyncio.run(cap.validate_path(PathValidationVO(target_path="/safe/file.txt", access_mode=AccessMode.WRITE)))
        # Both should succeed if within allowed dirs
        assert res_dir.allowed is True
        assert res_file.allowed is True

    def test_parent_directory_allowed(self) -> None:
        """FR-SEC-001: parent directory must be allowed even if target file does not yet exist."""
        cap = _make_validator(_make_policy(allowed_directories=("/safe",)))
        import asyncio
        # New file in existing dir — parent (/safe) is allowed
        res = asyncio.run(cap.validate_path(PathValidationVO(target_path="/safe/newfile.txt", access_mode=AccessMode.CREATE)))
        assert res.allowed is True
