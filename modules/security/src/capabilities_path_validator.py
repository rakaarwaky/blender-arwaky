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
from modules.shared.src.security.utility_security_path import is_within_allowed_dirs, normalize_path


class _PathResolver(Protocol):
    """Protocol for resolving canonical paths (DI boundary)."""

    def resolve(self, path: str) -> str: ...


class PathValidator(ValidatePathProtocol):
    """Validates filesystem path access against security policy."""

    # ─── Block 1: Class Definition & Constructor ──────────────
    def __init__(
        self,
        policy: SecurityPolicyVO,
        path_resolver: _PathResolver | None = None,
    ) -> None:
        self._policy = policy
        self._resolver = path_resolver

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

        if not os.path.isabs(target):
            base = request.base_directory or (self._policy.allowed_directories[0] if self._policy.allowed_directories else None)
            if base is None:
                return PathValidationVO(
                    target_path=request.target_path,
                    access_mode=request.access_mode,
                    allowed=False,
                    denial_reason="No base directory configured and policy has no allowed directories",
                    audit_metadata={"rule": "no_allowed_directory"},
                )
            target = os.path.join(base, target)

        try:
            normalized = normalize_path(target)
        except (OSError, ValueError) as exc:
            return PathValidationVO(
                target_path=request.target_path,
                access_mode=request.access_mode,
                allowed=False,
                denial_reason=f"Path resolution failed: {exc}",
                audit_metadata={"rule": "path_resolution_failed"},
            )

        if ".." in normalized.split(os.sep):
            return PathValidationVO(
                target_path=request.target_path,
                access_mode=request.access_mode,
                allowed=False,
                denial_reason="Path traversal detected",
                audit_metadata={"rule": "path_traversal"},
            )

        if self._resolver:
            try:
                resolved = self._resolver.resolve(normalized)
                if resolved != normalized:
                    return PathValidationVO(
                        target_path=request.target_path,
                        access_mode=request.access_mode,
                        allowed=False,
                        denial_reason="Symbolic link escape",
                        audit_metadata={"rule": "symlink_escape", "path": _redact_path(normalized)},
                    )
            except (OSError, ValueError):
                return PathValidationVO(
                    target_path=request.target_path,
                    access_mode=request.access_mode,
                    allowed=False,
                    denial_reason="Symlink resolution failed",
                    audit_metadata={"rule": "symlink_resolution_failed"},
                )

        allowed_dirs = list(self._policy.allowed_directories) if self._policy.allowed_directories else []
        if not is_within_allowed_dirs(normalized, allowed_dirs):
            return PathValidationVO(
                target_path=request.target_path,
                access_mode=request.access_mode,
                allowed=False,
                denial_reason="Path outside allowed directories",
                audit_metadata={"rule": "unauthorized_access", "path": _redact_path(normalized)},
            )

        return PathValidationVO(
            target_path=request.target_path,
            access_mode=request.access_mode,
            base_directory=request.base_directory,
            operation_context=request.operation_context,
            allowed=True,
            canonical_path=normalized,
            audit_metadata={"path": _redact_path(normalized), "mode": request.access_mode.value},
        )

    # ─── Block 3: Dunder Methods, Factories & Helpers ─────
    def __repr__(self) -> str:
        return "PathValidator()"


def _redact_path(path: str) -> str:
    parts = path.replace("\\", "/").split("/")
    if len(parts) <= 2:
        return "***"
    return "/".join(["***"] + parts[-2:])
