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
from .taxonomy_asset_vo import AssetSearchVO


class LibrarySearchProtocol(ABC):
    """Protocol for searching dedicated asset libraries."""

    @abstractmethod
    async def search_library_assets(
        self,
        query: SearchQuery,
        asset_type: AssetTypeFilter,
        categories: list[str] | None = None,
        page_token: str | None = None,
    ) -> AssetSearchVO:
        """Search dedicated asset libraries for environment/surface assets.

        FR-AST-003: Strictly read-only, no downloads triggered.
        Filters by asset type (HDRI, texture) and category.
        Returns unified VO with normalized list of preview/license metadata.
        """
        pass