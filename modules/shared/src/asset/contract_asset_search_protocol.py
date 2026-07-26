"""Asset domain contract: asset search protocol (ABC based).

Defines the protocol for unified multi-provider asset search.

FR-AST-001: Search Assets Across Providers
AES Contract layer — pure ABC definitions, no implementation.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from modules.shared.src.common.taxonomy_core_vo import (
    AssetIdList,
    AssetTypeFilter,
    NextPageToken,
    ProviderName,
    ResultLimit,
    SearchQuery,
)
from .taxonomy_asset_data_vo import AssetMetadata


class AssetSearchProtocol(ABC):
    """Protocol for unified multi-provider asset search.

    FR-AST-001: Single search operation regardless of provider count.
    Returns normalized, aggregated results with pagination and warnings.
    """

    @abstractmethod
    async def search_all(
        self,
        query: SearchQuery,
        providers: list[ProviderName] | None = None,
        asset_type_filter: AssetTypeFilter | None = None,
        limit: ResultLimit | None = None,
        page_token: NextPageToken | None = None,
    ) -> dict[str, Any]:
        """Search across all enabled providers with unified response.

        FR-AST-001: Each enabled provider queried independently.
        Failures logged and skipped; partial results returned when possible.
        Results normalized into common asset metadata shape before aggregation.

        Args:
            query: Text search query.
            providers: Optional provider filter; None means all enabled.
            asset_type_filter: Optional asset type filter.
            limit: Optional result limit per provider.
            page_token: Optional pagination cursor.

        Returns:
            Dict with normalized assets list, provider status summary,
            pagination metadata, and warnings.
        """
        ...
