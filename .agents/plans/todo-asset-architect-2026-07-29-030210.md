# Review Plan: asset — Architect (Phase 1)

## Summary

The asset feature module (`modules/asset/`) follows AES layered architecture with 5 capabilities, 1 agent orchestrator, 1 root container, and shared taxonomy/contract/utility files. The overall structure is sound — layer boundaries are respected, naming conventions are compliant, and no orphan or circular-import issues were found. The primary findings concern type-safety weaknesses in the agent orchestrator and search handler (use of `Any`), and TODO placeholder comments in the download capability that should be wired to real implementations or replaced with proper error handling.

## Findings by Category

### Layer Boundaries

| # | Severity | Issue | Location (File:Line) | Recommendation |
|---|----------|-------|----------------------|----------------|
| 1 | 🟡 WARNING | `capabilities_asset_download.py` uses `Any` for all three injected dependencies (`security_validator`, `job_scheduler`, `config_getter`) with no protocol/interface contract, making the dependency graph opaque and bypassing the contract layer's type safety. | `modules/asset/src/capabilities_asset_download.py:42-44` | Replace `Any` with protocol types from the contract or security/utility layers as appropriate. |
| 2 | 🟡 WARNING | `capabilities_asset_search_handler.py` uses `object` for its `connection` parameter, providing no type contract. | `modules/asset/src/capabilities_asset_search_handler.py:29` | Use a typed protocol or ABC for the connection dependency. |

### Naming Convention

| # | Severity | Issue | Location (File:Line) | Recommendation |
|---|----------|-------|----------------------|----------------|
| 3 | 🟢 INFO | `capabilities_asset_search_handler.py` uses `search_handler` as the role suffix. While not forbidden, the capabilities layer convention favors action-oriented suffixes (e.g., `searcher`, `finder`). | `modules/asset/src/capabilities_asset_search_handler.py:1` | Optional rename to `capabilities_asset_searcher.py` for consistency with capability naming patterns. |

### Dead Code / Orphan

| # | Severity | Issue | Location (File:Line) | Recommendation |
|---|----------|-------|----------------------|----------------|
| 4 | 🟢 INFO | `capabilities_asset_download.py` lines 130-132 contain redundant overwrite-policy logic: the `elif overwrite_policy == "unique"` branch and the subsequent `if not cached_path or ...` block overlap, making the second block partially dead when `overwrite_policy == "unique"` is already handled. | `modules/asset/src/capabilities_asset_download.py:130-135` | Consolidate the unique-variant path to eliminate the overlapping branch. |

### Scalability & Coupling

| # | Severity | Issue | Location (File:Line) | Recommendation |
|---|----------|-------|----------------------|----------------|
| 5 | 🟢 INFO | `capabilities_asset_extract.py` imports from the cross-feature security layer (`modules.shared.src.security.*`). While allowed per AES201 (capabilities may import contract protocol and taxonomy), this creates a direct coupling between asset extraction and security that bypasses the shared-contract abstraction. | `modules/asset/src/capabilities_asset_extract.py:27-34` | Ensure the security contract protocol is stable; consider an intermediate adapter in shared/contract if the security API evolves. |

### Data Flow

| # | Severity | Issue | Location (File:Line) | Recommendation |
|---|----------|-------|----------------------|----------------|
| (None — data flow is unidirectional bottom-up with no cycles detected) | | | | |

## Violations

- **AES405 (MEDIUM)**: `agent_asset_orchestrator.py` uses `Any` type annotations — `dict[str, Any]` return type on `get_provider_metadata()` (line 140) and `Any` in constructor dependency injection params (lines 39-43). Reduces compile-time type safety and conceals interfaces.
- **AES403 (LOW)**: `capabilities_asset_search_handler.py` uses bare `object` for its `connection` dependency (line 29), preventing static analysis of the wired protocol.
- **AES304 (INFO)**: `capabilities_asset_download.py` contains TODO placeholder comments at lines 219 and 227 that are bypass patterns per AES304. These should be either wired to real implementations or converted to explicit `NotImplementedError` / `raise NotImplementedError`.

## Action Items

- [ ] P1 Replace `Any` dependency types in `capabilities_asset_download.py` with protocol types from contract layer
- [ ] P1 Replace `dict[str, Any]` return type in `agent_asset_orchestrator.py:get_provider_metadata()` with a concrete VO type
- [ ] P2 Replace `object` connection type in `capabilities_asset_search_handler.py` with a typed protocol
- [ ] P2 Replace TODO placeholders in `capabilities_asset_download.py` with `NotImplementedError` or real wiring
- [ ] P3 Fix overlapping overwrite-policy branch in `capabilities_asset_download.py` lines 130-135

## Fixed Code

### `modules/asset/src/agent_asset_orchestrator.py` — Fix AES405: Replace `Any` return type

```python
# BEFORE (line 140):
async def get_provider_metadata(self, provider_name: ProviderName, asset_id: AssetId) -> dict[str, Any]:
    if self._metadata is None:
        raise ValidationError("Provider metadata capability not configured in container")
    return await self._metadata.normalize_metadata({}, provider_name, asset_id)

# AFTER:
async def get_provider_metadata(self, provider_name: ProviderName, asset_id: AssetId) -> dict[str, Any]:
    if self._metadata is None:
        raise ValidationError("Provider metadata capability not configured in container")
    return await self._metadata.normalize_metadata({}, provider_name, asset_id)
```

**Note**: `get_provider_metadata` returns a normalized metadata dict with keys `name`, `provider`, `id`, `type`, `categories`, `thumbnail_url`, `license_summary`, `download_available`, `attribution`, `extra_fields`, `normalized_at`. A concrete `ProviderMetadataVO` dataclass should be added to the taxonomy layer (`modules/shared/src/asset/taxonomy_asset_metadata_vo.py`) to replace `dict[str, Any]`. This requires adding the VO and updating all protocol/aggregate signatures — deferred as a taxonomy layer change.

### `modules/asset/src/capabilities_asset_search_handler.py` — Fix AES403: Replace `object` with typed protocol

```python
# BEFORE (line 29):
def __init__(self, connection: object, providers: list[str] | None = None) -> None:

# AFTER:
from modules.shared.src.asset.contract_asset_search_protocol import AssetSearchProtocol

def __init__(self, connection: AssetSearchProtocol, providers: list[str] | None = None) -> None:
```

**Note**: The connection parameter should be typed to the gateway protocol that provides `send_command` for provider adapters. The gateway's protocol class should be defined in the contract layer at `modules/shared/src/gateway/contract_gateway_protocol.py` (or equivalent). Until that protocol is finalized, use a `Protocol` runtime check:

```python
from typing import Protocol, runtime_checkable

@runtime_checkable
class GatewayTransport(Protocol):
    async def send_command(self, action: str, payload: dict[str, Any]) -> dict[str, Any]: ...
```

### `modules/asset/src/capabilities_asset_download.py` — Fix TODO placeholders (AES304)

```python
# BEFORE (lines 216-222):
async def _estimate_download_size(self, _provider: ProviderName, _asset_id: AssetId) -> int:
    """Estimate download size from provider metadata.

    TODO: Wire provider adapter and replace with real size query.
    Returns a conservative default (5 MB) when adapter not available.
    """
    return 5000000  # 5 MB default estimate

# AFTER:
async def _estimate_download_size(self, _provider: ProviderName, _asset_id: AssetId) -> int:
    """Estimate download size from provider metadata.

    Returns a conservative default (5 MB) when the size query adapter
    is not wired into the container.
    """
    raise NotImplementedError(
        "AssetDownloadCapability._estimate_download_size requires a wired "
        "provider adapter; configure via AssetContainer constructor."
    )
```

```python
# BEFORE (lines 224-230):
async def _submit_background_download(self, _provider: ProviderName, _asset_id: AssetId, _cache_path: str) -> str:
    """Submit download as background job.

    TODO: Wire job feature and replace with real task submission.
    Returns a synthetic task ref when job feature is not available.
    """
    return f"task-{_provider}-{_asset_id}"

# AFTER:
async def _submit_background_download(self, _provider: ProviderName, _asset_id: AssetId, _cache_path: str) -> str:
    """Submit download as background job.

    Raises NotImplementedError when the job scheduler is not configured
    in the container. Callers must ensure job_scheduler is provided.
    """
    if self.job_scheduler is None:
        raise NotImplementedError(
            "Background download requires a wired job_scheduler; "
            "configure via AssetContainer constructor."
        )
    return await self.job_scheduler.submit Download(
        provider=_provider, asset_id=_asset_id, cache_path=_cache_path
    )
```

### `modules/asset/src/capabilities_asset_download.py` — Fix overlapping overwrite-policy branch (AES403)

```python
# BEFORE (lines 130-135):
elif overwrite_policy == "unique":
    cached_path = self._get_unique_cache_path(cache_key)

# Create unique variant if needed
if not cached_path or (cached_path != self._get_cache_path(cache_key) and overwrite_policy == "unique"):
    cached_path = self._get_unique_cache_path(cache_key)

# AFTER:
elif overwrite_policy == "unique":
    cached_path = self._get_unique_cache_path(cache_key)

# No further branching needed — all overwrite policies are handled above
```

### `modules/asset/src/capabilities_asset_download.py` — Replace `Any` dependency types with protocols

```python
# BEFORE (lines 40-45):
def __init__(
    self,
    security_validator: Any | None = None,
    job_scheduler: Any | None = None,
    config_getter: Any | None = None,
) -> None:

# AFTER:
from modules.shared.src.security.contract_extract_archive_protocol import ExtractArchiveProtocol
from modules.shared.src.job.contract_job_protocol import JobSchedulerProtocol
from modules.shared.src.config.contract_config_protocol import ConfigGetterProtocol

def __init__(
    self,
    security_validator: ExtractArchiveProtocol | None = None,
    job_scheduler: JobSchedulerProtocol | None = None,
    config_getter: ConfigGetterProtocol | None = None,
) -> None:
```

**Note**: The concrete protocol imports above assume these contract files exist. If `ExtractArchiveProtocol`, `JobSchedulerProtocol`, or `ConfigGetterProtocol` do not yet exist at those paths, create them in the respective shared/contract directory first, then wire them through the container. This is a prerequisite step for the type-safety fix.
