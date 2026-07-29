File: `.agents/issues/issue-dispatcher-architect-2026-07-30-000000.md`

```markdown
# Issue: dispatcher — Architectural Review & Refactoring

## Summary
The `dispatcher` feature has a mostly correct AES skeleton: shared taxonomy VOs, shared contract protocols, capability implementations, an aggregate orchestrator, and a root container. However, the current implementation contains several architectural defects that must be addressed before the dispatcher can safely serve as the single routing and catalog authority. The most serious issues are unconfigured execution paths that can return fake success, weak contract signatures using `Any`/primitive containers instead of taxonomy VOs, implicit coupling between agent and capability error types, unsanitized exception messages that may leak sensitive information, and a parallel surface-schema subsystem that violates naming/role rules and appears orphaned from the actual entry/surface flow. These issues weaken FR-DSP-001/004/005/006 guarantees, reduce type safety, and create maintenance and security risk.

## Findings by Category

### Layer Boundaries
| # | Severity | Issue | Location (File:Line) | Recommendation |
|---|----------|-------|----------------------|----------------|
| 1 | 🔴 **CRITICAL** | `SyncDispatchExecutor` can return a successful envelope even when no real executor is wired. If `self._execute is None`, it returns `{"status": "dispatched"}` instead of executing the owning feature. This violates FR-DSP-004 routing integrity and can mislead CLI/MCP consumers into believing an action ran. | `modules/dispatcher/src/capabilities_sync_dispatch.py:dispatch_sync()` | Require a non-null action executor dependency, or return `execution_error` when unavailable. Do not synthesize success. Wire the real gateway/feature executor in the root container. |
| 2 | 🔴 **CRITICAL** | `BackgroundSubmitExecutor` creates a synthetic job ID with `uuid.uuid4()` when no `job_tracker` is wired. This bypasses the Job feature and violates FR-DSP-005 atomic submission through the job feature. | `modules/dispatcher/src/capabilities_background_submit.py:submit_background()` | Require a real job tracker implementation. If absent, return `execution_error` or fail construction. Never create fake task references in production code paths. |
| 3 | 🟡 **WARNING** | `DispatchRequestError` is defined inside a capabilities file but is implicitly consumed by the agent via duck typing (`getattr(e, "error_category", ...)`). This creates a hidden cross-layer contract not expressed in `shared` taxonomy/contract. | `modules/dispatcher/src/capabilities_request_validation.py:DispatchRequestError`, `modules/dispatcher/src/agent_dispatcher_orchestrator.py:execute_action()` | Move dispatcher error types and error-category constants into `modules/shared/src/dispatcher/taxonomy_dispatch_error.py` or a shared error/category VO. Agent should catch the shared explicit type. |
| 4 | 🟡 **WARNING** | Surface action schema files live inside the dispatcher feature and form a parallel schema system separate from `CatalogRegistrationExecutor`. FR-DSP-001 states dispatcher is the sole catalog owner. The current split creates two sources of truth for action parameters. | `modules/dispatcher/src/surface_action_registry.py`, `modules/dispatcher/src/surface_*_action.py` | Consolidate action schema definitions into the dispatcher catalog or shared taxonomy constants. If schemas are truly surface-facing, expose them through the canonical discovery/catalog flow, not a separate registry. |
| 5 | 🟡 **WARNING** | `root_dispatcher_container.py` wires capabilities together but does not wire an owning-feature executor or job tracker. The container therefore assembles an orchestrator that cannot fulfill FR-DSP-004/005 in a real deployment. | `modules/dispatcher/src/root_dispatcher_container.py:wire()` | Inject real dependencies from the application composition root: gateway/feature executor and job tracker. If dependencies are unavailable, fail fast during wiring. |

### Naming Convention
| # | Severity | Issue | Location (File:Line) | Recommendation |
|---|----------|-------|----------------------|----------------|
| 1 | 🟡 **WARNING** | `surface_action_registry.py` uses suffix `_registry`, which is not an allowed surface suffix under AES102. Allowed surface suffixes include `_command`, `_controller`, `_page`, `_view`, `_component`, `_router`, `_layout`, `_hook`, `_store`, `_action`, `_screen`. | `modules/dispatcher/src/surface_action_registry.py` | Rename to an allowed surface role such as `surface_action_store.py` if it is a utility surface, or remove/relocate if it is not actually a surface. |
| 2 | 🟢 **INFO** | Capability file names omit the concrete role suffix used by their classes. Files are named `capabilities_action_discovery.py`, but classes are `ActionDiscoveryExecutor`. This is not necessarily an AES violation if capability suffix policy is flexible, but it reduces naming consistency. | `modules/dispatcher/src/capabilities_action_discovery.py`, `capabilities_background_submit.py`, etc. | Consider renaming to `capabilities_action_discovery_executor.py`, `capabilities_background_submit_executor.py`, etc., or update class names to match file roles consistently. |
| 3 | 🟢 **INFO** | String-backed domain flags such as `detail_level`, `timeout_class`, `risk_level`, and `execution_mode` are raw strings across contracts, capabilities, and VOs. | `modules/shared/src/dispatcher/contract_action_discovery_protocol.py`, `taxonomy_action_metadata_vo.py`, `taxonomy_action_command_vo.py` | Introduce taxonomy constants or enum-like constant modules, e.g. `taxonomy_dispatch_constant.py`, with values such as `RISK_LEVEL_LOW`, `TIMEOUT_CLASS_DEFAULT`, `DETAIL_LEVEL_STANDARD`. |

### Dead Code / Orphan
| # | Severity | Issue | Location (File:Line) | Recommendation |
|---|----------|-------|----------------------|----------------|
| 1 | 🟡 **WARNING** | The surface schema subsystem appears orphaned inside the dispatcher module. `surface_action_registry.py` imports the individual `surface_*_action.py` files, but no smart surface, CLI entry, MCP entry, or root entry in the provided module scope imports `surface_action_registry`. This risks AES506 surface orphan violations. | `modules/dispatcher/src/surface_action_registry.py`, `modules/dispatcher/src/surface_asset_action.py`, etc. | Either wire the registry into the actual CLI/MCP smart surface flow, export it through the package API, or remove/relocate it. If schemas belong to dispatcher catalog, move them into catalog registration/taxonomy. |
| 2 | 🟢 **INFO** | No-op idempotency block: `idempotent` is read, then `if not idempotent: pass`. This adds noise and does not enforce behavior. | `modules/dispatcher/src/capabilities_sync_dispatch.py:dispatch_sync()` | Remove the no-op block. If retry policy is needed, implement it explicitly in the appropriate layer; otherwise document that dispatcher never retries. |
| 3 | 🟢 **INFO** | `CatalogRegistrationExecutor.get_catalog()` and `get_action()` are not used by the provided dispatcher wiring. They may be useful for tests or future surfaces, but currently they are not part of the protocol or container flow. | `modules/dispatcher/src/capabilities_catalog_registration.py:get_catalog(), get_action()` | Keep only if consumed by tests or an upcoming surface; otherwise remove or expose through a protocol if they are required behavior. |

### Scalability & Coupling
| # | Severity | Issue | Location (File:Line) | Recommendation |
|---|----------|-------|----------------------|----------------|
| 1 | 🟡 **WARNING** | `DispatcherOrchestrator` accepts all six protocol dependencies as optional `None` values. This permits constructing an invalid aggregate that fails only at runtime per method. | `modules/dispatcher/src/agent_dispatcher_orchestrator.py:__init__()` | Make required dependencies mandatory constructor arguments. Use optional dependencies only for genuinely optional capabilities, and represent absence explicitly via protocol/feature flags. |
| 2 | 🟡 **WARNING** | `SyncDispatchExecutor` creates a `ThreadPoolExecutor` internally but the root container never disposes it. The class supports context-manager cleanup, but the container does not use it. | `modules/dispatcher/src/capabilities_sync_dispatch.py:__init__()`, `root_dispatcher_container.py:wire()` | Manage executor lifecycle explicitly. Either use the context manager at application shutdown, inject a shared executor, or avoid internal thread pools unless lifecycle is handled. |
| 3 | 🟡 **WARNING** | `BackgroundSubmitExecutor._get_active_job_count()` probes multiple arbitrary method names on an untyped `job_tracker`. This is fragile and hides the real contract. | `modules/dispatcher/src/capabilities_background_submit.py:_get_active_job_count()` | Define an explicit shared protocol, e.g. `JobTrackerProtocol`, with a stable method such as `active_job_count()`. Inject that protocol instead of duck-typing. |
| 4 | 🟡 **WARNING** | `CatalogRegistrationExecutor.register_action()` duplicates enriched `ActionMetadataVO` construction for duplicate and new registrations. This increases maintenance cost and risks divergence. | `modules/dispatcher/src/capabilities_catalog_registration.py:register_action()` | Extract a private factory/helper such as `_enrich_with_version(metadata)` or add a `with_catalog_version()` method to `ActionMetadataVO`. |
| 5 | 🟢 **INFO** | `ResultNormalizationExecutor._sanitize_data()` and `_sanitize_dict()` do not consistently propagate depth through list recursion. A deeply nested list/dict alternation can reset depth tracking. | `modules/dispatcher/src/capabilities_result_normalization.py:_sanitize_data(), _sanitize_dict()` | Pass depth through all recursive paths or use an iterative sanitizer with an explicit stack and global depth limit. |

### Data Flow
| # | Severity | Issue | Location (File:Line) | Recommendation |
|---|----------|-------|----------------------|----------------|
| 1 | 🔴 **CRITICAL** | Aggregate and protocol contracts use `Any`, `dict[str, Any]`, and raw `str` values in domain-facing signatures. Examples: `register_action(metadata: Any) -> Any`, `execute_action(action_name: str, parameters: dict[str, Any])`, `normalize_result(raw_outcome: dict[str, Any], tracking_id: str, is_background: bool)`. This violates AES402/AES405 intent and bypasses taxonomy VOs. | `modules/shared/src/dispatcher/contract_dispatcher_aggregate.py`, `modules/dispatcher/src/agent_dispatcher_orchestrator.py`, `modules/shared/src/dispatcher/contract_result_normalization_protocol.py` | Replace primitives with shared VOs: `ActionMetadataVO`, `ActionCommandVO`, `DiscoveryFilterVO`, `RawOutcomeVO`. Avoid `Any` in agent/contract signatures. |
| 2 | 🔴 **CRITICAL** | Exception messages are placed directly into result envelopes without sanitization. Examples: `f"Action '{action_name}' failed: {e}"`, `f"Job creation failed: {e}"`, and `safe_error_envelope(str(e))`. Exception text may contain paths, secrets, stack-derived strings, or provider details, conflicting with FR-DSP-006. | `modules/dispatcher/src/capabilities_sync_dispatch.py:dispatch_sync()`, `capabilities_background_submit.py:submit_background()`, `agent_dispatcher_orchestrator.py:execute_action()` | Sanitize/redact exception messages before envelope construction. Return safe user-facing messages plus error category; keep detailed diagnostics in logs only. |
| 3 | 🟡 **WARNING** | `SyncDispatchExecutor._map_error_category()` can return `connection_error`, but the FRD error-category list does not include `connection_error`. This creates inconsistent error taxonomy between implementation and specification. | `modules/dispatcher/src/capabilities_sync_dispatch.py:_map_error_category()` | Either add `connection_error` to the FRD/taxonomy error categories or map connection failures to `execution_error` with metadata. Define error categories as taxonomy constants. |
| 4 | 🟡 **WARNING** | Discovery filters are raw strings and detail level is a raw string. This allows invalid values to flow until late validation and weakens contract expressiveness. | `modules/shared/src/dispatcher/contract_action_discovery_protocol.py:discover_actions()` | Introduce `DiscoveryFilterVO` and detail-level constants. Validate at VO construction where possible. |

## Violations
- **AES102 — Suffix/Prefix Rules**: `surface_action_registry.py` uses forbidden/unsupported surface suffix `_registry`.
- **AES303 — Mandatory Definition**: `surface_asset_action.py`, `surface_config_action.py`, `surface_job_action.py`, `surface_launcher_action.py`, `surface_object_action.py`, `surface_render_action.py`, and `surface_scene_action.py` contain only dictionary constants and no class/definition, while not using the `_constant` exception naming.
- **AES402 — Contract Role**: contract methods use primitive/generic values such as `Any`, `str`, and `dict[str, Any]` instead of taxonomy VOs.
- **AES405 — Agent Role**: agent code uses `Any` annotations and weakly typed parameters in aggregate-facing methods.
- **AES406 — Surface Role**: surface files contain schema data and validation logic without clear smart/utility/passive surface wiring; `surface_action_registry.py` performs validation behavior that likely belongs in capabilities or utility, depending on final placement.
- **AES506 — Surface Orphan**: surface schema files are not demonstrably imported by a smart surface, entry, or exported package API within the provided dispatcher scope.
- **AES305 — Duplication Code**: duplicate enriched `ActionMetadataVO` construction in `CatalogRegistrationExecutor.register_action()`.
- **Potential FRD violation**: FR-DSP-001/004/005 are weakened by the parallel surface-schema system, unconfigured sync executor fallback, and synthetic background job fallback.

## Action Items (For Developer)
- [ ] P0 Remove fake success path from `SyncDispatchExecutor`; require a real executor or return `execution_error`.
- [ ] P0 Remove synthetic background job fallback from `BackgroundSubmitExecutor`; require a real job tracker or return `execution_error`.
- [ ] P0 Replace `Any` and primitive contract/agent signatures with shared taxonomy VOs.
- [ ] P0 Sanitize/redact all exception-derived messages before placing them in `UnifiedResultEnvelopeVO`.
- [ ] P1 Move `DispatchRequestError` and error-category constants into shared taxonomy; update agent to catch the explicit shared error type.
- [ ] P1 Resolve surface schema subsystem: remove, relocate to shared taxonomy constants, or unify with catalog registration.
- [ ] P1 Rename or remove `surface_action_registry.py` to satisfy AES102 and AES406.
- [ ] P1 Make `DispatcherOrchestrator` dependencies required, or explicitly model optional capabilities.
- [ ] P2 Define explicit `JobTrackerProtocol` and `ActionExecutorProtocol` in shared contracts instead of duck-typing.
- [ ] P2 Manage `ThreadPoolExecutor` lifecycle in root/container or inject a shared executor.
- [ ] P2 Extract duplicated `ActionMetadataVO` enrichment logic in catalog registration.
- [ ] P2 Add taxonomy constants for `risk_level`, `timeout_class`, `detail_level`, `execution_mode`, and `error_category`.

## Proposed Fixes / Reference Code

### 1. New shared taxonomy: `taxonomy_dispatch_error.py`

```python
"""Dispatcher domain errors and error categories.

Taxonomy layer:
  - Stable error categories from FRD.
  - Explicit error type consumed by agent and capabilities.
"""

from __future__ import annotations


class DispatchErrorCategory:
    """FRD-aligned dispatcher error categories."""

    VALIDATION = "validation_error"
    NOT_FOUND = "not_found_error"
    EXECUTION = "execution_error"
    CAPACITY = "capacity_error"
    UNSUPPORTED = "unsupported_error"
    TIMEOUT = "timeout_error"
    CONFIRMATION = "confirmation_error"
    REGISTRATION = "registration_error"


class DispatchError(Exception):
    """Domain error carrying a stable dispatcher error category."""

    def __init__(
        self,
        message: str,
        error_category: str = DispatchErrorCategory.EXECUTION,
        field_name: str | None = None,
    ) -> None:
        super().__init__(message)
        self.error_category = error_category
        self.field_name = field_name
```

### 2. New shared taxonomy: `taxonomy_discovery_filter_vo.py`

```python
"""Discovery filter Value Object."""

from __future__ import annotations

from dataclasses import dataclass


class DiscoveryDetailLevel:
    STANDARD = "standard"
    FULL = "full"


@dataclass(frozen=True)
class DiscoveryFilterVO:
    """Filter criteria for action discovery."""

    name_filter: str | None = None
    capability_filter: str | None = None
    detail_level: str = DiscoveryDetailLevel.STANDARD

    def __post_init__(self) -> None:
        if self.detail_level not in (
            DiscoveryDetailLevel.STANDARD,
            DiscoveryDetailLevel.FULL,
        ):
            raise ValueError(f"Unsupported detail level: {self.detail_level}")
```

### 3. New shared taxonomy: `taxonomy_raw_outcome_vo.py`

```python
"""Raw outcome Value Object for normalization input."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class RawOutcomeVO:
    """Raw result produced by sync dispatch or background submission.

    This VO replaces raw dict[str, Any] in normalization contracts.
    """

    success: bool
    message: str
    tracking_id: str
    is_background: bool = False
    data: dict[str, Any] | None = None
    error_category: str | None = None
    warnings: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)
```

### 4. Update: `contract_dispatcher_aggregate.py`

```python
from __future__ import annotations

from abc import ABC, abstractmethod

from .taxonomy_action_command_vo import ActionCommandVO
from .taxonomy_action_metadata_vo import ActionMetadataVO
from .taxonomy_discovery_filter_vo import DiscoveryFilterVO
from .taxonomy_discovery_outcome_vo import DiscoveryOutcomeVO
from .taxonomy_raw_outcome_vo import RawOutcomeVO
from .taxonomy_unified_result_envelope_vo import UnifiedResultEnvelopeVO


class IDispatcherAggregate(ABC):
    @abstractmethod
    def register_action(self, metadata: ActionMetadataVO) -> ActionMetadataVO: ...

    @abstractmethod
    def discover_actions(self, filter_criteria: DiscoveryFilterVO) -> DiscoveryOutcomeVO: ...

    @abstractmethod
    def validate_request(self, request: ActionCommandVO) -> ActionCommandVO: ...

    @abstractmethod
    def dispatch_sync(self, request: ActionCommandVO) -> UnifiedResultEnvelopeVO: ...

    @abstractmethod
    def submit_background(self, request: ActionCommandVO) -> UnifiedResultEnvelopeVO: ...

    @abstractmethod
    def normalize_result(self, raw_outcome: RawOutcomeVO) -> UnifiedResultEnvelopeVO: ...

    @abstractmethod
    def execute_action(self, request: ActionCommandVO) -> UnifiedResultEnvelopeVO: ...
```

### 5. Update: `agent_dispatcher_orchestrator.py`

```python
from modules.shared.src.dispatcher.taxonomy_action_command_vo import ActionCommandVO
from modules.shared.src.dispatcher.taxonomy_action_metadata_vo import ActionMetadataVO
from modules.shared.src.dispatcher.taxonomy_discovery_filter_vo import DiscoveryFilterVO
from modules.shared.src.dispatcher.taxonomy_dispatch_error import (
    DispatchError,
    DispatchErrorCategory,
)
from modules.shared.src.dispatcher.taxonomy_raw_outcome_vo import RawOutcomeVO


class DispatcherOrchestrator(IDispatcherAggregate):
    def __init__(
        self,
        catalog_registration: CatalogRegistrationProtocol,
        action_discovery: ActionDiscoveryProtocol,
        request_validation: RequestValidationProtocol,
        sync_dispatch: SyncDispatchProtocol,
        background_submit: BackgroundSubmitProtocol,
        result_normalization: ResultNormalizationProtocol,
    ) -> None:
        self._catalog_reg = catalog_registration
        self._discovery = action_discovery
        self._validation = request_validation
        self._dispatch = sync_dispatch
        self._bg_submit = background_submit
        self._normalization = result_normalization

    def register_action(self, metadata: ActionMetadataVO) -> ActionMetadataVO:
        return self._catalog_reg.register_action(metadata)

    def discover_actions(self, filter_criteria: DiscoveryFilterVO) -> DiscoveryOutcomeVO:
        return self._discovery.discover_actions(filter_criteria)

    def normalize_result(self, raw_outcome: RawOutcomeVO) -> UnifiedResultEnvelopeVO:
        return self._normalization.normalize_result(raw_outcome)

    def execute_action(self, request: ActionCommandVO) -> UnifiedResultEnvelopeVO:
        try:
            validated = self.validate_request(request)

            if validated.resolved_metadata.get("background_eligibility_flag", False):
                return self.submit_background(validated)

            return self.dispatch_sync(validated)

        except DispatchError as e:
            logger.error("Dispatch rejected: %s", e)
            return UnifiedResultEnvelopeVO.error_envelope(
                message=self._safe_message(e),
                tracking_id=request.validated_tracking_id,
                error_category=e.error_category,
            )

        except Exception as e:
            logger.exception("Unexpected dispatch failure")
            return UnifiedResultEnvelopeVO.error_envelope(
                message="Action execution failed unexpectedly",
                tracking_id=request.validated_tracking_id,
                error_category=DispatchErrorCategory.EXECUTION,
            )

    @staticmethod
    def _safe_message(error: Exception) -> str:
        # Do not return raw exception text to consumers.
        # Keep detailed diagnostics in logs only.
        return "Action request could not be processed"
```

### 6. Update: `capabilities_request_validation.py`

```python
from modules.shared.src.dispatcher.taxonomy_dispatch_error import (
    DispatchError,
    DispatchErrorCategory,
)


class RequestValidationExecutor(RequestValidationProtocol):
    def validate_request(self, request: ActionCommandVO) -> ActionCommandVO:
        metadata = self._catalog.get(request.action_name)
        if metadata is None:
            raise DispatchError(
                f"Unknown action: {request.action_name}",
                DispatchErrorCategory.NOT_FOUND,
            )

        # Example field validation replacement:
        # raise DispatchError(
        #     f"Missing required parameter: {field_name}",
        #     DispatchErrorCategory.VALIDATION,
        #     field_name=field_name,
        # )
```

### 7. Update: `capabilities_sync_dispatch.py`

```python
class SyncDispatchExecutor(SyncDispatchProtocol):
    def __init__(self, execute_action: Any) -> None:
        if execute_action is None:
            raise ValueError("SyncDispatchExecutor requires an action executor")

        self._execute = execute_action
        self._pool = ThreadPoolExecutor(max_workers=1)

    def dispatch_sync(self, request: ActionCommandVO) -> UnifiedResultEnvelopeVO:
        tracking_id = request.validated_tracking_id or request.tracking_id or ""

        try:
            # Remove fake fallback. Always execute through wired owning feature/gateway.
            result = self._execute.execute_action(
                request.action_name,
                dict(request.parameters),
            )

            return UnifiedResultEnvelopeVO.success_envelope(
                message=f"Action {request.action_name} dispatched successfully",
                tracking_id=tracking_id,
                data=result if isinstance(result, dict) else {"result": "completed"},
            )

        except Exception:
            logger.exception("Dispatch failed")
            return UnifiedResultEnvelopeVO.error_envelope(
                message="Action execution failed",
                tracking_id=tracking_id,
                error_category="execution_error",
            )
```

### 8. Update: `capabilities_background_submit.py`

```python
class BackgroundSubmitExecutor(BackgroundSubmitProtocol):
    def __init__(
        self,
        job_tracker: Any,
        background_capacity: int = 50,
        max_result_data_size: int = 1_000_000,
    ) -> None:
        if job_tracker is None:
            raise ValueError("BackgroundSubmitExecutor requires a job tracker")

        self._job_tracker = job_tracker
        self._capacity = background_capacity
        self._max_data_size = max_result_data_size

    def submit_background(self, request: ActionCommandVO) -> UnifiedResultEnvelopeVO:
        tracking_id = request.validated_tracking_id or request.tracking_id or ""

        try:
            job_id, status = self._job_tracker.track_new_task(
                operation_type=request.action_name,
                metadata={"tracking_id": tracking_id},
            )
        except Exception:
            logger.exception("Job creation failed")
            return UnifiedResultEnvelopeVO.error_envelope(
                message="Background job submission failed",
                tracking_id=tracking_id,
                error_category="execution_error",
            )

        return UnifiedResultEnvelopeVO.success_envelope(
            message=f"Background job submitted for action '{request.action_name}'",
            tracking_id=tracking_id,
            data={"task_reference": job_id},
            metadata={
                "action_name": request.action_name,
                "task_reference": job_id,
                "initial_job_state": status.get("status") if isinstance(status, dict) else str(status),
                "polling_required": True,
            },
            warnings=["Polling required for final outcome"],
        )
```

### 9. Update: `root_dispatcher_container.py`

```python
class DispatcherContainer:
    def __init__(
        self,
        action_executor: Any,
        job_tracker: Any,
    ) -> None:
        self._action_executor = action_executor
        self._job_tracker = job_tracker
        self._orchestrator: DispatcherOrchestrator | None = None
        self._wired: bool = False

    def wire(self) -> None:
        if self._wired:
            return

        catalog: dict = {}

        catalog_registration = CatalogRegistrationExecutor(catalog)
        action_discovery = ActionDiscoveryExecutor(catalog)
        request_validation = RequestValidationExecutor(catalog)
        sync_dispatch = SyncDispatchExecutor(self._action_executor)
        background_submit = BackgroundSubmitExecutor(self._job_tracker)
        result_normalization = ResultNormalizationExecutor()

        self._orchestrator = DispatcherOrchestrator(
            catalog_registration=catalog_registration,
            action_discovery=action_discovery,
            request_validation=request_validation,
            sync_dispatch=sync_dispatch,
            background_submit=background_submit,
            result_normalization=result_normalization,
        )

        self._wired = True
```

### 10. Surface schema subsystem remediation

Preferred direction:

1. Remove `surface_action_registry.py` and `surface_*_action.py` from `modules/dispatcher/src/`.
2. Move canonical action schema definitions into shared taxonomy constants or into catalog registration seed data.
3. Ensure `CatalogRegistrationExecutor` remains the sole owner of action metadata.
4. If CLI/MCP need schema discovery, consume `IDispatcherAggregate.discover_actions()` with a `DiscoveryFilterVO`.

Temporary AES-compliant alternative if these files must remain surface-facing:

```text
modules/dispatcher/src/surface_action_store.py
modules/dispatcher/src/surface_asset_action_store.py
modules/dispatcher/src/surface_object_action_store.py
...
```

However, the temporary rename alone is not sufficient. The validation logic in `surface_action_registry.validate_action_args()` should be removed from surface and delegated to `RequestValidationExecutor` or a shared utility/capability depending on final schema ownership.

```

```
