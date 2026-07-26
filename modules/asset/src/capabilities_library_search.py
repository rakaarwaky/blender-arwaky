"""Asset library search: search dedicated asset libraries (HDRI, textures).

FR-AST-003: Search External Asset Libraries
- Read-only search for HDRI and texture assets
- Filters by asset type and category
- Returns normalized list with preview/license metadata
"""

import logging

from modules.shared.src.asset import LibrarySearchResponse
from modules.shared.src.common.taxonomy_core_vo import (
    AssetTypeFilter,
    ErrorMessage,
    NextPageToken,
    SearchQuery,
)
from modules.shared.src.common.taxonomy_domain_error import ProviderError

logger = logging.getLogger("BlenderMCPServer")


class LibrarySearchCapability:
    """Business logic for searching dedicated asset libraries."""

    def __init__(self, library_providers: dict[str, object]) -> None:  # AssetProviderPort implementations
        self._providers = library_providers

    async def search_library_assets(
        self,
        query: SearchQuery,
        asset_type: AssetTypeFilter,
        categories: list[str] | None = None,
        page_token: str | None = None,
    ) -> LibrarySearchResponse:
        """Search dedicated asset libraries for environment/surface assets.

        FR-AST-003: Strictly read-only, no downloads triggered.
        """
        all_results: list = []
        warnings: list[str] = []

        for provider_name, provider in self._providers.items():
            try:
                # Search through each provider's search_assets method
                if hasattr(provider, "search_assets"):
                    from modules.shared.src.asset.taxonomy_asset_vo import AssetSearchVO

                    request = AssetSearchVO(
                        query=query,
                    )
                    response = await provider.search_assets(request)
                    for item in response.assets:
                        all_results.append(item)
            except ProviderError as e:
                warnings.append(f"Provider {provider_name} error: {e}")
                logger.warning("Library search warning for %s: %s", provider_name, e)

        return LibrarySearchResponse(
            assets=all_results,
            total=len(all_results),
            next_token=NextPageToken("") if page_token else None,
            warnings=[ErrorMessage(w) for w in warnings] if warnings else None,
        )