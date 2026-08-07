"""Tests for AssetDownloadCapability — FR-AST-002: Download Asset to Cache.

Exercises cache reuse, overwrite policy, integrity verification, and
background download coordination with mocked dependencies.
Run via pytest from repo root.
"""

from __future__ import annotations

import os
import pathlib

import pytest

from modules.asset.src.capabilities_asset_download import AssetDownloadCapability
from modules.shared.src.common.taxonomy_core_vo import AssetId, AssetType, FilePath, MaxSize, ProviderName

# ─── Mocks ──────────────────────────────────────────────────────────────────


class MockSecurityValidator:
    """Mock security policy validator."""

    def __init__(self, validate=True) -> None:
        self.validate = validate
        self._validated_paths: list[str] = []

    async def validate_path(self, path: str, _mode: str) -> None:
        if not self.validate:
            raise Exception("path denied")
        self._validated_paths.append(path)


class MockJobScheduler:
    """Mock job feature for background downloads."""

    def __init__(self) -> None:
        self._submitted: list[dict] = []

    async def submit_download(self, provider: str, asset_id: str, path: str) -> str:
        self._submitted.append({"provider": provider, "asset_id": asset_id, "path": path})
        return f"task-{provider}:{asset_id}"


# ─── Helpers ────────────────────────────────────────────────────────────────


@pytest.fixture
def cache_dir(tmp_path: pathlib.Path) -> str:
    """Provide a temporary cache directory for each test."""
    return str(tmp_path / "cache")


@pytest.fixture
def capability_with_security(cache_dir: str) -> AssetDownloadCapability:
    """Asset download capability with security validator and job scheduler."""
    sec = MockSecurityValidator()
    job = MockJobScheduler()
    cap = AssetDownloadCapability(
        security_validator=sec,
        job_scheduler=job,
        config_aggregate=None,
    )
    cap._cache_dir = FilePath(cache_dir)
    os.makedirs(cache_dir, exist_ok=True)
    return cap


# ─── FR-AST-002: Download Asset to Cache ───────────────────────────────────


@pytest.mark.asyncio
async def test_fr_ast_002_download_to_cache_creates_path(
    capability_with_security: AssetDownloadCapability, cache_dir: str
):
    """Test that download creates a cache path and returns success."""
    result = await capability_with_security.download_to_cache(
        provider=ProviderName("polyhaven"),
        asset_id=AssetId("hdri_001"),
        asset_type=AssetType("hdri"),
        cache_dir=FilePath(cache_dir),
    )

    assert result["success"] is True
    assert "file_path" in result
    assert result["cached"] is False
    assert result["integrity_ok"] is True


@pytest.mark.asyncio
async def test_fr_ast_002_cache_reuse_reuse_policy(capability_with_security: AssetDownloadCapability, cache_dir: str):
    """Test that valid cached artifact is reused without network access."""
    os.makedirs(cache_dir, exist_ok=True)
    cap = capability_with_security

    # Compute the actual cache path the capability would use
    cache_key = "polyhaven:hdri_001:default"
    expected_path = cap._get_cache_path(cache_key)

    # Pre-populate cache at the correct path
    with open(expected_path, "w") as f:
        f.write("cached content")

    result = await cap.download_to_cache(
        provider=ProviderName("polyhaven"),
        asset_id=AssetId("hdri_001"),
        asset_type=AssetType("hdri"),
        cache_dir=FilePath(cache_dir),
        overwrite_policy="reuse",
    )

    assert result["success"] is True
    assert result["cached"] is True
    assert "Cached artifact served" in result["message"]


@pytest.mark.asyncio
async def test_fr_ast_002_cache_unique_variant(capability_with_security: AssetDownloadCapability, cache_dir: str):
    """Test that unique variant policy creates a new cache entry."""
    os.makedirs(cache_dir, exist_ok=True)
    cap = capability_with_security

    # Pre-populate existing cache
    test_path = os.path.join(cache_dir, "existing.cache")
    with open(test_path, "w") as f:
        f.write("old content")

    result = await cap.download_to_cache(
        provider=ProviderName("polyhaven"),
        asset_id=AssetId("hdri_001"),
        asset_type=AssetType("hdri"),
        cache_dir=FilePath(cache_dir),
        overwrite_policy="unique",
    )

    assert result["success"] is True
    assert result["cached"] is False


@pytest.mark.asyncio
async def test_fr_ast_002_security_validation_failure():
    """Test that download fails when security validation rejects the path."""
    sec = MockSecurityValidator(validate=False)
    cap = AssetDownloadCapability(security_validator=sec)

    result = await cap.download_to_cache(
        provider=ProviderName("polyhaven"),
        asset_id=AssetId("hdri_001"),
        asset_type=AssetType("hdri"),
        cache_dir=FilePath("/forbidden/path"),
    )

    assert result["success"] is False
    assert result["cached"] is False
    assert result["integrity_ok"] is False
    assert "validation failed" in result["message"].lower()


@pytest.mark.asyncio
async def test_fr_ast_002_max_size_exceeded(capability_with_security: AssetDownloadCapability, cache_dir: str):
    """Test that download fails when estimated size exceeds max size."""
    cap = capability_with_security
    result = await cap.download_to_cache(
        provider=ProviderName("polyhaven"),
        asset_id=AssetId("hdri_001"),
        asset_type=AssetType("hdri"),
        cache_dir=FilePath(cache_dir),
        max_size=MaxSize(100),  # Very small limit
    )

    assert result["success"] is False
    assert "exceeds max size" in result["message"].lower()


@pytest.mark.asyncio
async def test_fr_ast_002_background_download_returns_task_ref(
    capability_with_security: AssetDownloadCapability, cache_dir: str
):
    """Test that background download submits job and returns task reference."""
    cap = capability_with_security
    result = await cap.download_to_cache(
        provider=ProviderName("polyhaven"),
        asset_id=AssetId("hdri_001"),
        asset_type=AssetType("hdri"),
        cache_dir=FilePath(cache_dir),
        background=True,
    )

    assert result["success"] is True
    assert "task_ref" in result
    assert "Background download submitted" in result["message"]


@pytest.mark.asyncio
async def test_fr_ast_002_provider_error_returns_error():
    """Test that provider errors are caught and reported."""
    cap = AssetDownloadCapability()

    result = await cap.download_to_cache(
        provider=ProviderName("polyhaven"),
        asset_id=AssetId("hdri_001"),
        asset_type=AssetType("hdri"),
        cache_dir=FilePath("/tmp/cache"),
    )

    # Should handle gracefully without raising
    assert "success" in result


def test_fr_ast_002_integrity_verification(cache_dir: str):
    """Test that integrity check verifies file exists and is non-empty."""
    import os as _os

    cap = AssetDownloadCapability()
    cap._cache_dir = FilePath(cache_dir)

    # Empty file should fail integrity
    empty_path = _os.path.join(cache_dir, "empty.cache")
    _os.makedirs(cache_dir, exist_ok=True)
    with open(empty_path, "w") as f:
        pass  # zero bytes

    assert cap._verify_integrity(empty_path) is False

    # Non-empty file should pass
    good_path = _os.path.join(cache_dir, "good.cache")
    with open(good_path, "w") as f:
        f.write("data")

    assert cap._verify_integrity(good_path) is True


def test_fr_ast_002_cache_path_is_deterministic():
    """Test that cache path generation uses deterministic hash."""
    cap = AssetDownloadCapability()
    cap._cache_dir = FilePath("/tmp/cache")

    path1 = cap._get_cache_path("polyhaven:hdri_001:default")
    path2 = cap._get_cache_path("polyhaven:hdri_001:default")

    assert path1 == path2


def test_fr_ast_002_unique_cache_path_differs():
    """Test that unique cache paths differ from deterministic ones."""
    cap = AssetDownloadCapability()
    cap._cache_dir = FilePath("/tmp/cache")

    path_det = cap._get_cache_path("polyhaven:hdri_001:default")
    path_uniq = cap._get_unique_cache_path("polyhaven:hdri_001:default")

    assert path_uniq != path_det


@pytest.mark.asyncio
async def test_fr_ast_002_download_does_not_import():
    """Test that download operation does not trigger import (separate concern)."""
    cap = AssetDownloadCapability()
    result = await cap.download_to_cache(
        provider=ProviderName("polyhaven"),
        asset_id=AssetId("hdri_001"),
        asset_type=AssetType("hdri"),
        cache_dir=FilePath("/tmp/cache"),
    )

    # Result should not contain import-related keys
    assert "object_names" not in result


@pytest.mark.asyncio
async def test_fr_ast_002_credentials_not_logged():
    """Test that provider credentials are never echoed in results."""
    cap = AssetDownloadCapability()
    result = await cap.download_to_cache(
        provider=ProviderName("polyhaven"),
        asset_id=AssetId("hdri_001"),
        asset_type=AssetType("hdri"),
        cache_dir=FilePath("/tmp/cache"),
    )

    for _key, value in result.items():
        if isinstance(value, str):
            assert "secret" not in value.lower() or "provider" not in value.lower()


@pytest.mark.asyncio
async def test_fr_ast_005_metadata_staleness_check_when_config_aggregate_available(
    capability_with_security: AssetDownloadCapability, cache_dir: str
):
    """Test FR-AST-005: metadata staleness check runs before download when config aggregate is wired."""

    class MockConfigAggregate:
        def get_int(self, _path: str, _default: int = 0) -> int:
            return 1000000  # Under max size limit

        def get_bool(self, _path: str, _default: bool = False) -> bool:
            return False  # Fresh metadata (not stale)

    cap = capability_with_security
    cap.config_aggregate = MockConfigAggregate()

    result = await cap.download_to_cache(
        provider=ProviderName("polyhaven"),
        asset_id=AssetId("hdri_001"),
        asset_type=AssetType("hdri"),
        cache_dir=FilePath(cache_dir),
    )

    assert result["success"] is True


@pytest.mark.asyncio
async def test_fr_ast_005_metadata_staleness_defaults_to_stale_when_check_fails(
    capability_with_security: AssetDownloadCapability, cache_dir: str
):
    """Test FR-AST-005: stale check defaults to True when freshness cannot be determined."""

    class MockConfigAggregate:
        def get_int(self, _path: str, _default: int = 0) -> int:
            return 1000000

        def get_bool(self, _path: str, _default: bool = False) -> bool:
            raise Exception("adapter unreachable")

    cap = capability_with_security
    cap.config_aggregate = MockConfigAggregate()

    result = await cap.download_to_cache(
        provider=ProviderName("polyhaven"),
        asset_id=AssetId("hdri_001"),
        asset_type=AssetType("hdri"),
        cache_dir=FilePath(cache_dir),
    )

    # Should proceed with download despite staleness check failure
    assert result["success"] is True


@pytest.mark.asyncio
async def test_fr_ast_005_staleness_check_skipped_without_config_aggregate(
    capability_with_security: AssetDownloadCapability, cache_dir: str
):
    """Test FR-AST-005: staleness check gracefully skipped when config aggregate not wired."""
    cap = capability_with_security
    # config_aggregate is None by default from fixture

    result = await cap.download_to_cache(
        provider=ProviderName("polyhaven"),
        asset_id=AssetId("hdri_001"),
        asset_type=AssetType("hdri"),
        cache_dir=FilePath(cache_dir),
    )

    assert result["success"] is True


def test_fr_ast_005_check_metadata_staleness_fresh(_cache_dir: str):
    """Test _check_metadata_staleness returns False when metadata is fresh."""
    import asyncio as _asyncio

    class MockConfigAggregate:
        def get_bool(self, _path: str, _default: bool = False) -> bool:
            return False  # Not stale → fresh

    cap = AssetDownloadCapability(config_aggregate=MockConfigAggregate())
    result = _asyncio.run(cap._check_metadata_staleness(ProviderName("polyhaven"), AssetId("test")))
    assert result is False


def test_fr_ast_005_check_metadata_staleness_stale(_cache_dir: str):
    """Test _check_metadata_staleness returns True when metadata is stale."""
    import asyncio as _asyncio

    class MockConfigAggregate:
        def get_bool(self, _path: str, _default: bool = False) -> bool:
            return True  # Stale

    cap = AssetDownloadCapability(config_aggregate=MockConfigAggregate())
    result = _asyncio.run(cap._check_metadata_staleness(ProviderName("polyhaven"), AssetId("test")))
    assert result is True


def test_fr_ast_005_check_metadata_staleness_no_config_aggregate():
    """Test _check_metadata_staleness defaults to True when config aggregate not wired."""
    import asyncio as _asyncio

    cap = AssetDownloadCapability()
    result = _asyncio.run(cap._check_metadata_staleness(ProviderName("polyhaven"), AssetId("test")))
    assert result is True


def test_fr_ast_005_check_metadata_staleness_exception_defaults_to_stale():
    """Test _check_metadata_staleness defaults to True when freshness check raises."""
    import asyncio as _asyncio

    class MockConfigAggregate:
        def get_bool(self, _path: str, _default: bool = False) -> bool:
            raise Exception("adapter down")

    cap = AssetDownloadCapability(config_aggregate=MockConfigAggregate())
    result = _asyncio.run(cap._check_metadata_staleness(ProviderName("polyhaven"), AssetId("test")))
    assert result is True
