"""Asset domain contract: extract archive protocol (ABC based).

Defines the protocol for extracting downloaded archive artifacts
under security policy supervision.

FR-AST-003: Extract Asset Archive
AES Contract layer — pure ABC definitions, no implementation.
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from modules.shared.src.common.taxonomy_core_vo import FilePath


class AssetExtractProtocol(ABC):
    """Protocol for extracting archive artifacts into cache.

    FR-AST-003: Delegates all archive safety decisions to security
    policy feature: entry path validation, traversal rejection, depth/size
    and entry count limits, symbolic link and hard link policy.
    Never implements path traversal protection locally.
    """

    @abstractmethod
    async def extract_archive(
        self,
        artifact_path: FilePath,
        destination: FilePath,
        max_entries: int = 1000,
        max_extracted_size: int = 1073741824,
        allow_symlinks: bool = False,
    ) -> dict[str, object]:
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
            Dict with success indicator, extracted file references,
            rejected entry summary, and message.
        """
        ...
