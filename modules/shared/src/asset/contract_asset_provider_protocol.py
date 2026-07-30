"""Asset domain contract: provider metadata normalization protocol (ABC based).

Defines the protocol for normalizing provider-specific asset descriptions
into one consistent metadata shape consumed across the system.

FR-AST-005: Manage Provider Metadata
AES Contract layer — pure ABC definitions, no implementation.
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from modules.shared.src.asset.taxonomy_asset_metadata_vo import ProviderMetadataVO
from modules.shared.src.common.taxonomy_core_vo import (
    AssetId,
    ProviderName,
)


class AssetProviderProtocol(ABC):
    """Protocol for normalizing provider asset metadata.

    FR-AST-005: Normalized metadata includes name, provider, type,
    categories, preview/thumbnail, license summary, and download
    availability. Missing optional fields fall back to safe empty values.
    Provider secrets and credentials never exposed.
    """

    @abstractmethod
    async def normalize_metadata(
        self,
        raw_provider_data: dict[str, object],
        provider_name: ProviderName,
        asset_id: AssetId,
    ) -> ProviderMetadataVO:
        """Normalize provider-specific asset description into common shape.

        FR-AST-005: Includes at least name, provider, type, categories,
        preview reference, license summary, and download availability flag.
        Missing optional fields fall back to safe empty values. License
        information is informational only; does not constitute legal clearance.

        Args:
            raw_provider_data: Raw provider asset description dict.
            provider_name: Provider identifier.
            asset_id: Asset identifier from provider.

        Returns:
            Dict with normalized metadata including name, provider, type,
            categories, thumbnail_url, license_summary, download_available,
            and any preserved provider-specific extra fields.
        """
        ...

    @abstractmethod
    async def get_provider_capabilities(
        self,
        provider_name: ProviderName,
    ) -> dict[str, object]:
        """Get normalized provider capability metadata.

        FR-AST-005: Describes supported asset types, pagination behavior,
        and authentication requirements for the provider.

        Args:
            provider_name: Provider identifier.

        Returns:
            Dict with provider capabilities, supported types,
            pagination behavior, and auth requirements.
        """
        ...
