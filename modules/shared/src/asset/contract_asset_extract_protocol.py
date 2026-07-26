"""Asset domain contract: extract archive protocol (ABC based).

Defines the protocol for extracting downloaded archive artifacts
under security policy supervision.

FR-AST-003: Extract Asset Archive
AES Contract layer — pure ABC definitions, no implementation.
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from .taxonomy_asset_vo import AssetExtractArchiveVO


class AssetExtractProtocol(ABC):
    """Protocol for extracting archive artifacts into cache."""

    @abstractmethod
    async def extract_archive(self, vo: AssetExtractArchiveVO) -> AssetExtractArchiveVO:
        """Extract downloaded archive under security policy supervision.

        FR-AST-003: Delegates path validation, traversal rejection, depth/size
        and entry count limits to security policy feature. Returns extracted
        file references and rejected entry summary.
        """
        ...
