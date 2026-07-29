File: `.agents/issues/issue-asset-architect-2026-07-30-000000.md`

```markdown
# Issue: asset — Architectural Review & Refactoring

## Summary

The `asset` feature has a broadly correct AES skeleton: capabilities implement protocol contracts, the agent implements an aggregate contract, root wires implementations, and the smart surface depends on the aggregate. However, the current implementation contains several critical contract/runtime mismatches and typed-boundary weaknesses that will cause immediate runtime failures or make the feature unsafe to extend. The most severe problems are: security path validation is called with the wrong contract shape, the root container passes an unsupported constructor argument, capabilities call config methods that do not exist on the configured protocol, contracts return untyped `dict[str, Any]` instead of taxonomy VOs, archive-extraction VOs are duplicated across asset/security domains, and the smart surface is orphaned. These findings violate or weaken AES rules around contract role boundaries, orphan detection, naming, duplication, and typed data flow. They should be resolved before the asset feature is considered stable for CLI/MCP integration.

## Findings by Category

### Layer Boundaries

| # | Severity | Issue | Location (File:Line) | Recommendation |
|---|----------|-------|----------------------|----------------|
| 1 | 🔴 CRITICAL | `AssetDownloadCapability` calls `security_validator.validate_path(cache_dir, "write")`, but `ValidatePathProtocol.validate_path` accepts a single `PathValidationVO` request object and returns a `PathValidationVO`. This is a contract mismatch and will fail at runtime. | `modules/asset/src/capabilities_asset_download.py:AssetDownloadCapability.download_to_cache` | Construct `PathValidationVO(target_path=str(cache_dir), access_mode=AccessMode.WRITE)` and inspect `allowed` / `denial_reason` from the returned VO. |
| 2 | 🔴 CRITICAL | `AssetExtractCapability` builds archive VOs from `modules/shared/src/asset/taxonomy_asset_vo.py`, but `ExtractArchiveProtocol.validate_extraction` is defined against security-domain archive VOs from `modules/shared/src/security/taxonomy_security_vo.py`. This creates a duplicated, structurally fragile contract boundary. | `modules/asset/src/capabilities_asset_extract.py:AssetExtractCapability.extract_archive` | Use the security-domain archive VOs directly, or move shared archive VOs into a common/security taxonomy module and import them. Remove duplicated asset-domain archive VOs. |
| 3 | 🔴 CRITICAL | `modules/shared/src/asset/__init__.py` imports `taxonomy_asset_constant`, but that module is not present in the provided source snapshot. If missing in the repository, this breaks package import. | `modules/shared/src/asset/__init__.py` | Add `taxonomy_asset_constant.py` with the imported constants, or remove the imports/exports if the constants are no longer required. |
| 4 | 🟡 WARNING | Provider search utilities (`utility_polyhaven_search.py`, `utility_sketchfab_search.py`) perform provider-specific I/O through a duck-typed `connection: object`. Utility layer may only depend on taxonomy, so the real contract dependency is hidden behind `object`. This weakens layer boundaries and type safety. | `modules/shared/src/asset/utility/utility_polyhaven_search.py`, `modules/shared/src/asset/utility/utility_sketchfab_search.py` | Move provider adapter behavior into capabilities, or split utilities into pure parsing/normalization functions and inject the provider connection into a capability. If utilities remain, they must stay stateless and domain-agnostic. |
| 5 | 🟡 WARNING | `AssetContainer` declares major dependencies as `object | None` instead of their contract protocols. Root may depend on all layers, but wiring should be typed through contracts to preserve dependency inversion. | `modules/asset/src/root_asset_container.py:AssetContainer.__init__` | Type dependencies as `ValidatePathProtocol | None`, `ExtractArchiveProtocol | None`, `JobSchedulerProtocol | None`, `ConfigGetterProtocol | None`, and `GatewayClientProtocol | None`. |
| 6 | 🟡 WARNING | `AssetOrchestrator` emits telemetry/events directly through a module-level logging helper. Agent should orchestrate through contracts, not embed diagnostics side effects. | `modules/asset/src/agent_asset_orchestrator.py:_emit_event` | Inject a diagnostics/telemetry protocol or move event emission into a dedicated capability/utility consumed via contract. Keep the agent focused on orchestration. |

### Naming Convention

| # | Severity | Issue | Location (File:Line) | Recommendation |
|---|----------|-------|----------------------|----------------|
| 1 | 🟡 WARNING | `contract_asset_provider_connection.py` uses suffix `_connection`, but contract-layer files must use strict suffixes `_protocol` or `_aggregate`. This violates AES102. | `modules/shared/src/asset/contract_asset_provider_connection.py` | Rename to `contract_asset_provider_connection_protocol.py` or `contract_asset_provider_protocol.py` depending on intent. Update imports. |
| 2 | 🟡 WARNING | `IAssetProviderConnection` does not follow the contract naming pattern `I<Name>Protocol` or `I<Name>Aggregate`. | `modules/shared/src/asset/contract_asset_provider_connection.py:IAssetProviderConnection` | Rename to `IAssetProviderConnectionProtocol` or `AssetProviderConnectionProtocol`. |
| 3 | 🟢 INFO | `capabilities_asset_search_handler.py` uses role suffix `_handler`, which is not in the recommended capability role vocabulary. Capabilities allow flexible roles, but the name could be more explicit. | `modules/asset/src/capabilities_asset_search_handler.py` | Consider a clearer capability role such as `capabilities_asset_search_aggregator.py`, `capabilities_asset_search_provider.py`, or `capabilities_asset_search_fetcher.py` if the role matches the responsibility. |
| 4 | 🟢 INFO | `surface_asset_search_command.py` contains class `AssetSearchSurface`. For smart-surface consistency, a command-style class name such as `AssetSearchCommand` may be clearer. | `modules/asset/src/surface_asset_search_command.py:AssetSearchSurface` | Rename class to `AssetSearchCommand` or keep only if project convention explicitly allows `*Surface` class names. |

### Dead Code / Orphan

| # | Severity | Issue | Location (File:Line) | Recommendation |
|---|----------|-------|----------------------|----------------|
| 1 | 🟡 WARNING | `surface_asset_search_command.py` is not exported from `modules/asset/src/__init__.py` and is not referenced by any visible entrypoint, router, or composition root. This is a smart-surface orphan risk under AES506. | `modules/asset/src/surface_asset_search_command.py` | Wire the surface into the MCP/CLI entrypoint or feature barrel, or remove it if unused. |
| 2 | 🟡 WARNING | `polyhaven_get_details` and `polyhaven_download` are defined but not consumed by the asset feature. | `modules/shared/src/asset/utility/utility_polyhaven_search.py:polyhaven_get_details`, `modules/shared/src/asset/utility/utility_polyhaven_search.py:polyhaven_download` | Remove unused functions, or wire them into the download/detail flow if they are required by FRD scope. |
| 3 | 🟡 WARNING | `sketchfab_get_details` and `sketchfab_download` are defined but not consumed by the asset feature. | `modules/shared/src/asset/utility/utility_sketchfab_search.py:sketchfab_get_details`, `modules/shared/src/asset/utility/utility_sketchfab_search.py:sketchfab_download` | Remove unused functions, or wire them into the download/detail flow if required. |
| 4 | 🟢 INFO | Several taxonomy VOs appear unused by the current asset flow: `ImportGlbVO`, `ExportModelVO`, `SearchResultVO`, and alias `AssetMetadataVO`. | `modules/shared/src/asset/taxonomy_asset_vo.py` | Remove unused VOs or adopt them as typed contract results. If they are public shared API, document the consumer. |
| 5 | 🟢 INFO | `root_asset_container.py` imports `DuplicatePolicy` at module scope and again inside `get_orchestrator`. The top-level import appears unused. | `modules/asset/src/root_asset_container.py` | Remove the unused top-level import or use it consistently and delete the inner import. |

### Scalability & Coupling

| # | Severity | Issue | Location (File:Line) | Recommendation |
|---|----------|-------|----------------------|----------------|
| 1 | 🟡 WARNING | Major asset contracts return `dict[str, Any]` instead of taxonomy VOs: search, download, extract, import, and provider capabilities. This weakens AES402 contract typing and pushes parsing burden into the agent. | `modules/shared/src/asset/contract_asset_search_protocol.py`, `modules/shared/src/asset/contract_asset_download_protocol.py`, `modules/shared/src/asset/contract_asset_extract_protocol.py`, `modules/shared/src/asset/contract_asset_import_protocol.py`, `modules/shared/src/asset/contract_asset_provider_protocol.py` | Replace dictionary returns with frozen taxonomy result VOs. Prefer request/response VOs over long primitive parameter lists. |
| 2 | 🟡 WARNING | `AssetDownloadCapability` mixes cache path generation, integrity verification, metadata staleness checks, download-size estimation, background-job submission, and mock file writing. This reduces single-responsibility clarity. | `modules/asset/src/capabilities_asset_download.py:AssetDownloadCapability` | Extract reusable technical mechanics into utility functions or separate capabilities: cache pathing, integrity verification, provider download adapter. Keep the download capability focused on protocol execution. |
| 3 | 🟡 WARNING | `AssetOrchestrator` maintains mutable workflow state in `_workflow_states` and mutates it outside the constructor. This creates hidden orchestration state and may not scale safely across concurrent requests. | `modules/asset/src/agent_asset_orchestrator.py:AssetOrchestrator._set_workflow_state` | Make the orchestrator stateless where possible. If workflow state is required, store it in a taxonomy VO and pass it explicitly, or delegate lifecycle/state tracking to the job feature. |
| 4 | 🟡 WARNING | Provider names `"Polyhaven"` and `"Sketchfab"` are hardcoded in `AssetSearchHandler` and utility functions. Adding a provider requires modifying dispatch logic. | `modules/asset/src/capabilities_asset_search_handler.py:AssetSearchHandler.search_all` | Introduce a provider registry or adapter mapping keyed by `ProviderName`. Each provider adapter should implement a common protocol. |
| 5 | 🟡 WARNING | `AssetImportCapability` hardcodes supported import formats inside `_is_supported_format`. This is configuration/constant data embedded in behavior code. | `modules/asset/src/capabilities_asset_import.py:AssetImportCapability._is_supported_format` | Move supported format mappings to `taxonomy_asset_constant.py` or configuration. Use constants/config to drive format validation. |

### Data Flow

| # | Severity | Issue | Location (File:Line) | Recommendation |
|---|----------|-------|----------------------|----------------|
| 1 | 🔴 CRITICAL | `AssetContainer.get_orchestrator` passes `overwrite_policy=overwrite_policy_vo` to `AssetDownloadCapability`, but the capability constructor does not accept `overwrite_policy`. This will raise `TypeError` when the container is used. | `modules/asset/src/root_asset_container.py:AssetContainer.get_orchestrator` | Either add `overwrite_policy` to `AssetDownloadCapability.__init__` or remove the argument from container wiring. Prefer storing default policy in configuration/request VO. |
| 2 | 🔴 CRITICAL | `AssetDownloadCapability` calls `config_getter.get_entrypoint()`, then `entrypoint.get_download_size(...)` and `entrypoint.is_metadata_fresh(...)`. `ConfigGetterProtocol` only defines `get(key, default)`. These calls are outside the contract and will fail at runtime. | `modules/asset/src/capabilities_asset_download.py:AssetDownloadCapability._estimate_download_size`, `modules/asset/src/capabilities_asset_download.py:AssetDownloadCapability._check_metadata_staleness` | Use only methods defined on injected contracts. If metadata freshness or download-size estimation is required, inject an appropriate provider/metadata protocol or extend the contract explicitly. |
| 3 | 🔴 CRITICAL | `AssetImportCapability.import_asset` calls `self.gateway_client.execute_command(...)` without checking whether `gateway_client` is `None`. The container can currently pass `None`. | `modules/asset/src/capabilities_asset_import.py:AssetImportCapability.import_asset` | Fail fast with a typed validation/configuration error when `gateway_client` is missing, or make the dependency non-optional. |
| 4 | 🟡 WARNING | `AssetOrchestrator.get_provider_metadata` calls `normalize_metadata({}, provider_name, asset_id)`. Normalizing an empty dictionary cannot produce meaningful provider metadata. The raw provider data source is missing. | `modules/asset/src/agent_asset_orchestrator.py:AssetOrchestrator.get_provider_metadata` | Retrieve raw provider metadata through a provider protocol before normalization, or change the operation to return provider capabilities only. |
| 5 | 🟡 WARNING | `polyhaven_search` ignores the `SearchQuery` payload. The command sends only `asset_type` and `categories`, so query text never reaches the provider. | `modules/shared/src/asset/utility/utility_polyhaven_search.py:polyhaven_search` | Include `"query": str(query)` or the provider-equivalent field in the command payload. |
| 6 | 🟡 WARNING | `AssetSearchHandler.search_all` warns about disabled providers but still queries them. FRD expects disabled providers to be excluded with a warning. | `modules/asset/src/capabilities_asset_search_handler.py:AssetSearchHandler.search_all` | Filter `target` providers against `enabled_providers` before creating search tasks. Emit a warning for excluded providers. |
| 7 | 🟡 WARNING | `AssetOrchestrator.search` constructs `AssetMetadata` using `cast(str, ...)` instead of branded taxonomy constructors. This weakens taxonomy typing. | `modules/asset/src/agent_asset_orchestrator.py:AssetOrchestrator.search` | Use `AssetId(...)`, `AssetName(...)`, `AssetType(...)`, and `ProviderName(...)` when constructing `AssetMetadata`. |
| 8 | 🟡 WARNING | Archive extraction defaults are inconsistent: `AssetExtractProtocol.extract_archive` defaults `max_extracted_size` to `1073741824` bytes, while `ArchiveExtractionOptionsVO` defaults `max_total_size` to `104_857_600` bytes. | `modules/shared/src/asset/contract_asset_extract_protocol.py`, `modules/shared/src/asset/taxonomy_asset_vo.py:ArchiveExtractionOptionsVO` | Align defaults through a shared taxonomy constant or VO default. Prefer one source of truth. |
| 9 | 🟡 WARNING | `AssetExtractCapability.extract_archive` does not enforce the documented download-before-extract precondition. The orchestrator comments mention workflow state but does not check it before extraction. | `modules/asset/src/agent_asset_orchestrator.py:AssetOrchestrator.extract_archive` | Enforce workflow preconditions explicitly using typed state, or remove the claim if extraction is allowed independently. |
| 10 | 🟢 INFO | `AssetDownloadCapability` mutates per-request state such as `self._cache_dir`, `self._max_size`, and `self._overwrite_policy` inside `download_to_cache`. This can create concurrency hazards on a shared capability instance. | `modules/asset/src/capabilities_asset_download.py:AssetDownloadCapability.download_to_cache` | Keep per-request data in local variables or request VOs. Store only stable configuration in capability state. |

## Violations

- **AES102 — Suffix/Prefix Rules**
  - `contract_asset_provider_connection.py` uses invalid contract suffix `_connection`.
  - Contract type `IAssetProviderConnection` does not follow `I<Name>Protocol` or `I<Name>Aggregate` naming.

- **AES203 — Unused Import**
  - `root_asset_container.py` has an unused top-level `DuplicatePolicy` import shadowed by an inner import.

- **AES305 — Duplication Code**
  - Archive extraction VOs are duplicated between asset taxonomy and security taxonomy:
    - `modules/shared/src/asset/taxonomy_asset_vo.py`
    - `modules/shared/src/security/taxonomy_security_vo.py`

- **AES402 — Contract Role**
  - Multiple contract methods use `dict[str, Any]`, `Any`, or primitive-heavy signatures instead of typed taxonomy VOs:
    - `AssetSearchProtocol.search_all`
    - `AssetDownloadProtocol.download_to_cache`
    - `AssetExtractProtocol.extract_archive`
    - `AssetImportProtocol.import_asset`
    - `AssetProviderProtocol.get_provider_capabilities`
    - `IAssetAggregate.get_provider_metadata`

- **AES405 — Agent Role**
  - `AssetOrchestrator` uses `Any` and `dict[str, Any]` in agent-facing methods.
  - `AssetOrchestrator` mutates workflow state outside the constructor.
  - Agent file contains a module-level helper `_emit_event`, which should be extracted or injected.

- **AES504 — Utility Orphan**
  - Unused utility functions:
    - `polyhaven_get_details`
    - `polyhaven_download`
    - `sketchfab_get_details`
    - `sketchfab_download`

- **AES506 — Surface Orphan**
  - `surface_asset_search_command.py` is not wired into any visible entrypoint, router, or feature export.

## Action Items (For Developer)

- [ ] **P0** Fix runtime contract mismatches in `AssetDownloadCapability` for security path validation.
- [ ] **P0** Fix `AssetContainer` wiring: remove or add support for `overwrite_policy` in `AssetDownloadCapability`.
- [ ] **P0** Remove calls to undefined `ConfigGetterProtocol` methods (`get_entrypoint`, `get_download_size`, `is_metadata_fresh`) or replace them with valid contracted dependencies.
- [ ] **P0** Guard or make non-optional `gateway_client` in `AssetImportCapability`.
- [ ] **P0** Rename `contract_asset_provider_connection.py` to a valid contract suffix and update all imports.
- [ ] **P1** Replace `dict[str, Any]` contract returns with frozen taxonomy result VOs.
- [ ] **P1** Remove duplicated archive VOs from asset taxonomy and use security/common archive VOs.
- [ ] **P1** Wire `AssetSearchSurface` into an entrypoint or remove the orphan surface.
- [ ] **P1** Remove unused provider utility functions or connect them to real FRD flows.
- [ ] **P1** Fix Polyhaven search so the `SearchQuery` is actually sent to the provider.
- [ ] **P1** Exclude disabled providers from search execution, not only from logging.
- [ ] **P2** Refactor provider search into adapter/registry pattern keyed by `ProviderName`.
- [ ] **P2** Move supported import formats and provider constants into taxonomy constants or configuration.
- [ ] **P2** Extract agent telemetry/event emission into a diagnostics or telemetry contract.
- [ ] **P2** Make `AssetOrchestrator` stateless or move workflow state into an explicit taxonomy/job-backed VO.

## Proposed Fixes / Reference Code

### 1. Rename provider connection contract

```python
# modules/shared/src/asset/contract_asset_provider_connection_protocol.py
from __future__ import annotations

from typing import Any, Protocol

from modules.shared.src.common.taxonomy_core_vo import ActionName


class IAssetProviderConnectionProtocol(Protocol):
    """Contract for sending commands to an external asset provider."""

    async def send_command(
        self,
        action: ActionName,
        payload: dict[str, Any],
    ) -> dict[str, Any]:
        """Send a provider command and return the raw result payload."""
        ...
```

Update imports:

```python
# modules/asset/src/capabilities_asset_search_handler.py
from modules.shared.src.asset.contract_asset_provider_connection_protocol import (
    IAssetProviderConnectionProtocol,
)


class AssetSearchHandler(AssetSearchProtocol):
    def __init__(
        self,
        connection: IAssetProviderConnectionProtocol,
        providers: list[str] | None = None,
        enabled_providers: list[str] | None = None,
    ) -> None: ...
```

---

### 2. Use typed security path validation in download capability

```python
# modules/asset/src/capabilities_asset_download.py
from modules.shared.src.security.taxonomy_security_vo import (
    AccessMode,
    PathValidationVO,
)

# Inside AssetDownloadCapability.download_to_cache:
if self.security_validator is not None:
    validation_request = PathValidationVO(
        target_path=str(cache_dir),
        access_mode=AccessMode.WRITE,
        operation_context="asset_download_cache",
    )
    validation = await self.security_validator.validate_path(validation_request)

    if not validation.allowed:
        return AssetDownloadCacheVO(
            provider=provider,
            asset_id=asset_id,
            asset_type=asset_type,
            cache_dir=cache_dir,
            resolution=resolution,
            overwrite_policy=overwrite_policy,
            max_size=max_size,
            success=False,
            file_path=None,
            file_size=0,
            cached=False,
            integrity_ok=False,
            message=validation.denial_reason or "Cache path validation failed",
        )
```

---

### 3. Fix container wiring for download capability

Option A — remove unsupported argument:

```python
# modules/asset/src/root_asset_container.py
download = AssetDownloadCapability(
    security_validator=self._security_validator,
    job_scheduler=self._job_scheduler,
    config_getter=self._config_getter,
)
```

Option B — explicitly support default overwrite policy in the capability:

```python
# modules/asset/src/capabilities_asset_download.py
class AssetDownloadCapability(AssetDownloadProtocol):
    def __init__(
        self,
        security_validator: ValidatePathProtocol | None = None,
        job_scheduler: JobSchedulerProtocol | None = None,
        config_getter: ConfigGetterProtocol | None = None,
        default_overwrite_policy: DuplicatePolicy = DuplicatePolicy("reuse"),
    ) -> None:
        self.security_validator = security_validator
        self.job_scheduler = job_scheduler
        self.config_getter = config_getter
        self._default_overwrite_policy = default_overwrite_policy
```

Then container wiring:

```python
# modules/asset/src/root_asset_container.py
download = AssetDownloadCapability(
    security_validator=self._security_validator,
    job_scheduler=self._job_scheduler,
    config_getter=self._config_getter,
    default_overwrite_policy=overwrite_policy_vo,
)
```

---

### 4. Type root dependencies with contracts

```python
# modules/asset/src/root_asset_container.py
from modules.shared.src.config.contract_config_protocol import ConfigGetterProtocol
from modules.shared.src.gateway.contract_gateway_client_protocol import GatewayClientProtocol
from modules.shared.src.job.contract_job_protocol import JobSchedulerProtocol
from modules.shared.src.security.contract_extract_archive_protocol import ExtractArchiveProtocol
from modules.shared.src.security.contract_validate_path_protocol import ValidatePathProtocol


class AssetContainer:
    def __init__(
        self,
        connection: IAssetProviderConnectionProtocol,
        security_validator: ValidatePathProtocol | None = None,
        security_supervisor: ExtractArchiveProtocol | None = None,
        job_scheduler: JobSchedulerProtocol | None = None,
        config_getter: ConfigGetterProtocol | None = None,
        gateway_client: GatewayClientProtocol | None = None,
    ) -> None: ...
```

---

### 5. Remove duplicated archive VOs and use security taxonomy

```python
# modules/asset/src/capabilities_asset_extract.py
from modules.shared.src.security.taxonomy_security_vo import (
    ArchiveEntryVO,
    ArchiveExtractionOptionsVO,
    ArchiveExtractionVO,
)
```

Then remove duplicated definitions from:

```text
modules/shared/src/asset/taxonomy_asset_vo.py
```

If asset callers still need archive types, re-export from security taxonomy through the shared asset barrel only if it does not create layer cycles.

---

### 6. Replace dictionary contract results with VOs

Example for download:

```python
# modules/shared/src/asset/contract_asset_download_protocol.py
from modules.shared.src.asset.taxonomy_asset_vo import AssetDownloadCacheVO


class AssetDownloadProtocol(ABC):
    @abstractmethod
    async def download_to_cache(
        self,
        request: AssetDownloadCacheVO,
    ) -> AssetDownloadCacheVO:
        """Download an asset into cache and return the typed result."""
        ...
```

Example for search:

```python
# modules/shared/src/asset/contract_asset_search_protocol.py
from modules.shared.src.asset.taxonomy_asset_vo import SearchResultVO
from modules.shared.src.common.taxonomy_core_vo import SearchQuery, StringList


class AssetSearchProtocol(ABC):
    @abstractmethod
    async def search_all(
        self,
        query: SearchQuery,
        providers: StringList | None = None,
    ) -> SearchResultVO:
        """Search enabled providers and return normalized typed results."""
        ...
```

Then update `AssetOrchestrator` to consume VOs directly instead of dictionary access.

---

### 7. Construct taxonomy VOs safely in the agent

```python
# modules/asset/src/agent_asset_orchestrator.py
from modules.shared.src.common.taxonomy_core_vo import (
    AssetId,
    AssetName,
    AssetType,
    ProviderName,
)

return [
    AssetMetadata(
        id=AssetId(str(a.get("id", ""))),
        name=AssetName(str(a.get("name", ""))),
        type=AssetType(str(a.get("type", ""))),
        provider=ProviderName(str(a.get("provider", ""))),
    )
    for a in assets
]
```

---

### 8. Fix Polyhaven search query propagation

```python
# modules/shared/src/asset/utility/utility_polyhaven_search.py
async def polyhaven_search(
    connection: object,
    query: SearchQuery,
    categories: list[str] | None = None,
) -> AssetSearchVO:
    result = await connection.send_command(
        ActionName("search_polyhaven_assets"),
        {
            "query": str(query),
            "asset_type": "all",
            "categories": categories or [],
        },
    )
    ...
```

---

### 9. Exclude disabled providers before search execution

```python
# modules/asset/src/capabilities_asset_search_handler.py
target = providers if providers is not None else self._providers

if self._enabled_providers is not None:
    disabled = [p for p in target if p not in self._enabled_providers]
    if disabled:
        logger.warning("Excluding disabled providers from search: %s", disabled)

    target = [p for p in target if p in self._enabled_providers]
```

---

### 10. Wire or remove orphan surface

If the surface is required:

```python
# modules/asset/src/__init__.py
from .surface_asset_search_command import AssetSearchSurface

__all__ = [
    "AssetOrchestrator",
    "AssetDownloadCapability",
    "AssetExtractCapability",
    "AssetImportCapability",
    "AssetProviderMetadataCapability",
    "AssetSearchHandler",
    "AssetContainer",
    "create_asset_container",
    "AssetSearchSurface",
]
```

Then consume it from the MCP/CLI entrypoint:

```python
# Example entrypoint wiring
surface = AssetSearchSurface(container.get_orchestrator())
results = await surface.search_assets(query_text)
```

If no entrypoint consumes it, delete:

```text
modules/asset/src/surface_asset_search_command.py
```

```

```
