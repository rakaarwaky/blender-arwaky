"""Production asset-provider connection for FR-AST-001..005.

The provider boundary is intentionally small: provider utilities send named
commands and receive normalized dictionaries. The implementation uses the
standard-library HTTP client so the feature has no optional runtime dependency;
tests can inject an opener and never need network access.
"""

from __future__ import annotations

import asyncio
import json
import logging
import os
import re
import urllib.error
import urllib.parse
import urllib.request
from collections.abc import Callable
from pathlib import Path
from typing import Any

from modules.shared.src.asset.contract_asset_provider_connection_protocol import (
    IAssetProviderConnection,
)
from modules.shared.src.common.taxonomy_core_vo import ProviderName

logger = logging.getLogger("BlenderMCPServer")

HttpOpener = Callable[..., Any]


class AssetProviderConnectionImpl(IAssetProviderConnection):
    """Call real provider APIs through an injectable HTTP opener.

    Poly Haven is public for search/details/files. Sketchfab search/details and
    model download require ``SKETCHFAB_API_TOKEN``. Missing credentials are
    returned as categorized provider errors rather than a synthetic success.
    """

    POLYHAVEN_API = "https://api.polyhaven.com"
    SKETCHFAB_API = "https://api.sketchfab.com/v3"

    def __init__(
        self,
        *,
        timeout_seconds: float = 20.0,
        sketchfab_token: str | None = None,
        opener: HttpOpener | None = None,
    ) -> None:
        if timeout_seconds <= 0:
            raise ValueError("timeout_seconds must be positive")
        self._timeout_seconds = timeout_seconds
        self._sketchfab_token = sketchfab_token or os.getenv("SKETCHFAB_API_TOKEN")
        self._opener = opener or urllib.request.urlopen

    async def send_command(
        self,
        action: str,
        payload: dict[str, object],
        provider: ProviderName | None = None,
    ) -> dict[str, object]:
        """Execute one provider command without returning synthetic success."""
        try:
            return await asyncio.to_thread(self._send_command_sync, action, payload, provider)
        except ProviderConnectionError as exc:
            logger.warning("Asset provider command failed action=%s: %s", action, exc)
            return {"error": exc.category, "message": str(exc)}
        except Exception as exc:
            logger.exception("Unexpected asset provider command failure action=%s", action)
            return {"error": "provider_error", "message": str(exc)}

    def _send_command_sync(
        self,
        action: str,
        payload: dict[str, object],
        _provider: ProviderName | None,
    ) -> dict[str, object]:
        if action == "search_polyhaven_assets":
            return self._search_polyhaven(payload)
        if action == "get_polyhaven_asset_details":
            return self._get_polyhaven_details(payload)
        if action == "download_polyhaven_asset":
            return self._download_polyhaven(payload)
        if action == "search_sketchfab_models":
            return self._search_sketchfab(payload)
        if action == "get_sketchfab_model_preview":
            return self._get_sketchfab_details(payload)
        if action == "download_sketchfab_model":
            return self._download_sketchfab(payload)
        raise ProviderConnectionError("unsupported_action", f"Unsupported provider action: {action}")

    def _search_polyhaven(self, payload: dict[str, object]) -> dict[str, object]:
        query = str(payload.get("query", "")).strip().lower()
        data = self._request_json(f"{self.POLYHAVEN_API}/assets")
        if not isinstance(data, dict):
            raise ProviderConnectionError("invalid_response", "Poly Haven returned an invalid asset index")
        categories = {str(value).lower() for value in payload.get("categories", []) if value}
        assets: dict[str, dict[str, object]] = {}
        for asset_id, raw in data.items():
            item = raw if isinstance(raw, dict) else {}
            name = str(item.get("name", asset_id))
            item_categories = {str(value).lower() for value in item.get("categories", []) if value}
            if query and query not in f"{asset_id} {name}".lower():
                continue
            if categories and not categories.intersection(item_categories):
                continue
            assets[str(asset_id)] = {
                "name": name,
                "type": str(item.get("type", "unknown")),
                "categories": sorted(item_categories),
            }
        return {"assets": assets, "provider": "Polyhaven"}

    def _get_polyhaven_details(self, payload: dict[str, object]) -> dict[str, object]:
        asset_id = self._required_identifier(payload, "asset_id")
        return self._request_json(f"{self.POLYHAVEN_API}/assets/{urllib.parse.quote(asset_id)}")

    def _download_polyhaven(self, payload: dict[str, object]) -> dict[str, object]:
        asset_id = self._required_identifier(payload, "asset_id")
        destination = self._required_path(payload, "destination_path")
        asset_type = str(payload.get("asset_type", "model")).lower()
        files = self._request_json(f"{self.POLYHAVEN_API}/files/{urllib.parse.quote(asset_id)}")
        download_url = self._select_download_url(files, asset_type)
        if download_url is None:
            raise ProviderConnectionError("asset_not_downloadable", f"No downloadable Poly Haven file for {asset_id}")
        self._download_file(download_url, destination, payload.get("max_size"))
        return {"success": True, "path": destination, "provider": "Polyhaven"}

    def _search_sketchfab(self, payload: dict[str, object]) -> dict[str, object]:
        self._require_sketchfab_token()
        query = str(payload.get("query", "")).strip()
        params = {
            "type": "models",
            "q": query,
            "count": str(int(payload.get("count", 20))),
            "downloadable": "true",
        }
        result = self._request_json(
            f"{self.SKETCHFAB_API}/search?{urllib.parse.urlencode(params)}", self._sketchfab_headers()
        )
        if not isinstance(result, dict):
            raise ProviderConnectionError("invalid_response", "Sketchfab returned an invalid search response")
        return {"results": result.get("results", []), "provider": "Sketchfab"}

    def _get_sketchfab_details(self, payload: dict[str, object]) -> dict[str, object]:
        self._require_sketchfab_token()
        uid = self._required_identifier(payload, "uid")
        return self._request_json(f"{self.SKETCHFAB_API}/models/{urllib.parse.quote(uid)}", self._sketchfab_headers())

    def _download_sketchfab(self, payload: dict[str, object]) -> dict[str, object]:
        self._require_sketchfab_token()
        uid = self._required_identifier(payload, "uid")
        destination = self._required_path(payload, "destination_path")
        result = self._request_json(
            f"{self.SKETCHFAB_API}/models/{urllib.parse.quote(uid)}/download", self._sketchfab_headers()
        )
        download_url = self._select_download_url(result, "model")
        if download_url is None:
            raise ProviderConnectionError("asset_not_downloadable", f"Sketchfab model {uid} has no download URL")
        self._download_file(download_url, destination, payload.get("max_size"), self._sketchfab_headers())
        return {"success": True, "path": destination, "provider": "Sketchfab"}

    def _request_json(
        self,
        url: str,
        headers: dict[str, str] | None = None,
    ) -> dict[str, object]:
        request = urllib.request.Request(url, headers=headers or {}, method="GET")
        try:
            with self._opener(request, timeout=self._timeout_seconds) as response:
                status = int(getattr(response, "status", 200))
                body = response.read()
        except urllib.error.HTTPError as exc:
            category = "missing_credentials" if exc.code in {401, 403} else "provider_http_error"
            raise ProviderConnectionError(category, f"Provider HTTP status {exc.code}") from exc
        except (urllib.error.URLError, TimeoutError, OSError) as exc:
            raise ProviderConnectionError("provider_unavailable", f"Provider request failed: {exc}") from exc
        if status < 200 or status >= 300:
            raise ProviderConnectionError("provider_http_error", f"Provider HTTP status {status}")
        try:
            value = json.loads(body.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise ProviderConnectionError("invalid_response", "Provider returned invalid JSON") from exc
        if not isinstance(value, dict):
            raise ProviderConnectionError("invalid_response", "Provider JSON response must be an object")
        return value

    def _download_file(
        self,
        url: str,
        destination: str,
        max_size: object = None,
        headers: dict[str, str] | None = None,
    ) -> None:
        destination_path = Path(destination)
        destination_path.parent.mkdir(parents=True, exist_ok=True)
        tmp_path = destination_path.with_name(f".{destination_path.name}.download")
        max_bytes = int(max_size) if max_size is not None else None
        request = urllib.request.Request(url, headers=headers or {}, method="GET")
        total = 0
        try:
            with self._opener(request, timeout=self._timeout_seconds) as response, tmp_path.open("wb") as output:
                while True:
                    chunk = response.read(1024 * 1024)
                    if not chunk:
                        break
                    total += len(chunk)
                    if max_bytes is not None and total > max_bytes:
                        raise ProviderConnectionError("oversized_asset", f"Download exceeds max size {max_bytes}")
                    output.write(chunk)
            if total == 0:
                raise ProviderConnectionError("empty_download", "Provider returned an empty asset")
            os.replace(tmp_path, destination_path)
        except ProviderConnectionError:
            tmp_path.unlink(missing_ok=True)
            raise
        except (urllib.error.URLError, TimeoutError, OSError) as exc:
            tmp_path.unlink(missing_ok=True)
            raise ProviderConnectionError("provider_unavailable", f"Asset download failed: {exc}") from exc

    def _select_download_url(self, value: object, asset_type: str) -> str | None:
        preferred = ("hdr", "exr") if asset_type == "hdri" else ("glb", "gltf", "fbx", "obj", "zip")
        candidates: list[str] = []

        def collect(node: object) -> None:
            if isinstance(node, str) and node.startswith(("http://", "https://")):
                candidates.append(node)
            elif isinstance(node, dict):
                for child in node.values():
                    collect(child)
            elif isinstance(node, list):
                for child in node:
                    collect(child)

        collect(value)
        for suffix in preferred:
            for candidate in candidates:
                if re.search(rf"\.{re.escape(suffix)}(?:$|[?])", candidate, re.IGNORECASE):
                    return candidate
        return candidates[0] if candidates else None

    def _sketchfab_headers(self) -> dict[str, str]:
        self._require_sketchfab_token()
        return {"Authorization": f"Bearer {self._sketchfab_token}"}

    def _require_sketchfab_token(self) -> None:
        if not self._sketchfab_token:
            raise ProviderConnectionError("missing_credentials", "SKETCHFAB_API_TOKEN is required for Sketchfab")

    @staticmethod
    def _required_identifier(payload: dict[str, object], key: str) -> str:
        value = str(payload.get(key, "")).strip()
        if not value:
            raise ProviderConnectionError("validation_error", f"{key} is required")
        return value

    @staticmethod
    def _required_path(payload: dict[str, object], key: str) -> str:
        value = str(payload.get(key, "")).strip()
        if not value:
            raise ProviderConnectionError("validation_error", f"{key} is required")
        return value


class ProviderConnectionError(RuntimeError):
    """Categorized provider boundary failure."""

    def __init__(self, category: str, message: str) -> None:
        super().__init__(message)
        self.category = category
