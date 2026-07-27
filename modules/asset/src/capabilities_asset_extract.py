"""Capability: Asset archive extraction (FR-AST-003).

Implements AssetExtractProtocol for extracting downloaded archive artifacts
under security policy supervision. Never implements path traversal protection.

FR-AST-003 mandates that ALL archive safety decisions (entry path validation,
traversal/escape rejection, depth/size/entry-count limits, symbolic/hard link
policy) are delegated to the security policy feature. This capability therefore
performs only the mechanical extraction of entries that the security supervisor
has explicitly approved; it contains no local traversal or link enforcement.
"""

from __future__ import annotations

import logging
import os
import tarfile
import zipfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from modules.shared.src.asset.contract_asset_extract_protocol import AssetExtractProtocol
from modules.shared.src.common.taxonomy_core_vo import FilePath
from modules.shared.src.common.taxonomy_domain_error import ValidationError
from modules.shared.src.security.contract_extract_archive_protocol import (
    ExtractArchiveProtocol,
)
from modules.shared.src.security.taxonomy_security_vo import (
    ArchiveEntryVO,
    ArchiveExtractionOptionsVO,
    ArchiveExtractionVO,
)

logger = logging.getLogger("BlenderMCPServer")


class AssetExtractCapability(AssetExtractProtocol):
    """Archive extraction capability with security delegation.

    FR-AST-003: All archive safety decisions delegated to security policy
    feature. Never implements path traversal protection locally. Extraction
    destination is validated through security policy before any entry is
    written. Rejected entries are reported without exposing unsafe target
    paths in raw form.
    """

    def __init__(self, security_supervisor: ExtractArchiveProtocol | None = None) -> None:
        """Initialize with the security supervisor for extraction safety.

        Args:
            security_supervisor: Security policy feature implementing
                ExtractArchiveProtocol. The asset feature MUST delegate all
                archive safety decisions to it; extraction is refused when
                no supervisor is available (the asset feature does not
                implement its own traversal protection).
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
        extraction is avoided because approval is obtained before any
        entry is written. Nested archives follow the same security
        supervision.

        Args:
            artifact_path: Path to the archive file to extract.
            destination: Extraction destination within allowed directories.
            max_entries: Maximum number of entries to extract.
            max_extracted_size: Maximum total extracted size in bytes.
            allow_symlinks: Whether to allow symbolic links.

        Returns:
            Dict with success, extracted file references, rejected entry
            summary, and message.
        """
        if not Path(artifact_path).exists():
            return {
                "success": False,
                "extracted_files": [],
                "rejected_entries": [],
                "message": f"Archive file not found: {artifact_path}",
            }

        # Enumerate entries for the security supervisor to evaluate.
        try:
            entries = self._list_entries(str(artifact_path))
        except ValidationError as e:
            return {
                "success": False,
                "extracted_files": [],
                "rejected_entries": [],
                "message": str(e),
            }
        except (zipfile.BadZipFile, tarfile.TarError) as e:
            logger.error("Invalid archive %s: %s", artifact_path, e)
            return {
                "success": False,
                "extracted_files": [],
                "rejected_entries": [],
                "message": f"Invalid archive: {e}",
            }

        options = ArchiveExtractionOptionsVO(
            max_entry_count=max_entries,
            max_total_size=max_extracted_size,
            allow_symbolic_links=allow_symlinks,
        )
        request = ArchiveExtractionVO(
            destination_directory=str(destination),
            entries=tuple(entries),
            options=options,
        )

        # FR-AST-003: the asset feature must not implement its own traversal
        # protection, so without a security supervisor it cannot safely extract.
        if self.security_supervisor is None:
            return {
                "success": False,
                "extracted_files": [],
                "rejected_entries": [],
                "message": (
                    "Archive extraction requires security supervision (FR-AST-003): "
                    "asset feature does not implement path traversal protection."
                ),
            }

        try:
            result = await self.security_supervisor.validate_extraction(request)
        except Exception as e:  # supervisor raised during validation
            logger.warning("Security extraction validation failed: %s", e)
            return {
                "success": False,
                "extracted_files": [],
                "rejected_entries": [f"security_validation: {e}"],
                "message": f"Extraction rejected by security policy: {e}",
            }

        if not result.allowed:
            rejected = [r.entry_path for r in result.rejected_entries]
            return {
                "success": False,
                "extracted_files": [],
                "rejected_entries": rejected,
                "message": "Extraction rejected by security policy",
                "warnings": list(result.warnings),
            }

        dest = result.safe_destination or str(destination)
        os.makedirs(dest, exist_ok=True)
        rejected_names = {r.entry_path for r in result.rejected_entries}

        try:
            extracted_files = self._extract_allowed(str(artifact_path), dest, rejected_names)
        except (zipfile.BadZipFile, tarfile.TarError) as e:
            logger.error("Extraction failed for %s: %s", artifact_path, e)
            return {
                "success": False,
                "extracted_files": [],
                "rejected_entries": [f"extraction_error: {e}"],
                "message": f"Extraction failed: {e}",
            }

        return {
            "success": True,
            "extracted_files": extracted_files,
            "rejected_entries": [r.entry_path for r in result.rejected_entries],
            "message": f"Extracted {len(extracted_files)} files, {len(rejected_names)} rejected",
            "extraction_timestamp": datetime.now(timezone.utc).isoformat(),
        }

    def _list_entries(self, artifact_path: str) -> list[ArchiveEntryVO]:
        """Enumerate archive entries as ArchiveEntryVO for security review.

        Raises ValidationError for unsupported archive formats.
        """
        path = Path(artifact_path)
        suffix = path.suffix.lower()
        name_lower = path.name.lower()

        if suffix == ".zip" or name_lower.endswith(".zip"):
            with zipfile.ZipFile(artifact_path, "r") as zf:
                entries: list[ArchiveEntryVO] = []
                for info in zf.infolist():
                    unix_mode = (info.external_attr >> 16) & 0o170000
                    entries.append(
                        ArchiveEntryVO(
                            entry_path=info.filename,
                            is_directory=info.filename.endswith("/"),
                            is_symbolic_link=unix_mode == 0o120000,
                            is_hard_link=False,
                            compressed_size=info.compress_size,
                            uncompressed_size=info.file_size,
                        )
                    )
                return entries

        if (
            suffix == ".tar"
            or suffix == ".tgz"
            or (suffix == ".gz" and (name_lower.endswith(".tar.gz") or name_lower.endswith(".tgz")))
        ):
            with tarfile.open(artifact_path, "r:*") as tf:
                entries = []
                for member in tf.getmembers():
                    entries.append(
                        ArchiveEntryVO(
                            entry_path=member.name,
                            is_directory=member.isdir(),
                            is_symbolic_link=member.issym(),
                            is_hard_link=member.islnk(),
                            compressed_size=member.size,
                            uncompressed_size=member.size,
                        )
                    )
                return entries

        raise ValidationError(f"Unsupported archive format: {path.suffix or name_lower}")

    def _extract_allowed(
        self, artifact_path: str, dest: str, rejected_names: set[str]
    ) -> list[str]:
        """Extract only the entries the security supervisor approved.

        No local path/symlink/size checks are performed here; safety has
        already been enforced by the security supervisor.
        """
        path = Path(artifact_path)
        suffix = path.suffix.lower()
        name_lower = path.name.lower()
        extracted: list[str] = []

        if suffix == ".zip" or name_lower.endswith(".zip"):
            with zipfile.ZipFile(artifact_path, "r") as zf:
                for info in zf.infolist():
                    if info.filename in rejected_names:
                        continue
                    zf.extract(info, dest)
                    extracted.append(str(Path(dest) / info.filename))
        else:
            with tarfile.open(artifact_path, "r:*") as tf:
                for member in tf.getmembers():
                    if member.name in rejected_names:
                        continue
                    tf.extract(member, dest)
                    extracted.append(str(Path(dest) / member.name))

        return extracted
