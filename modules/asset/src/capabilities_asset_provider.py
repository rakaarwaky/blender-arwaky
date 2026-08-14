"""Capability: Provider metadata normalization (FR-AST-005).

Implements AssetProviderMetadataProtocol for normalizing provider-specific
asset descriptions into one consistent metadata shape.
"""

from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Any

from modules.shared.src.asset.contract_asset_provider_protocol import (
    AssetProviderProtocol,
)
from modules.shared.src.asset.taxonomy_asset_metadata_vo import ProviderMetadataVO
from modules.shared.src.common.taxonomy_core_vo import (
    AssetId,
    AssetType,
    ProviderName,
    TagList,
    ThumbnailUrl,
)

logger = logging.getLogger("BlenderMCPServer")


class AssetProviderMetadataCapability(AssetProviderProtocol):
    """Provider metadata normalization capability.

    FR-AST-005: Normalized metadata includes name, provider, type,
    categories, preview/thumbnail, license summary, and download
    availability flag. Missing optional fields fall back to safe empty values.
    Provider secrets and credentials never exposed.
    """

    def __init__(self, cache_ttl_seconds: int = 3600) -> None:
        """Initialize with optional cache TTL.

        Args:
            cache_ttl_seconds: Cache freshness window in seconds.
        """
        self.cache_ttl_seconds = cache_ttl_seconds
        self._metadata_cache: dict[str, dict[str, Any]] = {}
        self._provider_capabilities: dict[str, dict[str, Any]] = {}

    async def normalize_metadata(
        self,
        raw_provider_data: dict[str, Any],
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
            ProviderMetadataVO with normalized metadata fields.
        """
        cache_key = f"{provider_name}:{asset_id}"

        # Check cache freshness with stale-refresh logic (FR-AST-005 / R03)
        if cache_key in self._metadata_cache:
            cached = self._metadata_cache[cache_key]
            age = (datetime.now(timezone.utc) - cached["timestamp"]).total_seconds()

            if age < self.cache_ttl_seconds:
                logger.debug("Using fresh cached metadata for %s", cache_key)
                return cached["vo"]

            # R03: Stale metadata refreshed before use
            logger.debug("Cached metadata stale for %s (age=%.1fs), refreshing", cache_key, age)
            # Continue to normalization below to fetch fresh data

        # Normalize fields
        normalized = ProviderMetadataVO(
            name=ProviderName(self._extract_name(raw_provider_data)),
            provider=provider_name,
            id=asset_id,
            type=AssetType(self._extract_type(raw_provider_data)),
            categories=TagList(self._extract_categories(raw_provider_data)),
            thumbnail_url=ThumbnailUrl(self._extract_thumbnail(raw_provider_data))
            if self._extract_thumbnail(raw_provider_data)
            else None,
            license_summary=self._extract_license(raw_provider_data),
            download_available=self._extract_download_availability(raw_provider_data),
            attribution=self._extract_attribution(raw_provider_data),
            extra_fields=self._extract_extra_fields(raw_provider_data),
            normalized_at=datetime.now(timezone.utc).isoformat(),
        )

        # Cache normalized result
        self._metadata_cache[cache_key] = {
            "vo": normalized,
            "timestamp": datetime.now(timezone.utc),
        }

        logger.debug("Normalized metadata for %s from %s", asset_id, provider_name)
        return normalized

    async def get_provider_capabilities(
        self,
        provider_name: ProviderName,
    ) -> dict[str, Any]:
        """Get normalized provider capability metadata.

        FR-AST-005: Describes supported asset types, pagination behavior,
        and authentication requirements for the provider.

        Args:
            provider_name: Provider identifier.

        Returns:
            Dict with provider capabilities, supported types,
            pagination behavior, and auth requirements.
        """
        if provider_name in self._provider_capabilities:
            return dict(self._provider_capabilities[provider_name])

        # Default capabilities - providers can override via their adapter
        capabilities = {
            "provider": provider_name,
            "supported_types": ["model", "texture", "hdri"],
            "pagination": {"supported": True, "default_limit": 50},
            "auth_required": False,
            "rate_limit": None,
            "cache_freshness_seconds": self.cache_ttl_seconds,
        }

        self._provider_capabilities[provider_name] = capabilities
        return capabilities

    def _extract_name(self, data: dict[str, Any]) -> str:
        """Extract asset name from raw provider data."""
        for key in ("name", "title", "asset_name", "filename"):
            if key in data and data[key]:
                return str(data[key])
        return ""

    def _extract_type(self, data: dict[str, Any]) -> str:
        """Extract asset type from raw provider data."""
        for key in ("type", "asset_type", "category"):
            if key in data and data[key]:
                return str(data[key]).lower()
        return "model"  # Default type

    def _extract_categories(self, data: dict[str, Any]) -> list[str]:
        """Extract categories from raw provider data."""
        for key in ("categories", "tags", "keywords", "labels"):
            if key in data and data[key]:
                items = data[key]
                if isinstance(items, str):
                    return [items]
                if isinstance(items, list):
                    return [str(i) for i in items]
        return []

    def _extract_thumbnail(self, data: dict[str, Any]) -> str | None:
        """Extract thumbnail URL from raw provider data."""
        for key in ("thumbnail_url", "preview_url", "image_url", "poster_url"):
            if key in data and data[key]:
                url = str(data[key])
                # Reject unsafe protocols
                url_lower = url.lower()
                if any(proto in url_lower for proto in ("file://", "javascript:", "data:")):
                    return None
                # Never embed credentials or signed URLs
                if "token=" in url or "signature=" in url or "X-Amz-" in url:
                    return None
                # Only allow HTTPS
                if not url.startswith("https://"):
                    logger.warning("Non-HTTPS thumbnail URL rejected: %s", url)
                    return None
                return url
        return None

    def _extract_license(self, data: dict[str, Any]) -> str | None:
        """Extract license summary from raw provider data."""
        for key in ("license", "license_summary", "license_type", "copyright"):
            if key in data and data[key]:
                val = str(data[key])
                # Keep it short - summary only
                return val[:100] if len(val) > 100 else val
        return None

    def _extract_download_availability(self, data: dict[str, Any]) -> bool:
        """Extract download availability flag."""
        for key in ("download_available", "is_downloadable", "has_download"):
            if key in data and data[key]:
                return bool(data[key])
        return True  # Default to available

    def _extract_attribution(self, data: dict[str, Any]) -> str | None:
        """Extract attribution requirements."""
        for key in ("attribution", "credit", "author", "artist"):
            if key in data and data[key]:
                return str(data[key])
        return None

    def _extract_extra_fields(self, data: dict[str, Any]) -> dict[str, Any]:
        """Extract provider-specific extra fields without breaking common shape."""
        reserved_keys = {
            "name",
            "provider",
            "id",
            "type",
            "categories",
            "thumbnail_url",
            "license_summary",
            "download_available",
            "attribution",
            "extra_fields",
            "normalized_at",
        }
        return {k: v for k, v in data.items() if k not in reserved_keys}
