"""Capabilities: Path validator — FR-SEC-001.

Validates filesystem path access: traversal, symlink escape, allowed directories.
Implements ValidatePathProtocol.
"""

from __future__ import annotations

import os
from typing import Protocol

from modules.shared.src.security.contract_validate_path_protocol import ValidatePathProtocol
from modules.shared.src.security.taxonomy_security_vo import (
    PathValidationVO,
    SecurityPolicyVO,
)
from modules.shared.src.security.utility_security_path import (
    is_within_allowed_dirs,
    normalize_path,
    resolve_path,
)


class _PathResolver(Protocol):
    """Protocol for resolving canonical paths (DI boundary)."""

    def resolve(self, path: str) -> str: ...


class _OsPathResolver:
    """Default resolver using os.path.realpath."""

    def resolve(self, path: str) -> str:
        return resolve_path(path)


def _redact_path(path: str) -> str:
    parts = path.replace("\\", "/").split("/")
    if len(parts) <= 2:
        return "***"
    return "/" + "/".join(["***"] + list(parts[-2:]))


class PathValidator(ValidatePathProtocol):
    """Validates filesystem path access against security policy."""

    # ─── Block 1: Class Definition & Constructor ──────────────
    def __init__(
        self,
        policy: SecurityPolicyVO,
        path_resolver: _PathResolver | None = None,
    ) -> None:
        self._policy = policy
        self._resolver = path_resolver or _OsPathResolver()

    # ─── Block 2: Public Contract  ────────────────────────
    async def validate_path(self, request: PathValidationVO) -> PathValidationVO:
        """Validate whether a filesystem path is allowed for the requested access mode."""
        target = request.target_path
        if not target:
            return PathValidationVO(
                target_path=request.target_path,
                access_mode=request.access_mode,
                base_directory=request.base_directory,
                operation_context=request.operation_context,
                allowed=False,
                denial_reason="Empty path",
                audit_metadata={"rule": "empty_path"},
            )

        # Check for path traversal BEFORE normalization
        if ".." in target.replace("\\", "/").split("/"):
            return PathValidationVO(
                target_path=request.target_path,
                access_mode=request.access_mode,
                base_directory=request.base_directory,
                operation_context=request.operation_context,
                allowed=False,
                denial_reason="Path traversal detected",
                audit_metadata={"rule": "path_traversal"},
            )

        if not os.path.isabs(target):
            base = request.base_directory
            if base is None and self._policy.allowed_directories:
                base = self._policy.allowed_directories[0]

            if base is None:
                base = "/"

            target = os.path.join(base, target)

        try:
            normalized = normalize_path(target)
            resolved = self._resolver.resolve(normalized)
        except (OSError, ValueError):
            return PathValidationVO(
                target_path=request.target_path,
                access_mode=request.access_mode,
                allowed=False,
                denial_reason="Symlink resolution failed",
                audit_metadata={"rule": "path_resolution_failed"},
            )

        # Symlink escape check
        if resolved != normalized:
            return PathValidationVO(
                target_path=request.target_path,
                access_mode=request.access_mode,
                allowed=False,
                denial_reason="Symbolic link escape",
                audit_metadata={"rule": "symlink_escape", "path": _redact_path(resolved)},
            )

        allowed_dirs = self._policy.allowed_directories
        if allowed_dirs and not is_within_allowed_dirs(resolved, allowed_dirs):
            return PathValidationVO(
                target_path=request.target_path,
                access_mode=request.access_mode,
                base_directory=request.base_directory,
                operation_context=request.operation_context,
                allowed=False,
                denial_reason="Path outside allowed directories",
                audit_metadata={"rule": "unauthorized_access", "path": _redact_path(resolved)},
            )

        return PathValidationVO(
            target_path=request.target_path,
            access_mode=request.access_mode,
            base_directory=request.base_directory,
            operation_context=request.operation_context,
            allowed=True,
            canonical_path=resolved,
            audit_metadata={"path": _redact_path(resolved), "mode": request.access_mode.value},
        )

    # ─── Block 3: Dunder Methods, Factories & Helpers ─────
    def __repr__(self) -> str:
        return "PathValidator()"
