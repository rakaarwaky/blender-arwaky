# Review Plan: dispatcher — Backend Developer

**Timestamp:** 2026-07-28T07:27:45
**Module:** modules/dispatcher (FR-DSP-001 … FR-DSP-006)
**Reviewer role:** Expert Backend Developer (Python)

## Summary

The dispatcher feature module is structurally sound in its AES layering (capabilities
import only taxonomy + contract; agent orchestrator wires capabilities through the
container; root container composes them). However, a **critical wiring defect** makes the
wired container non-functional, and several FRD-mandated behaviors are stubs or missing:
request validation is a near-no-op, background eligibility/capacity are not enforced, the
synchronous dispatch never enforces the action timeout, the result envelope never flags
truncation, and the shared catalog is not shared between registration, discovery, and
validation. This plan fixes the critical wiring bug and the FRD-justified behavioral gaps
without expanding scope beyond `modules/dispatcher/src/`.

## Findings by Category

### Architecture & Layer Compliance

| #   | Severity | Issue | Location | Recommendation |
| --- | -------- | ----- | -------- | -------------- |
| A1  | 🔴 CRITICAL | The container wires `ActionDiscoveryExecutor()` and `RequestValidationExecutor()` with the default empty `catalog` (`{}`), while `CatalogRegistrationExecutor()` keeps its **own** private `_catalog` dict. Registration therefore populates a different catalog than discovery/validation read → the wired module is completely non-functional (discovery always empty, validation always "Unknown action"). Violates FR-DSP-001 "Dispatcher is the only owner of the action catalog" and FR-DSP-002/003. | `root_dispatcher_container.py` (lines 43–48), `capabilities_catalog_registration.py` (`__init__` line 28) | Make `CatalogRegistrationExecutor` accept an injectable catalog dict; have the container create **one** shared catalog and inject it into registration, discovery, and validation executors. |
| A2  | 🟢 INFO | Agent `DispatcherOrchestrator` does not inherit an aggregate ABC (no `contract_*_aggregate.py` exists for dispatcher in shared). AES403 expects agent classes to inherit the aggregate ABC. Not fixable within module scope (requires shared-layer change). | `agent_orchestrator.py` (class decl) | Track as out-of-scope; add aggregate protocol in shared if/when the project adopts strict AES403 aggregate inheritance. |

### Security

| #   | Severity | Issue | Location | Recommendation |
| --- | -------- | ----- | -------- | -------------- |
| S1  | 🟢 INFO | `_sanitize_data` redacts any key containing `"code"` (e.g. `"color_code"`, `"decode"`), which can over-redact. FR-DSP-006 requires redacting raw code — acceptable but broad. | `capabilities_result_normalization.py` (line 100) | Keep; acceptable heuristic. No change this cycle. |

### Performance

| #   | Severity | Issue | Location | Recommendation |
| --- | -------- | ----- | -------- | -------------- |
| P1  | 🟡 WARNING | Synchronous dispatch never enforces the declared action timeout (`applied_timeout` is only recorded in metadata, never applied). Long-running/blocking calls can hang indefinitely. FR-DSP-004 "Dispatch must enforce action timeout" + QA "Action timeout enforced during dispatch". | `capabilities_sync_dispatch.py` (`dispatch_sync`, lines 47–71) | Run the injected `execute_action` callable under a real timeout (thread pool, `concurrent.futures`) bounded by `applied_timeout`; on timeout raise `TimeoutError` → mapped to `timeout_error`. |

### Error Handling

| #   | Severity | Issue | Location | Recommendation |
| --- | -------- | ----- | -------- | -------------- |
| E1  | 🟡 WARNING | `capabilities_request_validation.validate_request` only checks required-present and unknown-extra params. It omits FR-DSP-003-required checks: field **types**, numeric **ranges**, textual **length limits**, enumerated **allowed values**, payload **size limit**, **execution-mode compatibility** (background requires eligibility), **destructive confirmation** enforcement, and **timeout-override bounds**. | `capabilities_request_validation.py` (`_validate_parameters`, lines 77–89) | Implement full schema/parameter validation using the registered `parameter_schema` (properties with `type`, `minimum/maximum`, `minLength/maxLength`, `enum`), payload size limit, execution-mode compatibility, destructive-confirmation (enforced by default), and timeout-override bounds. Raise a `DispatchRequestError(ValueError)` carrying the correct FRD error category so the orchestrator can reflect `unsupported_error` / `confirmation_error` / `timeout_error`. |
| E2  | 🟡 WARNING | `unknown parameter policy` (strict/tolerant) is not implemented; extra params are always rejected. FR-DSP-003 allows tolerant ignore-with-warning. | `capabilities_request_validation.py` | Add `unknown_parameter_policy: str = "strict"` ctor arg; in tolerant mode record a `validation_warning` instead of raising. |
| E3  | 🟡 WARNING | `submit_background` never enforces background eligibility. FR-DSP-005 requires `unsupported_error` when the action lacks the background-eligibility flag. | `capabilities_background_submit.py` (`submit_background`, lines 43–104) | Check `request.resolved_metadata["background_eligibility_flag"]`; return `unsupported_error` envelope when ineligible. |
| E4  | 🟡 WARNING | Background capacity enforcement is a no-op: `_get_active_job_count` always returns `0` (even when a job tracker is wired). FR-DSP-005 "Background capacity limit must be enforced". | `capabilities_background_submit.py` (`_get_active_job_count`, lines 108–113) | Delegate to the wired job tracker when available (best-effort via documented method names); fall back to `0` only when no tracker is present, with a logged warning that capacity cannot be enforced. |
| E5  | 🟡 WARNING | Normalization never sets the `data_truncated` flag; oversized data is replaced but the envelope/meta lacks the truncation indicator required by FR-DSP-006 QA ("Oversized data truncated with truncation indicator"). | `capabilities_result_normalization.py` (lines 58–81) | When data exceeds `max_result_data_size`, build the envelope with `data_truncated=True` and add a `truncation` warning. |
| E6  | 🟡 WARNING | Catalog registration schema integrity check is a no-op (only logs a warning). FR-DSP-001 "Registration must validate schema integrity before acceptance" and QA "Invalid parameter schema rejected at registration". | `capabilities_catalog_registration.py` (`_validate_schema`, lines 96–111) | Reject malformed schemas with a clear error (non-dict, missing `properties`/`type`, `required` entries not declared in `properties`, property missing `type`). |

### Other (Typing / Business Logic)

| #   | Severity | Issue | Location | Recommendation |
| --- | -------- | ----- | -------- | -------------- |
| T1  | 🟡 WARNING | `any` (builtin function) is used as a type annotation instead of `Any`. Latent typing error; `dict[str, any]` resolves to `dict[str, <builtin any>]`. | `capabilities_action_discovery.py` (lines 28, 74), `capabilities_request_validation.py` (lines 30, 77) | Import `Any` from `typing` and use it. |
| T2  | 🟡 WARNING | Discovery `capability_filter` matches `risk_level` as if it were a capability, which is semantically wrong (risk level is metadata, not a capability/category). FR-DSP-002 capability filter should match the owning feature. | `capabilities_action_discovery.py` (`discover_actions`, lines 49–55) | Filter only on `owning_feature_ref` (and an explicit `category` if present); drop the `risk_level` match. |
| T3  | 🟢 INFO | `DispatcherOrchestrator.execute_action` returns the envelope produced by the leaf executors directly and never calls `normalize_result`. Leaf executors already build unified envelopes, so this is acceptable, but the aggregate's `normalize_result` is effectively unused by the main pipeline. | `agent_orchestrator.py` (`execute_action`) | Leave as-is (no regression); noted for awareness. |

## Violations

- **AES201 (Forbidden Import):** None. All capabilities import only `taxonomy_*` and `contract_*`; agent imports only taxonomy + contract; root imports only intra-module. Compliant.
- **AES203 (Unused Import):** None detected.
- **AES304 (Bypass Comment):** None (`unwrap`/`panic`/`noqa`/`type: ignore` absent).
- **AES403 (Agent aggregate inheritance):** `DispatcherOrchestrator` does not inherit an aggregate ABC — but no `contract_*_aggregate` exists for dispatcher in shared, so this is a project-wide gap, not fixable within module scope. Recorded as INFO A2.
- **AES405 (Agent Role):** Orchestrator coordinates ≥2 subsystems, contains no business computation, depends on contracts via DI. Compliant.
- No circular imports, no inter-capability dependencies, no domain-model definition in capabilities.

## Action Items

- [ ] **CRITICAL** A1 — Inject a single shared catalog into registration/discovery/validation (container + `CatalogRegistrationExecutor` ctor).
- [ ] E6 — Real schema-integrity validation in `CatalogRegistrationExecutor._validate_schema`.
- [ ] T1 — Replace `any` with `Any` in discovery + validation.
- [ ] T2 — Fix `capability_filter` to match owning feature only.
- [ ] E1/E2 — Full parameter + policy + mode/confirmation/timeout validation in `RequestValidationExecutor` with categorized `DispatchRequestError`.
- [ ] E3/E4 — Enforce background eligibility + real capacity check in `BackgroundSubmitExecutor`.
- [ ] P1 — Enforce action timeout in `SyncDispatchExecutor`.
- [ ] E5 — Set `data_truncated` indicator in `ResultNormalizationExecutor`.
- [ ] T3 — Leave orchestrator `execute_action` as-is (INFO).

## Fixed Code

The corrected code is applied directly to the files in `modules/dispatcher/src/` during the
Implement phase; key diffs are summarized in the execution report.
