from __future__ import annotations

import json
from pathlib import Path
from urllib.error import HTTPError

import pytest

from modules.asset.src.capabilities_asset_provider_connection import AssetProviderConnectionImpl


class FakeResponse:
    def __init__(self, body: bytes, status: int = 200) -> None:
        self.body = body
        self.status = status
        self._read = False

    def read(self, _size: int = -1) -> bytes:
        if self._read:
            return b""
        self._read = True
        return self.body

    def __enter__(self) -> "FakeResponse":
        return self

    def __exit__(self, *_args: object) -> None:
        return None


def test_polyhaven_search_uses_real_http_boundary() -> None:
    calls: list[str] = []

    def opener(request, timeout: float):
        calls.append(f"{request.full_url}:{timeout}")
        return FakeResponse(
            json.dumps({"chair": {"name": "Chair", "type": "model", "categories": ["Furniture"]}}).encode()
        )

    connection = AssetProviderConnectionImpl(opener=opener, timeout_seconds=4.0)
    result = __import__("asyncio").run(connection.send_command("search_polyhaven_assets", {"query": "chair"}))

    assert result["assets"]["chair"]["name"] == "Chair"  # nosec B101
    assert calls and "/assets" in calls[0]  # nosec B101
    assert "status" not in result  # nosec B101


@pytest.mark.asyncio
async def test_polyhaven_download_writes_requested_destination(tmp_path: Path) -> None:
    destination = tmp_path / "asset.cache"
    calls: list[str] = []

    def opener(request, timeout: float):
        calls.append(request.full_url)
        if request.full_url.endswith("/files/chair"):
            return FakeResponse(json.dumps({"blend": {"hdr": {"url": "https://cdn.example/chair.hdr"}}}).encode())
        return FakeResponse(b"HDR-DATA")

    connection = AssetProviderConnectionImpl(opener=opener)
    result = await connection.send_command(
        "download_polyhaven_asset",
        {"asset_id": "chair", "asset_type": "hdri", "destination_path": str(destination)},
    )

    assert result["success"] is True  # nosec B101
    assert destination.read_bytes() == b"HDR-DATA"  # nosec B101
    assert calls[-1] == "https://cdn.example/chair.hdr"  # nosec B101


@pytest.mark.asyncio
async def test_sketchfab_requires_explicit_token() -> None:
    connection = AssetProviderConnectionImpl(sketchfab_token=None, opener=lambda *_args, **_kwargs: FakeResponse(b"{}"))
    result = await connection.send_command("search_sketchfab_models", {"query": "chair"})

    assert result["error"] == "missing_credentials"  # nosec B101
    assert "SKETCHFAB_API_TOKEN" in result["message"]  # nosec B101


@pytest.mark.asyncio
async def test_provider_http_failure_is_categorized() -> None:
    def opener(request, timeout: float):
        raise HTTPError(request.full_url, 503, "unavailable", {}, None)

    connection = AssetProviderConnectionImpl(opener=opener)
    result = await connection.send_command("search_polyhaven_assets", {"query": "chair"})

    assert result["error"] == "provider_http_error"  # nosec B101
    assert "503" in result["message"]  # nosec B101
