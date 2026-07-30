
# Document 1: `.agents/issues/issue-dispatcher-business-analyst-2026-07-30-150000.md`

```markdown
# Issue: dispatcher — Business Logic & Requirements Review

## Summary
The dispatcher module implements 6 FRD requirements (FR-DSP-001 through FR-DSP-006) across 6 capabilities, 6 contracts, and 1 aggregate orchestrator. Critical gaps exist: the SyncDispatchExecutor is never wired in the container (making synchronous dispatch permanently broken at runtime), the orchestrator's `execute_action` facade overrides caller-specified execution mode, background submission lacks idempotency deduplication and observability events, and the sync dispatch capability does not route to the owning feature per catalog metadata as specified. Multiple FRD rules are partially implemented or silently skipped, creating data integrity and behavioral correctness risks for CLI/MCP consumers.

## Findings by Category

### Requirements Clarity
| # | Severity | Issue | Location (File:Line) | Recommendation |
|---|----------|-------|----------------------|----------------|
| 1 | 🟡 WARNING | FR-DSP-001 specifies "Immutable for consumers after registration phase" and "Hot re-registration configurable" but no phase-lock or config flag exists in code. The requirement is ambiguous: what triggers end of registration phase? | `modules/dispatcher/FRD.md`:FR-DSP-001 Rules | Define explicit registration phase boundary (e.g., container wire() completes registration; post-wire registrations require `catalog_hot_re_registration=True`). Add config key check in `register_action`. |
| 2 | 🟡 WARNING | FR-DSP-004 states "Read-only actions may flag to bypass serialization (final queue decision by gateway)" — unclear what "flag" means concretely. No field in ActionCommandVO or envelope carries this hint. | `modules/dispatcher/FRD.md`:FR-DSP-004 Rules | Add `read_only_hint: bool` to dispatch metadata passed to gateway, or document that this is gateway-internal and remove from dispatcher FRD scope. |
| 3 | 🟡 WARNING | FR-DSP-005 "Duplicate with idempotency hint may return existing task ref" — no definition of what constitutes an "idempotency hint" or how duplicates are detected (by action_name? by payload hash? by tracking_id?). | `modules/dispatcher/FRD.md`:FR-DSP-005 Rules | Define idempotency key composition (e.g., `action_name + hash(parameters)`) and storage mechanism for dedup lookup. |
| 4 | 🟢 INFO | FR-DSP-006 "field-level detail" in error envelope is specified but UnifiedResultEnvelopeVO has no `field_errors` field. Unclear if this is dispatcher responsibility or validation-layer responsibility. | `modules/dispatcher/FRD.md`:FR-DSP-006 Rules | Add optional `field_errors: dict[str, str]` to envelope VO, or clarify that field-level detail lives in `metadata` dict. |

### Business Flow
| # | Severity | Issue | Location (File:Line) | Recommendation |
|---|----------|-------|----------------------|----------------|
| 1 | 🔴 CRITICAL | `SyncDispatchExecutor` is never instantiated or wired in `DispatcherContainer.wire()`. The orchestrator's `dispatch_sync()` will always raise `RuntimeError("SyncDispatchProtocol not configured")`. Synchronous dispatch — the primary execution path — is completely broken. | `modules/dispatcher/src/root_dispatcher_container.py`:44-62 | Wire `SyncDispatchExecutor` in the container with an injected action executor. See Proposed Fixes. |
| 2 | 🔴 CRITICAL | `DispatcherOrchestrator.execute_action()` overrides caller's `execution_mode` by checking `bg_eligible or long_running` from resolved metadata. FR-DSP-003 validates execution mode compatibility, but the facade ignores the validated mode and makes its own routing decision. A caller requesting `sync` for a background-eligible action will be silently routed to background. | `modules/dispatcher/src/agent_dispatcher_orchestrator.py`:108-112 | Respect `request.execution_mode` as the primary routing signal. Use metadata flags only as fallback when mode is None. |
| 3 | 🟡 WARNING | FR-DSP-004 requires "Routing target = owning feature from catalog metadata" but `SyncDispatchExecutor` calls a single generic `self._execute.execute_action(action_name, params)` without resolving the owning feature. All actions route to the same executor regardless of `owning_feature_ref`. | `modules/dispatcher/src/capabilities_sync_dispatch.py`:72 | Implement a feature registry/router that resolves `owning_feature_ref` to the correct feature executor, or document that the injected executor is a gateway that handles internal routing. |
| 4 | 🟡 WARNING | FR-DSP-004 "Destructive → carries confirmation state" — the confirmation flag from the validated request is never passed to the executor. The owning feature cannot verify confirmation was obtained. | `modules/dispatcher/src/capabilities_sync_dispatch.py`:64-72 | Include `confirmation_flag` in the params or metadata passed to the executor. |
| 5 | 🟡 WARNING | FR-DSP-005 "Emits observability event" — `BackgroundSubmitExecutor` logs but never emits a structured lifecycle event. FR-DSP Events section specifies "background job submitted (task ref + action name)". | `modules/dispatcher/src/capabilities_background_submit.py`:entire file | Inject an event sink and emit a structured event on successful submission. |
| 6 | 🟡 WARNING | FR-DSP-004 "Partial results normalized with warning list" — no code path handles partial results from the executor. If the executor returns a result with warnings, they are lost. | `modules/dispatcher/src/capabilities_sync_dispatch.py`:74-82 | Check executor result for warnings/partial indicators and propagate to envelope. |

### Logic Implementation
| # | Severity | Issue | Location (File:Line) | Recommendation |
|---|----------|-------|----------------------|----------------|
| 1 | 🔴 CRITICAL | `BackgroundSubmitExecutor` uses `getattr(tracker, "create_task", None)` and `getattr(tracker, "track_new_task", None)` — runtime string-based method resolution bypasses type safety. If the job tracker interface changes, failure is silent until runtime. The `IJobLifecycle` contract defines `create_task` but the code also probes for a non-existent `track_new_task` method. | `modules/dispatcher/src/capabilities_background_submit.py`:68-88 | Type the `job_tracker` parameter as `IJobLifecycle` and call `create_task` directly. Remove the `track_new_task` fallback (not in the contract). |
| 2 | 🟡 WARNING | `RequestValidationExecutor` defines module-level constants (`DEFAULT_TIMEOUT`, `MAX_TIMEOUT_OVERRIDE`, `MAX_PAYLOAD_SIZE`, `DESTRUCTIVE_CONFIRMATION_ENFORCED`) directly in the capability file. AES405 prohibits magic constants in non-taxonomy layers. These should reference `taxonomy_dispatch_constant.py`. | `modules/dispatcher/src/capabilities_request_validation.py`:18-21 | Move constants to `taxonomy_dispatch_constant.py` and import them. |
| 3 | 🟡 WARNING | `SyncDispatchExecutor.__init__` accepts `execute_action: object` — untyped. The capability has no compile-time guarantee that the executor has an `execute_action` method. Violates AES402 spirit (concrete types in signatures). | `modules/dispatcher/src/capabilities_sync_dispatch.py`:38 | Define a `Protocol` class (e.g., `_ActionExecutor`) with `execute_action(action_name: str, params: dict) -> Any` and use it as the parameter type. |
| 4 | 🟡 WARNING | `ActionDiscoveryExecutor._format_action` accepts `metadata: Any` — loses all type safety. The catalog stores `ActionMetadataVO` but the discovery capability treats entries as untyped. | `modules/dispatcher/src/capabilities_action_discovery.py`:52 | Type the parameter as `ActionMetadataVO` and the catalog as `dict[str, ActionMetadataVO]`. |
| 5 | 🟡 WARNING | `CatalogRegistrationExecutor.register_action` duplicates the entire `ActionMetadataVO` construction for both duplicate-replacement and new-registration paths (lines 42-60 and 63-81 are identical except for the log message). DRY violation. | `modules/dispatcher/src/capabilities_catalog_registration.py`:42-81 | Extract a private `_enrich_and_store(metadata)` helper. |
| 6 | 🟢 INFO | `ResultNormalizationExecutor._sanitize_data` uses recursion for lists (`[self._sanitize_data(item) for item in data]`) but iterative depth-limited approach for dicts. Deeply nested lists can still cause stack overflow. | `modules/dispatcher/src/capabilities_result_normalization.py`:107 | Apply the same depth-limit pattern to list sanitization. |

### Testability & Acceptance Criteria
| # | Severity | Issue | Location (File:Line) | Recommendation |
|---|----------|-------|----------------------|----------------|
| 1 | 🟡 WARNING | FR-DSP-001 QA item "Degraded feature surfaced in discovery" — no code path ever sets `degraded=True` on `ActionMetadataVO`. The field exists but is dead. Cannot be tested because no trigger exists. | `modules/shared/src/dispatcher/taxonomy_action_metadata_vo.py`:37 | Define degradation trigger (e.g., health probe failure of owning feature) and implement the marking path, or remove the field and QA item. |
| 2 | 🟡 WARNING | FR-DSP-005 QA item "Duplicate with idempotency hint → existing task ref" — no dedup logic exists. This QA item is unverifiable. | `modules/dispatcher/src/capabilities_background_submit.py`:entire file | Implement idempotency key lookup before job creation, or mark this as P2/deferred in FRD. |
| 3 | 🟡 WARNING | FR-DSP-004 QA item "Non-idempotent not retried automatically" — trivially true because no retry logic exists at all. The acceptance criterion is vacuously satisfied and doesn't test the intended behavior (that a retry mechanism exists but skips non-idempotent actions). | `modules/dispatcher/FRD.md`:QA Checklist | Clarify: is retry planned? If yes, the test should verify retry skips non-idempotent. If no, reword QA item. |
| 4 | 🟢 INFO | No test files exist for the dispatcher module in the provided codebase. All 6 capabilities and the orchestrator lack unit/integration tests. | `modules/dispatcher/` | Create `tests/contract_dispatcher.py`, `tests/unit_dispatcher_*.py`, `tests/integration_dispatcher.py` per create-test-python skill. |

### Traceability (FRD → Code)
| # | Severity | Issue | Location (File:Line) | Recommendation |
|---|----------|-------|----------------------|----------------|
| 1 | 🔴 CRITICAL | FR-DSP-004 (Dispatch Synchronous Action) → `SyncDispatchExecutor` exists but is NEVER wired in the container. The FR is implemented in code but unreachable at runtime. Traceability breaks at the composition root. | `modules/dispatcher/src/root_dispatcher_container.py`:44-62 | Add SyncDispatchExecutor wiring. Verify with integration test that `dispatch_sync` returns an envelope. |
| 2 | 🟡 WARNING | FR-DSP Events section lists 6 events (action routed, completed, rejected, background submitted, catalog registered, action failed). No structured event emission exists in any capability. Only `logger.*` calls are present. | All capability files | Define an event sink protocol and inject into capabilities. Map each FRD event to a specific emission point. |
| 3 | 🟡 WARNING | FR-DSP Configuration Keys table lists 8 keys. Only `unknown_parameter_policy`, `destructive_confirmation_enforced`, `maximum_result_data_size`, and `background_capacity` are wired. Missing: `default_action_timeout`, `maximum_allowed_timeout`, `catalog_hot_re_registration`, `tracking_id_generation`. | `modules/dispatcher/src/root_dispatcher_container.py`:44-62 | Wire all config keys from the config feature into capability constructors. |
| 4 | 🟢 INFO | `taxonomy_dispatch_constant.py` defines error category constants but `capabilities_sync_dispatch.py` uses raw string literals (`"timeout_error"`, `"connection_error"`, etc.) in `_map_error_category`. Constants exist but are not consumed. | `modules/dispatcher/src/capabilities_sync_dispatch.py`:100-112 | Import and use constants from `taxonomy_dispatch_constant.py`. |

## Violations
- **AES405 (Agent Role)**: `capabilities_request_validation.py` defines module-level magic constants instead of importing from taxonomy constants.
- **AES402 (Contract Role)**: `SyncDispatchExecutor.__init__` uses `object` type for the executor parameter — no concrete protocol type.
- **AES201 (Forbidden Import)**: No violations detected.
- **AES403 (Capabilities Role)**: All capabilities implement their protocol ABC. Type count ≤ 3 per file. No violations.
- **AES503 (Capabilities Orphan)**: `SyncDispatchExecutor` is not wired in any container — effectively orphaned at runtime.

## Action Items (For Developer)
- [ ] P0: Wire `SyncDispatchExecutor` in `DispatcherContainer.wire()` with an injected action executor
- [ ] P0: Fix `execute_action` facade to respect `request.execution_mode` instead of overriding it
- [ ] P1: Type `SyncDispatchExecutor.execute_action` parameter as a Protocol instead of `object`
- [ ] P1: Type `ActionDiscoveryExecutor._format_action` parameter as `ActionMetadataVO` instead of `Any`
- [ ] P1: Remove `getattr`-based method resolution in `BackgroundSubmitExecutor`; use typed `IJobLifecycle` directly
- [ ] P1: Move validation constants from `capabilities_request_validation.py` to `taxonomy_dispatch_constant.py`
- [ ] P2: Implement structured event emission for all 6 FRD events
- [ ] P2: Implement idempotency dedup in background submission
- [ ] P2: Pass confirmation flag to executor in sync dispatch
- [ ] P2: Wire remaining config keys (default_action_timeout, maximum_allowed_timeout, catalog_hot_re_registration, tracking_id_generation)
- [ ] P3: Add depth-limit to list sanitization in ResultNormalizationExecutor
- [ ] P3: Deduplicate ActionMetadataVO construction in CatalogRegistrationExecutor

## Proposed Fixes / Reference Code

### File: `modules/dispatcher/src/root_dispatcher_container.py`

```python
def wire(self) -> None:
    """Wire the six dispatcher capabilities to the orchestrator."""
    if self._wired:
        return
    logger.info("Wiring dispatcher feature module")

    catalog: dict = {}
    catalog_registration = CatalogRegistrationExecutor(catalog)
    action_discovery = ActionDiscoveryExecutor(catalog)
    request_validation = RequestValidationExecutor(catalog)

    # FR-DSP-004: SyncDispatchExecutor MUST be wired for synchronous dispatch to work.
    # The action_executor is the gateway or feature router that executes actions.
    sync_dispatch = SyncDispatchExecutor(
        execute_action=self._action_executor,  # inject from container caller
    ) if self._action_executor else None

    background_submit = BackgroundSubmitExecutor(
        job_tracker=self._job_lifecycle,
    ) if self._job_lifecycle else None

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
    logger.info("Dispatcher feature module wired successfully")
```

### File: `modules/dispatcher/src/agent_dispatcher_orchestrator.py` (execute_action fix)

```python
def execute_action(self, request: ActionCommandVO) -> UnifiedResultEnvelopeVO:
    """Execute an action through the full dispatcher pipeline.

    Respects the caller's execution_mode. Falls back to metadata flags
    only when execution_mode is not explicitly set.
    """
    try:
        validated = self.validate_request(request)

        # Respect caller's explicit execution mode choice
        mode = validated.execution_mode
        if mode == "background":
            return self.submit_background(validated)
        if mode == "sync":
            return self.dispatch_sync(validated)

        # Fallback: infer from metadata when mode is unset
        bg_eligible = validated.resolved_metadata.get("background_eligibility_flag", False)
        long_running = validated.resolved_metadata.get("long_running_flag", False)
        if bg_eligible or long_running:
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
        logger.error("Unexpected dispatch failure: %s", e)
        return UnifiedResultEnvelopeVO.error_envelope(
            message="Action execution failed unexpectedly",
            tracking_id=request.validated_tracking_id,
            error_category=DispatchErrorCategory.EXECUTION,
        )
```

### File: `modules/dispatcher/src/capabilities_sync_dispatch.py` (typed executor)

```python
from typing import Protocol, runtime_checkable


@runtime_checkable
class ActionExecutorProtocol(Protocol):
    """Protocol for the action executor (gateway or feature router)."""

    def execute_action(self, action_name: str, params: dict[str, object]) -> object: ...


class SyncDispatchExecutor(SyncDispatchProtocol):
    def __init__(self, execute_action: ActionExecutorProtocol) -> None:
        if execute_action is None:
            raise ValueError(
                "SyncDispatchExecutor requires a non-null action executor. "
                "Ensure the owning feature executor is wired in the container."
            )
        self._execute = execute_action
        self._pool = ThreadPoolExecutor(max_workers=1)
```

### File: `modules/dispatcher/src/capabilities_background_submit.py` (typed job tracker)

```python
from modules.shared.src.job.contract_job_lifecycle_protocol import IJobLifecycle


class BackgroundSubmitExecutor(BackgroundSubmitProtocol):
    def __init__(
        self,
        job_tracker: IJobLifecycle,
        background_capacity: int = 50,
        max_result_data_size: int = 1_000_000,
    ) -> None:
        if job_tracker is None:
            raise ValueError(
                "BackgroundSubmitExecutor requires a job tracker. "
                "Ensure the job tracker service is wired in the container."
            )
        self._job_tracker = job_tracker
        self._capacity = background_capacity
        self._max_data_size = max_result_data_size

    # In submit_background, replace getattr block with:
    def _create_job(self, request: ActionCommandVO, tracking_id: str) -> tuple[str, str]:
        command = CreateTaskCommand(
            operation_type=OperationType(request.action_name),
            metadata=TaskMetadata({"tracking_id": tracking_id}),
        )
        snapshot = self._job_tracker.create_task(command)
        return str(snapshot.job_id), str(snapshot.state.value)
```

```

---
```
