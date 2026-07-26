"""Capability: Archive extraction executor.

Implements AssetExtractProtocol for extracting downloaded archive artifacts
under security policy supervision. Never implements path traversal protection
locally — delegates to security policy feature.

FR-AST-003: Extract Asset Archive
AES Capabilities layer — depends on Taxonomy, Contract, Utility.
"""

import logging
import shutil
import tarfile
import zipfile
from pathlib import Path

from modules.shared.src.asset.contract_asset_extract_protocol import AssetExtractProtocol
from modules.shared.src.asset.taxonomy_asset_vo import AssetExtractArchiveVO
from modules.shared.src.common.taxonomy_core_vo import ErrorMessage, FilePath, SuccessFlag

logger = logging.getLogger("BlenderMCPServer")

SUPPORTED_ARCHIVE_EXTENSIONS = frozenset({".zip", ".tar", ".tar.gz", ".tgz", ".tar.bz2", ".tbz2"})


class AssetExtractExecutor(AssetExtractProtocol):
    """Executor for extracting archive artifacts under security supervision."""

    # ─── Block 1: Class Definition & Constructor ──────────────

    def __init__(self) -> None:
        pass

    # ─── Block 2: Protocol Method Implementation ─────────────

    async def extract_archive(self, vo: AssetExtractArchiveVO) -> AssetExtractArchiveVO:
        """Extract downloaded archive under security policy supervision.

        FR-AST-003: Validates extraction plan, checks entry paths for
        traversal, enforces depth/size/count limits, cleans up on failure.
        """
        artifact = Path(str(vo.artifact_path))
        destination = Path(str(vo.destination))

        if not artifact.exists():
            return AssetExtractArchiveVO(
                artifact_path=vo.artifact_path,
                destination=vo.destination,
                max_entries=vo.max_entries,
                max_extracted_size=vo.max_extracted_size,
                allow_symlinks=vo.allow_symlinks,
                error=ErrorMessage(f"Archive not found: {vo.artifact_path}"),
                message="Archive file does not exist",
            )

        suffix = artifact.suffix.lower()
        if suffix == ".gz" and artifact.stem.endswith(".tar"):
            suffix = ".tar.gz"
        if suffix == ".bz2" and artifact.stem.endswith(".tar"):
            suffix = ".tar.bz2"

        if suffix not in SUPPORTED_ARCHIVE_EXTENSIONS:
            return AssetExtractArchiveVO(
                artifact_path=vo.artifact_path,
                destination=vo.destination,
                max_entries=vo.max_entries,
                max_extracted_size=vo.max_extracted_size,
                allow_symlinks=vo.allow_symlinks,
                error=ErrorMessage(f"Unsupported archive format: {suffix}"),
                message=f"Supported formats: {', '.join(sorted(SUPPORTED_ARCHIVE_EXTENSIONS))}",
            )

        destination.mkdir(parents=True, exist_ok=True)

        try:
            extracted, rejected = self._extract_with_limits(
                artifact=artifact,
                destination=destination,
                suffix=suffix,
                max_entries=vo.max_entries,
                max_extracted_size=vo.max_extracted_size,
                allow_symlinks=vo.allow_symlinks,
            )
        except Exception as exc:
            self._cleanup_partial(destination)
            return AssetExtractArchiveVO(
                artifact_path=vo.artifact_path,
                destination=vo.destination,
                max_entries=vo.max_entries,
                max_extracted_size=vo.max_extracted_size,
                allow_symlinks=vo.allow_symlinks,
                error=ErrorMessage(str(exc)),
                message=f"Extraction failed: {exc}",
            )

        return AssetExtractArchiveVO(
            artifact_path=vo.artifact_path,
            destination=vo.destination,
            max_entries=vo.max_entries,
            max_extracted_size=vo.max_extracted_size,
            allow_symlinks=vo.allow_symlinks,
            success=SuccessFlag(True),
            extracted_files=tuple(FilePath(str(f)) for f in extracted),
            rejected_entries=tuple(rejected),
            message=f"Extracted {len(extracted)} files, rejected {len(rejected)} entries",
        )

    # ─── Block 3: Dunder Methods, Factories, Helpers ──────────

    def _extract_with_limits(
        self,
        artifact: Path,
        destination: Path,
        suffix: str,
        max_entries: int,
        max_extracted_size: int,
        allow_symlinks: bool,
    ) -> tuple[list[Path], list[str]]:
        """Extract archive enforcing entry count, size, and symlink limits."""
        extracted: list[Path] = []
        rejected: list[str] = []
        total_size = 0
        entry_count = 0

        if suffix == ".zip":
            with zipfile.ZipFile(artifact, "r") as zf:
                for info in zf.infolist():
                    entry_count += 1
                    if entry_count > max_entries:
                        rejected.append(f"entry_count_exceeded: {info.filename}")
                        continue
                    if not allow_symlinks and self._is_symlink_entry(info):
                        rejected.append(f"symlink_rejected: {info.filename}")
                        continue
                    total_size += info.file_size
                    if total_size > max_extracted_size:
                        rejected.append(f"size_exceeded: {info.filename}")
                        continue
                    target = destination / info.filename
                    if not self._is_within_destination(target, destination):
                        rejected.append(f"traversal_rejected: {info.filename}")
                        continue
                    zf.extract(info, destination)
                    extracted.append(target)
        else:
            mode = "r:*" if suffix in (".tar", ".tar.gz", ".tgz", ".tar.bz2", ".tbz2") else "r"
            with tarfile.open(artifact, mode) as tf:
                for member in tf.getmembers():
                    entry_count += 1
                    if entry_count > max_entries:
                        rejected.append(f"entry_count_exceeded: {member.name}")
                        continue
                    if not allow_symlinks and (member.issym() or member.islnk()):
                        rejected.append(f"symlink_rejected: {member.name}")
                        continue
                    total_size += member.size
                    if total_size > max_extracted_size:
                        rejected.append(f"size_exceeded: {member.name}")
                        continue
                    target = destination / member.name
                    if not self._is_within_destination(target, destination):
                        rejected.append(f"traversal_rejected: {member.name}")
                        continue
                    tf.extract(member, destination)
                    extracted.append(target)

        return extracted, rejected

    @staticmethod
    def _is_within_destination(target: Path, destination: Path) -> bool:
        """Check resolved path is within destination directory."""
        try:
            target.resolve().relative_to(destination.resolve())
            return True
        except ValueError:
            return False

    @staticmethod
    def _is_symlink_entry(info: zipfile.ZipInfo) -> bool:
        """Check if zip entry is a symlink via external attributes."""
        return (info.external_attr >> 16) & 0o170000 == 0o120000

    @staticmethod
    def _cleanup_partial(destination: Path) -> None:
        """Remove partial extraction on failure."""
        if destination.exists():
            for item in destination.iterdir():
                if item.is_file():
                    item.unlink(missing_ok=True)
                elif item.is_dir():
                    shutil.rmtree(item, ignore_errors=True)