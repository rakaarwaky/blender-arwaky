"""Capabilities: Path validator — FR-SEC-001.

Validates filesystem path access: traversal, symlink escape, allowed directories.
Implements ValidatePathProtocol.
"""

from __future__ import annotations

import os
from typing import Protocol
from urllib.parse import unquote

from modules.shared.src.security.contract_validate_path_protocol import ValidatePathProtocol
from modules.shared.src.security.taxonomy_security_vo import (
    PathValidationVO,
    SecurityPolicyVO,
)
from modules.shared.src.security.utility_security_path import (
    is_within_allowed_dirs,
    normalize_path,
    redact_path,
    resolve_path,
)


class _PathResolver(Protocol):
    """Protocol for resolving canonical paths (DI boundary)."""

    def resolve(self, path: str) -> str: ...


class _OsPathResolver:
    """Default resolver using os.path.realpath."""

    def resolve(self, path: str) -> str:
        return resolve_path(path)


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

        # Decode URL-escaped separators/dots before traversal detection.
        # This prevents encoded paths from bypassing the segment check.
        target = unquote(target)

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
                audit_metadata={"rule": "symlink_escape", "path": redact_path(resolved)},
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
                audit_metadata={"rule": "unauthorized_access", "path": redact_path(resolved)},
            )

        return PathValidationVO(
            target_path=request.target_path,
            access_mode=request.access_mode,
            base_directory=request.base_directory,
            operation_context=request.operation_context,
            allowed=True,
            canonical_path=resolved,
            audit_metadata={"path": redact_path(resolved), "mode": request.access_mode.value},
        )

    # ─── Block 3: Dunder Methods, Factories & Helpers ─────
    def validate_path_sync(self, request: PathValidationVO) -> PathValidationVO:
        """Synchronous wrapper for async validate_path (for use in sync contexts)."""
        import asyncio
        from concurrent.futures import ThreadPoolExecutor

        try:
            asyncio.get_running_loop()
        except RuntimeError:
            return asyncio.run(self.validate_path(request))

        # A synchronous caller may still be running inside an event loop.
        # Execute the coroutine in a short-lived worker loop instead of
        # nesting or reusing the active loop.
        with ThreadPoolExecutor(max_workers=1) as executor:
            return executor.submit(asyncio.run, self.validate_path(request)).result()

    def __repr__(self) -> str:
        return "PathValidator()"
