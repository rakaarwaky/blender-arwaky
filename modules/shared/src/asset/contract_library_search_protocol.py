"""Asset domain contract: library search protocol (ABC based).

Defines the protocol for searching dedicated asset libraries (HDRI, textures).
AES Contract layer — pure ABC definitions, no implementation.

FR-AST-003: Search External Asset Libraries
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from modules.shared.src.common.taxonomy_core_vo import (
    AssetTypeFilter,
    SearchQuery,
)


class LibraryAssetMetadata:
    """Normalized library asset metadata."""

    def __init__(
        self,
        id: str,
        name: str,
        asset_type: str,
        provider: str,
        tags: list[str] | None = None,
        thumbnail_url: str | None = None,
        license_summary: str | None = None,
    ) -> None:
        self.id = id
        self.name = name
        self.asset_type = asset_type
        self.provider = provider
        self.tags = tags or []
        self.thumbnail_url = thumbnail_url
        self.license_summary = license_summary


class LibrarySearchResponse:
    """Response from library search."""

    def __init__(
        self,
        assets: list[LibraryAssetMetadata],
        total: int = 0,
        next_token: str | None = None,
        provider: str | None = None,
        warnings: list[str] | None = None,
    ) -> None:
        self.assets = assets
        self.total = total
        self.next_token = next_token
        self.provider = provider
        self.warnings = warnings or []


class LibrarySearchProtocol(ABC):
    """Protocol for searching dedicated asset libraries."""

    @abstractmethod
    async def search_library_assets(
        self,
        query: SearchQuery,
        asset_type: AssetTypeFilter,
        categories: list[str] | None = None,
        page_token: str | None = None,
    ) -> LibrarySearchResponse:
        """Search dedicated asset libraries for environment/surface assets.

        FR-AST-003: Strictly read-only, no downloads triggered.
        Filters by asset type (HDRI, texture) and category.
        Returns normalized list with preview/license metadata.
        """
        pass