"""Capabilities: Archive guard — FR-SEC-002.

Validates archive extraction safety: path traversal, symlink, depth, size, count limits.
Implements ExtractArchiveProtocol.
"""

from __future__ import annotations

import os

from modules.shared.src.security.contract_extract_archive_protocol import ExtractArchiveProtocol
from modules.shared.src.security.taxonomy_security_vo import (
    ArchiveExtractionVO,
    RejectedEntryVO,
    SecurityPolicyVO,
)


class ArchiveGuard(ExtractArchiveProtocol):
    """Validates archive extraction against safety policy."""

    # ─── Block 1: Class Definition & Constructor ──────────────
    def __init__(self, policy: SecurityPolicyVO | None = None) -> None:
        self._policy = policy

    # ─── Block 2: Public Contract  ────────────────────────
    async def validate_extraction(self, request: ArchiveExtractionVO) -> ArchiveExtractionVO:
        """Validate and guard archive extraction against safety policy."""
        opts = request.options
        dest = os.path.normpath(os.path.abspath(request.destination_directory))
        rejected: list[RejectedEntryVO] = []
        warnings: list[str] = []

        if not dest:
            return ArchiveExtractionVO(
                destination_directory=request.destination_directory,
                entries=request.entries,
                options=request.options,
                allowed=False,
                rejected_entries=tuple(rejected),
                warnings=tuple(warnings),
                audit_metadata={"rule": "missing_destination"},
            )

        # Validate destination is within allowed directories (FR-SEC-002)
        # Note: policy is not available in this capability; callers should
        # validate allowed_directories before invoking ArchiveGuard.

        total_size = 0
        entry_count = 0

        for entry in request.entries:
            entry_count += 1

            if entry_count > opts.max_entry_count:
                rejected.append(RejectedEntryVO(entry_path=entry.entry_path, reason="Exceeds maximum entry count"))
                continue

            if entry.is_symbolic_link and not opts.allow_symbolic_links:
                rejected.append(RejectedEntryVO(entry_path=entry.entry_path, reason="Symbolic link entry not allowed"))
                continue

            if entry.is_hard_link and not opts.allow_hard_links:
                rejected.append(RejectedEntryVO(entry_path=entry.entry_path, reason="Hard link entry not allowed"))
                continue

            if entry.uncompressed_size > opts.max_entry_size:
                rejected.append(RejectedEntryVO(entry_path=entry.entry_path, reason=f"Entry exceeds maximum size: {entry.uncompressed_size} > {opts.max_entry_size}"))
                continue

            if os.path.isabs(entry.entry_path):
                rejected.append(RejectedEntryVO(entry_path=entry.entry_path, reason="Absolute entry path not allowed"))
                continue

            if ".." in entry.entry_path.split("/") or ".." in entry.entry_path.split(os.sep):
                rejected.append(RejectedEntryVO(entry_path=entry.entry_path, reason="Path traversal in entry path"))
                continue

            entry_resolved = os.path.normpath(os.path.join(dest, entry.entry_path))
            if not entry_resolved.startswith(dest + os.sep) and entry_resolved != dest:
                rejected.append(RejectedEntryVO(entry_path=entry.entry_path, reason="Entry escapes destination directory"))
                continue

            # Depth check: count nesting levels relative to destination (FR-SEC-002)
            if len(entry_resolved) > len(dest):
                relative = entry_resolved[len(dest):]
                nesting_depth = relative.count(os.sep)
                if nesting_depth > opts.max_depth:
                    rejected.append(RejectedEntryVO(
                        entry_path=entry.entry_path,
                        reason=f"Entry nesting depth {nesting_depth} exceeds maximum {opts.max_depth}",
                    ))
                    continue

            total_size += entry.uncompressed_size

        if total_size > opts.max_total_size:
            return ArchiveExtractionVO(
                destination_directory=request.destination_directory,
                entries=request.entries,
                options=request.options,
                allowed=False,
                safe_destination=dest,
                rejected_entries=tuple(rejected),
                warnings=tuple(warnings + [f"Total extracted size {total_size} exceeds limit {opts.max_total_size}"]),
                audit_metadata={"rule": "total_size_exceeded", "total_size": total_size},
            )

        allowed = len(rejected) == 0
        return ArchiveExtractionVO(
            destination_directory=request.destination_directory,
            entries=request.entries,
            options=request.options,
            allowed=allowed,
            safe_destination=dest,
            rejected_entries=tuple(rejected),
            warnings=tuple(warnings),
            audit_metadata={"entry_count": entry_count, "total_size": total_size},
        )

    # ─── Block 3: Dunder Methods, Factories & Helpers ─────
    def __repr__(self) -> str:
        return "ArchiveGuard()"
