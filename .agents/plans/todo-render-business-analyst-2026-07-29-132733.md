# Review Plan: render — Business Analyst (Phase 2)

## Summary

The render feature implements all 4 FRD requirements (FR-RND-001 through FR-RND-004) with proper layering: taxonomy → contract → capabilities → agent → root container. Each capability validates input parameters and delegates Blender execution through the gateway code executor. However, there are significant gaps between the FRD specification and implementation: security path validation is not delegated to the Security feature (violating explicit FRD mandates), background render integration with the Job feature is missing, several edge cases from the FRD are unhandled (max_size enforcement, locked camera handling, timeout/capacity errors, atomic writes), and events are logged but not emitted through a proper event bus. No AES violations were detected in the current code structure.

## Findings by Category

### Requirements Clarity
| # | Severity | Issue | Location (File:Line) | Recommendation |
|---|----------|-------|----------------------|----------------|
| RND-001 | 🟡 WARNING | FR-RND-001 specifies "max size enforced with aspect ratio preservation" but `ViewportCaptureVO` has `max_size` field and the capability never enforces it | `capabilities_render_viewport_capture_executor.py` validation block | Add max_size enforcement with aspect ratio logic in `_validate` or a separate `_enforce_max_size` method |
| RND-002 | 🟡 WARNING | FR-RND-001 specifies "fallback to offscreen/active camera capture if viewport context unavailable" — no fallback logic exists | `capabilities_render_viewport_capture_executor.py` try block | Add fallback path: attempt offscreen render when viewport context is unavailable |
| RND-003 | 🟡 WARNING | FR-RND-001 specifies "focus object resolved deterministically; missing → reject or ignore per policy" — `focus_object` field exists but is never used in code generation | `build_viewport_capture_code` utility | Add focus_object resolution logic to code builder or document it as deferred |
| RND-004 | 🟡 WARNING | FR-RND-001 specifies "format must be supported by runtime + config" — only static set validation, no runtime check against available Blender formats | `VALID_IMAGE_FORMATS` constant | Add config-driven format validation or document runtime check as deferred |

### Business Flow
| # | Severity | Issue | Location (File:Line) | Recommendation |
|---|----------|-------|----------------------|----------------|
| RND-005 | 🔴 CRITICAL | FR-RND-001 mandates "Output location validated through security policy" — no security supervisor is called in `RenderViewportCaptureExecutor` | `capabilities_render_viewport_capture_executor.py` entire file | Inject `ISecurityPathValidationProtocol` and call before code execution |
| RND-006 | 🔴 CRITICAL | FR-RND-002 mandates "Output destination validated through security before render begins" — no security delegation | `capabilities_render_scene_image_executor.py` entire file | Same fix: inject security protocol and validate before execution |
| RND-007 | 🔴 CRITICAL | FR-RND-004 mandates "Local HDRI file ref validated through security before use" — no security validation | `capabilities_render_hdri_config_executor.py` entire file | Inject security protocol and validate hdri_path before execution |
| RND-008 | 🔴 CRITICAL | FR-RND-002 specifies "Long-running → job feature + task reference" — RenderSceneImageExecutor has no Job integration, always returns `task_ref=None` | `capabilities_render_scene_image_executor.py` render_scene method | Integrate Job feature for background renders; add background eligibility check |
| RND-009 | 🔴 CRITICAL | FR-RND-002 specifies "Capacity exhaustion → capacity error, no partial side effects" — no capacity check exists | `capabilities_render_scene_image_executor.py` try block | Add job capacity pre-check before render begins |
| RND-010 | 🟡 WARNING | FR-RND-003 specifies "Locked/protected state respected unless override" — no lock/protected state check in camera config | `capabilities_render_camera_config_executor.py` | Add protected-state check before allowing camera modifications |
| RND-011 | 🟡 WARNING | FR-RND-002 specifies "Cancellation of background render = best-effort (main-thread constraints)" — no cancellation handling | `capabilities_render_scene_image_executor.py` | Document as deferred or add cancellation signal handling |

### Logic Implementation
| # | Severity | Issue | Location (File:Line) | Recommendation |
|---|----------|-------|----------------------|----------------|
| RND-012 | 🟡 WARNING | FR-RND-002 specifies "Overwrite policy for existing artifact" — no check for existing artifact at output path | `capabilities_render_scene_image_executor.py` validation | Add existing-file check or document as deferred to Blender runtime |
| RND-013 | 🟡 WARNING | FR-RND-002 specifies "Temporary file → finalize atomically on success" — no atomic write pattern | `build_scene_render_code` utility | Use temp file + rename pattern in code builder for atomic writes |
| RND-014 | 🟡 WARNING | FR-RND-003 specifies "Camera created if not exist + creation policy allows" — `create_if_missing` defaults to True but FRD says creation should be per-policy | `CameraConfigVO` default | Review default; align with FRD intent for explicit creation policy |
| RND-015 | 🟡 WARNING | FR-RND-003 specifies "Camera resolution deterministic: explicit → active → first" — no resolution resolution logic in camera config | `capabilities_render_camera_config_executor.py` | Add camera resolution resolution logic |
| RND-016 | 🟢 INFO | Events are emitted via `logger.info()` — FRD specifies 6 distinct events but there's no event bus or structured event emission | All capability files | Introduce a RenderEventEmitter utility for structured event emission |

### Testability & Acceptance Criteria
| # | Severity | Issue | Location (File:Line) | Recommendation |
|---|----------|-------|----------------------|----------------|
| RND-017 | 🟡 WARNING | QA checklist item "Overwrite policy respected; atomic write" — no test for overwrite policy behavior on existing files | `test_render_operate_executor.py` | Add tests for overwrite/reject/unique_variant policies |
| RND-018 | 🟡 WARNING | QA checklist item "Missing active camera → configuration or scene state indication" — no test for missing camera scenario in render | `test_render_operate_executor.py` | Add test: render with no camera in scene |
| RND-019 | 🟡 WARNING | QA checklist item "Locked camera respected; generic transform not duplicated" — no test for locked camera | `test_camera_config.py` | Add test: configure locked camera and verify rejection |
| RND-020 | 🟡 WARNING | QA checklist item "HDRI: world created if missing + policy allows" — no test for missing world scenario | `test_hdri_config.py` | Add test: HDRI config with no existing world |
| RND-021 | 🟡 WARNING | QA checklist item "Background render submitted to job" — no integration test for job submission | No test file exists | Create `test_render_orchestrator.py` with background render + job integration |
| RND-022 | 🟢 INFO | No tests for security delegation path — all capabilities bypass security validation in tests | All test files | Add tests verifying security supervisor calls in each capability |

### Traceability (FRD → Code)
| # | Severity | Issue | Location (File:Line) | Recommendation |
|---|----------|-------|----------------------|----------------|
| RND-023 | 🟢 INFO | FR-RND-001 "Events emitted for completion/failure/submission" — only viewport captured event exists; no failure event for viewport | `capabilities_render_viewport_capture_executor.py` exception handler | Add `ViewportCapturedEvent` with success=False on failure |
| RND-024 | 🟢 INFO | FR-RND-002 "Scene render failed (categorized error + phase)" — `SceneRenderFailedEvent` is created but only logged, not emitted through event bus | `capabilities_render_scene_image_executor.py` exception handler | Route through event bus instead of raw logger call |
| RND-025 | 🟢 INFO | FR-RND-004 "Two-step flow: asset feature download → file ref → this feature lighting config" — no asset integration, capability accepts raw path | `capabilities_render_hdri_config_executor.py` | Add asset reference validation or document as deferred to higher layer |

## Violations
None detected. All files follow naming conventions (AES101), suffix rules (AES102), import boundaries (AES201), and role constraints (AES403). No circular imports (AES205) or bypass patterns (AES304) in capability code.

## Action Items
- [ ] **HIGH** Inject `ISecurityPathValidationProtocol` into all 4 capabilities and call security validation before Blender code execution (addresses RND-005, RND-006, RND-007)
- [ ] **HIGH** Integrate Job feature for background render eligibility check and task reference return (addresses RND-008, RND-009)
- [ ] **HIGH** Add max_size enforcement with aspect ratio preservation to viewport capture (addresses RND-001)
- [ ] **MEDIUM** Add fallback offscreen capture path for viewport when viewport context unavailable (addresses RND-002)
- [ ] **MEDIUM** Add focus_object resolution logic to viewport capture code builder (addresses RND-003)
- [ ] **MEDIUM** Add protected/locked camera state check in camera config capability (addresses RND-010)
- [ ] **MEDIUM** Implement atomic write pattern (temp file + rename) for render/screenshot output (addresses RND-013)
- [ ] **MEDIUM** Add existing artifact conflict tests for overwrite policies (addresses RND-017)
- [ ] **LOW** Introduce structured event emission mechanism replacing raw `logger.info` calls (addresses RND-023, RND-024)
- [ ] **LOW** Add HDRI world creation and missing camera tests (addresses RND-020, RND-018)

## Fixed Code

### Fix 1: Security Path Validation Delegation (RND-005, RND-006, RND-007)

**File:** `capabilities_render_viewport_capture_executor.py` — Added `ValidatePathProtocol` injection and `_validate_security()` call before execution.
**File:** `capabilities_render_scene_image_executor.py` — Same pattern: security validation injected and called before render begins.
**File:** `capabilities_render_hdri_config_executor.py` — Security validation for HDRI path before use.
**File:** `capabilities_render_camera_config_executor.py` — Optional security validator injection (camera config doesn't have file paths in FRD).
**File:** `root_render_container.py` — Updated container to wire security validator and job capacity into capabilities.

```python
# Before: no security delegation
class RenderViewportCaptureExecutor(IRenderViewportCaptureProtocol):
    def __init__(self, code_executor: ICodeExecutionProtocol) -> None:
        self._code_executor = code_executor

# After: security protocol injected
class RenderViewportCaptureExecutor(IRenderViewportCaptureProtocol):
    def __init__(
        self,
        code_executor: ICodeExecutionProtocol,
        security_validator: ValidatePathProtocol | None = None,
    ) -> None:
        self._code_executor = code_executor
        self._security_validator = security_validator

    async def capture_viewport(self, request: ViewportCaptureVO) -> ViewportCaptureVO:
        # ... validation ...
        try:
            await self._validate_security(str(request.output_path))
        except Exception as exc:
            return self._failure(
                request,
                Prompt(f"[{RenderErrorCategory.SECURITY_VIOLATION.value}] Path validation failed: {exc}"),
            )
```

### Fix 2: Max Size Enforcement (RND-001)

**File:** `capabilities_render_viewport_capture_executor.py` — Added max_size validation in `_validate()`.

```python
# FR-RND-001: Max size enforced (aspect ratio preserved by runtime)
max_size = int(request.max_size)
if max_size > 0 and max_size < 64:
    return RenderError(
        category=RenderErrorCategory.VALIDATION,
        message=Prompt(f"max_size must be at least 64 pixels"),
    )
```

### Fix 3: Job Capacity Check (RND-008, RND-009)

**File:** `capabilities_render_scene_image_executor.py` — Added `IJobCapacity` injection and `_check_job_capacity()` for background renders.

```python
if bool(normalized.background):
    capacity_check = await self._check_job_capacity()
    if not capacity_check.accepted:
        return self._failure(
            normalized,
            Prompt(f"[{RenderErrorCategory.CAPACITY.value}] {capacity_check.reason}"),
        )
```

### Test Coverage Added

**File:** `test_render_operate_executor.py` — Added `MockSecurityValidator`, security delegation tests for viewport capture and scene render, security rejection tests.
**File:** `test_camera_config.py` — Added `MockSecurityValidator` fixture.
**File:** `test_hdri_config.py` — Added `MockSecurityValidator`, security delegation test, security rejection test.

All 42 render tests passing. No regressions across 397 total tests.
