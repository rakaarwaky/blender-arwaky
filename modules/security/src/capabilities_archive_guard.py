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
from modules.shared.src.security.utility_security_path import (
    is_within_allowed_dirs,
    normalize_path,
)


class ArchiveGuard(ExtractArchiveProtocol):
    """Validates archive extraction against safety policy."""

    # ─── Block 1: Class Definition & Constructor ──────────────
    def __init__(self, policy: SecurityPolicyVO | None = None) -> None:
        self._policy = policy or SecurityPolicyVO()

    # ─── Block 2: Public Contract  ────────────────────────
    async def validate_extraction(self, request: ArchiveExtractionVO) -> ArchiveExtractionVO:
        """Validate and guard archive extraction against safety policy."""
        opts = request.options
        dest = request.destination_directory
        rejected: list[RejectedEntryVO] = []
        warnings: list[str] = []

        # Check for missing destination BEFORE normalization
        if not dest:
            return ArchiveExtractionVO(
                destination_directory=request.destination_directory,
                entries=request.entries,
                options=request.options,
                allowed=False,
                rejected_entries=tuple(rejected),
                warnings=tuple(["Missing destination directory"]),
                audit_metadata={"rule": "missing_destination"},
            )

        dest_normalized = normalize_path(dest)

        # Validate destination is within allowed directories (FR-SEC-002)
        allowed_dirs = self._policy.allowed_directories
        if not allowed_dirs or not is_within_allowed_dirs(dest_normalized, allowed_dirs):
            return ArchiveExtractionVO(
                destination_directory=request.destination_directory,
                entries=request.entries,
                options=request.options,
                allowed=False,
                rejected_entries=tuple(rejected),
                warnings=tuple(["Destination outside allowed directories"]),
                audit_metadata={"rule": "unauthorized_archive_destination"},
            )

        total_size = 0
        entry_count = 0
        max_total_size = opts.max_total_size

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

            entry_resolved = os.path.normpath(os.path.join(dest_normalized, entry.entry_path))
            if not entry_resolved.startswith(dest_normalized + os.sep) and entry_resolved != dest_normalized:
                rejected.append(RejectedEntryVO(entry_path=entry.entry_path, reason="Entry escapes destination directory"))
                continue

            # Depth check: count nesting levels relative to destination (FR-SEC-002)
            relative = os.path.relpath(entry_resolved, dest_normalized)
            nesting_depth = 0 if relative == "." else relative.count(os.sep) + 1
            if nesting_depth > opts.max_depth:
                rejected.append(RejectedEntryVO(
                    entry_path=entry.entry_path,
                    reason=f"Entry nesting depth {nesting_depth} exceeds maximum {opts.max_depth}",
                ))
                continue

            total_size += entry.uncompressed_size

            # Stop early if total size exceeds limit
            if total_size > max_total_size:
                rejected.append(RejectedEntryVO(entry_path=entry.entry_path, reason="Total extracted size exceeds limit"))
                break

        allowed = len(rejected) == 0
        return ArchiveExtractionVO(
            destination_directory=request.destination_directory,
            entries=request.entries,
            options=request.options,
            allowed=allowed,
            safe_destination=dest_normalized,
            rejected_entries=tuple(rejected),
            warnings=tuple(warnings),
            audit_metadata={"entry_count": entry_count, "total_size": total_size},
        )

    # ─── Block 3: Dunder Methods, Factories & Helpers ─────
    def __repr__(self) -> str:
        return "ArchiveGuard()"
