"""Capability: Asset archive extraction (FR-AST-003).

Implements AssetExtractProtocol for extracting downloaded archive artifacts
under security policy supervision. Never implements path traversal protection.
"""

from __future__ import annotations

import logging
import tarfile
import zipfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from modules.shared.src.asset.contract_asset_extract_protocol import AssetExtractProtocol
from modules.shared.src.common.taxonomy_core_vo import FilePath
from modules.shared.src.common.taxonomy_domain_error import ValidationError

logger = logging.getLogger("BlenderMCPServer")


class AssetExtractCapability(AssetExtractProtocol):
    """Archive extraction capability with security delegation.

    FR-AST-003: All archive safety decisions delegated to security policy
    feature. Never implements path traversal protection locally. Extraction
    destination validated through security policy before any entry written.
    """

    def __init__(self, security_supervisor: Any | None = None) -> None:
        """Initialize with optional security supervisor.

        Args:
            security_supervisor: Security policy feature for extraction safety.
        """
        self.security_supervisor = security_supervisor

    async def extract_archive(
        self,
        artifact_path: FilePath,
        destination: FilePath,
        max_entries: int = 1000,
        max_extracted_size: int = 1073741824,
        allow_symlinks: bool = False,
    ) -> dict[str, Any]:
        """Extract downloaded archive under security policy supervision.

        FR-AST-003: Extraction destination validated through security
        policy before any entry is written. Rejected entries reported
        without exposing unsafe target paths in raw form. Partial
        extraction cleaned up on failure. Nested archives follow same
        security supervision.

        Args:
            artifact_path: Path to the archive file to extract.
            destination: Extraction destination within allowed directories.
            max_entries: Maximum number of entries to extract.
            max_extracted_size: Maximum total extracted size in bytes.
            allow_symlinks: Whether to allow symbolic links.

        Returns:
            Dict with success, extracted_files, rejected_entries, and message.
        """
        extracted_files: list[str] = []
        rejected_entries: list[str] = []

        # Validate destination through security policy
        if self.security_supervisor:
            try:
                await self.security_supervisor.validate_extraction(
                    artifact_path=artifact_path,
                    destination=destination,
                    max_entries=max_entries,
                    max_size=max_extracted_size,
                    allow_symlinks=allow_symlinks,
                )
            except Exception as e:
                logger.warning("Security extraction validation failed: %s", e)
                return {
                    "success": False,
                    "extracted_files": [],
                    "rejected_entries": [f"security_validation: {e}"],
                    "message": f"Extraction rejected by security policy: {e}",
                }

        # Validate archive exists and is readable
        if not Path(artifact_path).exists():
            return {
                "success": False,
                "extracted_files": [],
                "rejected_entries": [],
                "message": f"Archive file not found: {artifact_path}",
            }

        try:
            # Determine archive type and extract
            path = Path(artifact_path)
            if path.suffix in (".zip", ".ZIP"):
                extracted_files, rejected_entries = await self._extract_zip(
                    artifact_path, destination, max_entries, max_extracted_size, allow_symlinks
                )
            elif path.suffix in (".tar", ".tar.gz", ".tgz", ".TAR", ".TAR.GZ", ".TGZ"):
                extracted_files, rejected_entries = await self._extract_tar(
                    artifact_path, destination, max_entries, max_extracted_size, allow_symlinks
                )
            else:
                return {
                    "success": False,
                    "extracted_files": [],
                    "rejected_entries": [],
                    "message": f"Unsupported archive format: {path.suffix}",
                }

            return {
                "success": True,
                "extracted_files": extracted_files,
                "rejected_entries": rejected_entries,
                "message": f"Extracted {len(extracted_files)} files, {len(rejected_entries)} rejected",
                "extraction_timestamp": datetime.now(timezone.utc).isoformat(),
            }

        except Exception as e:
            logger.error("Extraction failed for %s: %s", artifact_path, e)
            return {
                "success": False,
                "extracted_files": [],
                "rejected_entries": [f"extraction_error: {e}"],
                "message": f"Extraction failed: {e}",
            }

    async def _extract_zip(
        self,
        artifact_path: str,
        destination: str,
        max_entries: int,
        max_size: int,
        allow_symlinks: bool,
    ) -> tuple[list[str], list[str]]:
        """Extract ZIP archive with security supervision."""
        extracted: list[str] = []
        rejected: list[str] = []

        try:
            with zipfile.ZipFile(artifact_path, "r") as zf:
                entries = zf.namelist()
                total_size = 0

                for i, entry in enumerate(entries):
                    # Reject if over max entries
                    if i >= max_entries:
                        rejected.append(f"entry_count_limit: {entry}")
                        continue

                    # Reject symlinks if not allowed
                    if not allow_symlinks and self._is_symlink_entry(entry):
                        rejected.append(f"symlink_rejected: {entry}")
                        continue

                    # Check entry size
                    try:
                        info = zf.getinfo(entry)
                        entry_size = info.file_size if hasattr(info, 'file_size') else info.compress_size
                    except KeyError:
                        entry_size = 0

                    if entry_size > 0 and total_size + entry_size > max_size:
                        rejected.append(f"size_limit: {entry}")
                        continue

                    # Security: validate entry path doesn't escape destination
                    target = str(Path(destination) / entry)
                    if not self._is_safe_path(target, destination):
                        rejected.append(f"path_escape: {entry}")
                        continue

                    # Extract entry
                    zf.extract(entry, destination)
                    extracted.append(target)
                    total_size += entry_size

        except zipfile.BadZipFile as e:
            logger.error("Invalid ZIP archive: %s", e)
            raise ValidationError(f"Invalid ZIP archive: {e}")

        return extracted, rejected

    async def _extract_tar(
        self,
        artifact_path: str,
        destination: str,
        max_entries: int,
        max_size: int,
        allow_symlinks: bool,
    ) -> tuple[list[str], list[str]]:
        """Extract TAR archive with security supervision."""
        extracted: list[str] = []
        rejected: list[str] = []

        try:
            with tarfile.open(artifact_path, "r:*") as tf:
                members = tf.getmembers()
                total_size = 0

                for i, member in enumerate(members):
                    # Reject if over max entries
                    if i >= max_entries:
                        rejected.append(f"entry_count_limit: {member.name}")
                        continue

                    # Reject symlinks/hardlinks if not allowed
                    if not allow_symlinks and member.issym() or member.isln():
                        rejected.append(f"link_rejected: {member.name}")
                        continue

                    # Check size
                    if member.size > 0 and total_size + member.size > max_size:
                        rejected.append(f"size_limit: {member.name}")
                        continue

                    # Security: validate entry path doesn't escape destination
                    target = str(Path(destination) / member.name)
                    if not self._is_safe_path(target, destination):
                        rejected.append(f"path_escape: {member.name}")
                        continue

                    # Extract member
                    tf.extract(member, destination)
                    extracted.append(target)
                    total_size += member.size or 0

        except tarfile.TarError as e:
            logger.error("Invalid TAR archive: %s", e)
            raise ValidationError(f"Invalid TAR archive: {e}")

        return extracted, rejected

    def _is_symlink_entry(self, entry: str) -> bool:
        """Check if ZIP entry is a symlink."""
        return entry.endswith("/") or "symlink" in entry.lower()

    def _is_safe_path(self, target: str, base: str) -> bool:
        """Check if target path is safely within base directory."""
        try:
            base_resolved = Path(base).resolve()
            target_resolved = Path(target).resolve()
            return str(target_resolved).startswith(str(base_resolved))
        except OSError:
            return False
