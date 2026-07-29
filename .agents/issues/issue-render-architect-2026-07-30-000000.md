<!-- Target file: .agents/issues/issue-render-architect-2026-07-30-000000.md -->

# Issue: render — Architectural Review & Refactoring

## Summary

The `render` feature has a mostly correct AES layer split: capabilities implement protocol contracts, the agent implements the render aggregate, and the root container wires concrete capabilities. However, the feature contains several architectural defects that must be addressed before it can be considered FRD-compliant and AES-safe. The most severe problems are: capabilities call a gateway contract method (`execute_python`) that is not defined by the injected contract; security path validation is optional and fails open; viewport and scene render result parsing can silently produce success with empty artifacts; background rendering is not actually integrated with the Job feature; and several Blender code builders ignore required FRD input fields. There are also AES hygiene issues: unused imports, dummy-looking mandatory imports in the aggregate contract, primitive-typed gateway contract signatures, and orphaned taxonomy/event definitions.

## Findings by Category

### Layer Boundaries

| # | Severity | Issue | Location (File:Line) | Recommendation |
|---|----------|-------|----------------------|----------------|
| 1 | 🔴 CRITICAL | Render capabilities call `self._code_executor.execute_python(code)`, but `ICodeExecutionProtocol` does not define `execute_python`. The injected contract defines `execute_blender_code`, `execute_task`, `create_task`, etc. This is a contract/implementation mismatch and can fail at runtime. | `modules/render/src/capabilities_render_camera_config_executor.py:_execute_code`; `modules/render/src/capabilities_render_hdri_config_executor.py:_execute_code`; `modules/render/src/capabilities_render_scene_image_executor.py:_execute_code`; `modules/render/src/capabilities_render_viewport_capture_executor.py:_execute_code`; contract: `modules/shared/src/gateway/contract_code_execution_protocol.py:ICodeExecutionProtocol` | Either add a VO-typed `execute_python` method to the gateway contract and implement it in the concrete gateway, or change render capabilities to use the existing `execute_blender_code` contract method and adapt `ExecutionResult` to `Prompt`. |
| 2 | 🔴 CRITICAL | Security validator is optional (`ValidatePathProtocol | None = None`) and `_validate_security` returns without validation when it is `None`. This fails open and bypasses FRD-mandated output/path security. | `modules/render/src/capabilities_render_viewport_capture_executor.py:__init__/_validate_security`; `modules/render/src/capabilities_render_scene_image_executor.py:__init__/_validate_security`; `modules/render/src/capabilities_render_hdri_config_executor.py:__init__/_validate_security`; `modules/render/src/root_render_container.py:__init__` | Make `security_validator` mandatory for render capabilities and container, or fail closed by raising `RenderError(category=SECURITY_VIOLATION)` when no validator is available. |
| 3 | 🟡 WARNING | `ICodeExecutionProtocol` uses primitive types in contract method signatures: `code: str`, `task_id: str`, `request_id: str | None`, return `str`. This violates AES402 contract-role expectations; contracts should use taxonomy VOs. | `modules/shared/src/gateway/contract_code_execution_protocol.py:ICodeExecutionProtocol` | Replace primitives with taxonomy types such as `PythonCode`, `RequestId`, `TaskUuid`, and typed result VOs. |
| 4 | 🟡 WARNING | Job capacity is optional and fails open: if `job_capacity` is `None`, scene render returns an accepted capacity decision with hardcoded limits. Background rendering can proceed without real capacity enforcement. | `modules/render/src/capabilities_render_scene_image_executor.py:_check_job_capacity` | If background rendering is requested, require a job capacity dependency or reject background execution. Do not synthesize a fake accepted `CapacityDecision`. |
| 5 | 🟡 WARNING | Capacity evaluation uses hardcoded `active_count=0` and default `JobPolicy()`, so the decision is not based on real job state or configured policy. | `modules/render/src/capabilities_render_scene_image_executor.py:_check_job_capacity` | Query real active job count and inject policy from configuration/job feature. |
| 6 | 🟢 INFO | Two overlapping code-execution contracts exist: `CodeExecutionProtocol` and `ICodeExecutionProtocol`. Render uses the second but calls a method from neither. This increases coupling and confusion. | `modules/shared/src/gateway/contract_code_execution_protocol.py` | Consolidate into one contract or clearly separate synchronous execution, async task lifecycle, and Python-code execution responsibilities. |

### Naming Convention

| # | Severity | Issue | Location (File:Line) | Recommendation |
|---|----------|-------|----------------------|----------------|
| 1 | 🟡 WARNING | Some shared contracts used by render do not follow the `I<Name>Protocol` convention: `CodeExecutionProtocol`, `ValidatePathProtocol`. Render contracts correctly use `IRender*Protocol`. | `modules/shared/src/gateway/contract_code_execution_protocol.py:CodeExecutionProtocol`; `modules/shared/src/security/contract_validate_path_protocol.py:ValidatePathProtocol` | Rename to `ICodeExecutionProtocol`/`IValidatePathProtocol` or provide canonical `I*` aliases and migrate consumers. |
| 2 | 🟢 INFO | `contract_render_aggregate.py` imports taxonomy VOs as unused aliases solely to satisfy mandatory import expectations. This resembles a dummy import smell. | `modules/shared/src/render/contract_render_aggregate.py:15-19` | Either remove the unused imports if AES202 does not require them, or make them meaningful by explicitly declaring aggregate method signatures using those VOs. |

### Dead Code / Orphan

| # | Severity | Issue | Location (File:Line) | Recommendation |
|---|----------|-------|----------------------|----------------|
| 1 | 🟡 WARNING | Unused imports in scene render capability: `uuid`, `JobId`, `TaskUuid`, `OperationType`, and `RenderSubmittedToBackgroundEvent` are imported but not used. | `modules/render/src/capabilities_render_scene_image_executor.py:5`, `:8-15`, `:22-26`, `:47-51` | Remove unused imports, or use them when implementing background render submission. |
| 2 | 🟡 WARNING | Unused `FilePath` import in viewport capture capability. | `modules/render/src/capabilities_render_viewport_capture_executor.py:8-14` | Remove import or use it in explicit typed annotations/result checks. |
| 3 | 🟡 WARNING | Unused `FilePath` import in HDRI capability. | `modules/render/src/capabilities_render_hdri_config_executor.py:8-14` | Remove import or use it in explicit typed annotations/result checks. |
| 4 | 🟢 INFO | `RenderSubmittedToBackgroundEvent` is defined and exported but never emitted. FRD expects a background-submission event, but current scene render never uses it. | `modules/shared/src/render/taxonomy_render_event.py:RenderSubmittedToBackgroundEvent`; `modules/shared/src/render/__init__.py` | Emit the event when background submission is implemented; otherwise remove until needed. |
| 5 | 🟢 INFO | `VALID_HDRI_STRENGTH_RANGE` is defined but not consumed by validation or exports. | `modules/shared/src/render/taxonomy_render_constant.py:VALID_HDRI_STRENGTH_RANGE` | Use it in HDRI validation or remove it. |
| 6 | 🟢 INFO | `DEFAULT_FOCUS_DISTANCE` is exported but not used by camera configuration defaults or code generation. | `modules/shared/src/render/taxonomy_render_constant.py:DEFAULT_FOCUS_DISTANCE`; `modules/shared/src/render/__init__.py` | Use it as a default for camera DoF or remove it. |
| 7 | 🟢 INFO | Unused aliased VOs in aggregate contract: `_CameraConfigVO`, `_HdriConfigVO`, `_RenderSceneVO`, `_ViewportCaptureVO`. | `modules/shared/src/render/contract_render_aggregate.py:15-19` | Make imports meaningful or remove them. |

### Scalability & Coupling

| # | Severity | Issue | Location (File:Line) | Recommendation |
|---|----------|-------|----------------------|----------------|
| 1 | 🟡 WARNING | Background rendering is not actually backgrounded. `RenderSceneVO.background` only triggers a capacity check, then the capability executes synchronously and returns `task_ref=None`. This violates FR-RND-002 long-running render flow. | `modules/render/src/capabilities_render_scene_image_executor.py:render_scene` | Integrate with Job feature: create task, submit background execution, emit `RenderSubmittedToBackgroundEvent`, and return `task_ref`. If Job integration is unavailable, reject `background=True`. |
| 2 | 🟡 WARNING | Viewport capture code builder ignores most FRD input fields: `max_size`, `view_angle`, `shading`, `show_overlays`, `focus_object`, and `overwrite_policy`. It also uses `bpy.ops.render.render`, which is scene rendering, not viewport capture. | `modules/shared/src/render/utility_render_code_builder.py:build_viewport_capture_code` | Generate true viewport-capture code using the 3D viewport context and consume all request fields. Implement max-size enforcement, shading mode, overlay visibility, focus handling, and overwrite policy. |
| 3 | 🟡 WARNING | Scene render code builder ignores `camera_ref`, `overwrite_policy`, `background`, transparency/color-mode-related FRD inputs, and timeout/background semantics. | `modules/shared/src/render/utility_render_code_builder.py:build_scene_render_code` | Extend generated Blender code to resolve camera reference, apply overwrite policy, and distinguish synchronous/background execution. |
| 4 | 🟡 WARNING | HDRI code builder ignores `overwrite_policy` and unconditionally loads/relinks environment nodes. This can duplicate nodes or replace existing environments contrary to policy. | `modules/shared/src/render/utility_render_code_builder.py:build_hdri_config_code` | Reuse existing world/node setup when policy allows, reject when policy is `reject`, and create unique variants when required. |
| 5 | 🟢 INFO | Capabilities construct and log domain events directly. This couples business capabilities to logger-based observability and makes event dispatch harder to scale. | All render capabilities | Consider introducing a taxonomy/contract event sink or diagnostics publisher so capabilities emit events through a protocol. |
| 6 | 🟢 INFO | Unified request/response VOs contain many input and output fields in one object. This is convenient but can obscure operation state and increase coupling between callers and internal result fields. | `modules/shared/src/render/taxonomy_render_vo.py` | Consider separate request/command VOs and result/status VOs if the render feature grows. |

### Data Flow

| # | Severity | Issue | Location (File:Line) | Recommendation |
|---|----------|-------|----------------------|----------------|
| 1 | 🔴 CRITICAL | Viewport capture can return `success=True` with empty artifact data. `parse_artifact_result` returns defaults on parse failure, and the capability does not validate `artifact_path`, `width`, or `height`. | `modules/render/src/capabilities_render_viewport_capture_executor.py:capture_viewport`; `modules/shared/src/render/utility_render_result_parser.py:parse_artifact_result` | After parsing, fail unless `artifact_path` is non-empty and dimensions are positive. |
| 2 | 🔴 CRITICAL | Scene render can return `success=True` with empty artifact data. `parse_render_result` returns defaults on parse failure, and the capability does not validate `artifact_path` or resolution. | `modules/render/src/capabilities_render_scene_image_executor.py:render_scene`; `modules/shared/src/render/utility_render_result_parser.py:parse_render_result` | After parsing, fail unless `artifact_path` is non-empty and resolution/render metrics are valid. |
| 3 | 🟡 WARNING | Security validation failures are raised as generic `Exception` and then converted into string messages. This loses domain error category structure and may leak exception details. | `modules/render/src/capabilities_render_viewport_capture_executor.py:_validate_security`; `modules/render/src/capabilities_render_scene_image_executor.py:_validate_security`; `modules/render/src/capabilities_render_hdri_config_executor.py:_validate_security` | Raise `RenderError(category=SECURITY_VIOLATION, message=...)` and redact sensitive denial details. |
| 4 | 🟡 WARNING | Capacity data flow is fake: active count is hardcoded and policy is default-constructed. The render feature does not receive real Job state. | `modules/render/src/capabilities_render_scene_image_executor.py:_check_job_capacity` | Inject a job-state query or pass active count/policy from the root/container. |
| 5 | 🟢 INFO | Result parsers accept raw `Prompt` stdout and silently return default VOs when JSON parsing fails. This hides execution contract violations. | `modules/shared/src/render/utility_render_result_parser.py` | Return typed parse results, raise parse errors, or return a result object that callers must validate. |

## Violations

- **AES203 — Unused Import**: unused imports in `capabilities_render_scene_image_executor.py`, `capabilities_render_viewport_capture_executor.py`, `capabilities_render_hdri_config_executor.py`, and `contract_render_aggregate.py`.
- **AES204 — Dummy Import smell**: `contract_render_aggregate.py` imports taxonomy VOs as unused aliases only to satisfy mandatory import expectations.
- **AES402 — Contract Role**: `ICodeExecutionProtocol` uses primitive types such as `str` in contract method signatures instead of taxonomy VOs.
- **AES501 — Taxonomy Orphan**: `RenderSubmittedToBackgroundEvent`, `VALID_HDRI_STRENGTH_RANGE`, and `DEFAULT_FOCUS_DISTANCE` appear unused by active render behavior.
- **Contract/Implementation Mismatch**: render capabilities call `execute_python`, which is absent from `ICodeExecutionProtocol`.
- **Fail-Open Security Boundary**: optional `security_validator` allows render operations to skip path validation.
- **Silent Error Discard**: viewport and scene render can succeed with empty/invalid parsed artifacts.

## Action Items (For Developer)

- [ ] P0 Align render capabilities with the gateway code-execution contract: remove calls to undefined `execute_python` or add a VO-typed `execute_python` method to the contract and concrete implementation.
- [ ] P0 Make security path validation fail closed: require `ValidatePathProtocol` in render capabilities and `RenderContainer`, or raise `RenderError(category=SECURITY_VIOLATION)` when unavailable.
- [ ] P0 Validate parsed viewport capture results: fail when `artifact_path` is empty or dimensions are invalid.
- [ ] P0 Validate parsed scene render results: fail when `artifact_path` is empty, resolution is invalid, or render metrics are missing.
- [ ] P1 Implement background render submission through the Job feature, including `task_ref` population and `RenderSubmittedToBackgroundEvent` emission; alternatively reject `background=True` until implemented.
- [ ] P1 Replace viewport capture code generation with true viewport capture logic that consumes `max_size`, `view_angle`, `shading`, `show_overlays`, `focus_object`, and `overwrite_policy`.
- [ ] P1 Extend scene render code generation to consume `camera_ref`, `overwrite_policy`, and background execution semantics.
- [ ] P1 Extend HDRI code generation to respect `overwrite_policy` and avoid duplicate world/node setup.
- [ ] P2 Remove unused imports from render capabilities and shared render contract files.
- [ ] P2 Replace primitive types in `ICodeExecutionProtocol` signatures with taxonomy VOs: `PythonCode`, `RequestId`, `TaskUuid`, and typed result VOs.
- [ ] P2 Rename or alias non-conventional shared contract classes to follow `I<Name>Protocol`.
- [ ] P3 Introduce an event publisher/sink contract so capabilities do not log domain events directly.
- [ ] P3 Consider splitting large unified request/response VOs into command and result VOs if render operations grow.

## Proposed Fixes / Reference Code

### 1. Align code execution with the existing gateway contract

Short-term fix for all render capabilities: stop calling undefined `execute_python` and use `execute_blender_code`.

```python
# modules/render/src/capabilities_render_*_executor.py

from modules.shared.src.common.taxonomy_core_vo import Prompt, PythonCode, RequestId
from modules.shared.src.render.taxonomy_render_error import RenderError, RenderErrorCategory


async def _execute_code(
    self,
    code: PythonCode,
    correlation_id: RequestId,
) -> Prompt:
    result = await self._code_executor.execute_blender_code(
        str(code),
        str(correlation_id) or None,
    )

    if result.status != "success":
        message = "Code execution failed"
        if result.error is not None and result.error.message:
            message = result.error.message

        raise RenderError(
            category=RenderErrorCategory.EXECUTION,
            message=Prompt(message),
        )

    return Prompt(str(result.data or ""))
```

Update call sites:

```python
# Before
raw = await self._execute_code(code)

# After
raw = await self._execute_code(code, request.correlation_id)
```

Long-term target for the gateway contract:

```python
# modules/shared/src/gateway/contract_code_execution_protocol.py

from modules.shared.src.common.taxonomy_core_vo import (
    Prompt,
    PythonCode,
    RequestId,
    TaskUuid,
)


class ICodeExecutionProtocol(ABC):
    @abstractmethod
    async def execute_python(
        self,
        code: PythonCode,
        request_id: RequestId | None = None,
    ) -> Prompt: ...

    @abstractmethod
    def create_task(
        self,
        request_id: RequestId | None = None,
    ) -> TaskUuid: ...
```

### 2. Fail closed on security validation

Make the dependency required in capabilities:

```python
# modules/render/src/capabilities_render_viewport_capture_executor.py


class RenderViewportCaptureExecutor(IRenderViewportCaptureProtocol):
    def __init__(
        self,
        code_executor: ICodeExecutionProtocol,
        security_validator: ValidatePathProtocol,
    ) -> None:
        self._code_executor = code_executor
        self._security_validator = security_validator
```

Fail closed if the validator is missing:

```python
async def _validate_security(self, path: str) -> None:
    if self._security_validator is None:
        raise RenderError(
            category=RenderErrorCategory.SECURITY_VIOLATION,
            message=Prompt("Security path validator is unavailable"),
        )

    request = PathValidationVO(
        target_path=path,
        access_mode=AccessMode.WRITE,
    )

    result = await self._security_validator.validate_path(request)

    if not result.allowed:
        raise RenderError(
            category=RenderErrorCategory.SECURITY_VIOLATION,
            message=Prompt(result.denial_reason or "Path validation denied"),
        )
```

Update container wiring:

```python
# modules/render/src/root_render_container.py


class RenderContainer:
    def __init__(
        self,
        code_executor: ICodeExecutionProtocol,
        security_validator: ValidatePathProtocol,
        job_capacity: IJobCapacity | None = None,
    ) -> None:
        self._code_executor = code_executor
        self._security_validator = security_validator
        self._job_capacity = job_capacity
        self._lock = threading.Lock()
        self._orchestrator: RenderOrchestrator | None = None
```

### 3. Validate parsed viewport capture output

```python
# modules/render/src/capabilities_render_viewport_capture_executor.py

artifact_path, width, height, resolved_format = parse_artifact_result(raw)

if not str(artifact_path).strip():
    return self._failure(
        request,
        Prompt(f"[{RenderErrorCategory.RENDER_OUTPUT.value}] Viewport capture failed: artifact path missing"),
    )

if int(width) <= 0 or int(height) <= 0:
    return self._failure(
        request,
        Prompt(f"[{RenderErrorCategory.RENDER_OUTPUT.value}] Viewport capture failed: invalid image dimensions"),
    )
```

### 4. Validate parsed scene render output

```python
# modules/render/src/capabilities_render_scene_image_executor.py

metrics = parse_render_result(raw)

if not str(metrics.artifact_path).strip():
    return self._failure(
        normalized,
        Prompt(f"[{RenderErrorCategory.RENDER_OUTPUT.value}] Scene render failed: artifact path missing"),
    )

if int(metrics.width) <= 0 or int(metrics.height) <= 0:
    return self._failure(
        normalized,
        Prompt(f"[{RenderErrorCategory.RENDER_OUTPUT.value}] Scene render failed: invalid render resolution"),
    )
```

### 5. Reject background execution until Job integration exists

Temporary safe behavior:

```python
# modules/render/src/capabilities_render_scene_image_executor.py

if bool(normalized.background):
    return self._failure(
        normalized,
        Prompt(f"[{RenderErrorCategory.CAPACITY.value}] Background rendering is not wired to the job feature"),
    )
```

Target Job-integrated behavior:

```python
# modules/render/src/capabilities_render_scene_image_executor.py

from modules.shared.src.common.taxonomy_core_vo import TaskUuid
from modules.shared.src.render.taxonomy_render_event import (
    RenderSubmittedToBackgroundEvent,
)


if bool(normalized.background):
    capacity_check = await self._check_job_capacity()
    if not capacity_check.accepted:
        return self._failure(
            normalized,
            Prompt(f"[{RenderErrorCategory.CAPACITY.value}] {capacity_check.reason}"),
        )

    task_id = self._code_executor.create_task(
        str(normalized.correlation_id) or None,
    )

    event = RenderSubmittedToBackgroundEvent(
        correlation_id=normalized.correlation_id,
        success=SuccessFlag(True),
        task_ref=TaskUuid(task_id),
        message=Prompt("Scene render submitted to background"),
    )
    logger.info("render_submitted_to_background event=%s", event)

    return replace(
        normalized,
        success=SuccessFlag(True),
        task_ref=TaskUuid(task_id),
        message=Prompt("Scene render submitted to background"),
    )
```

### 6. Make aggregate contract imports meaningful

```python
# modules/shared/src/render/contract_render_aggregate.py

from __future__ import annotations

from abc import abstractmethod

from .contract_render_camera_config_protocol import IRenderCameraConfigProtocol
from .contract_render_hdri_config_protocol import IRenderHdriConfigProtocol
from .contract_render_scene_image_protocol import IRenderSceneImageProtocol
from .contract_render_viewport_capture_protocol import IRenderViewportCaptureProtocol
from .taxonomy_render_vo import (
    CameraConfigVO,
    HdriConfigVO,
    RenderSceneVO,
    ViewportCaptureVO,
)


class IRenderAggregate(
    IRenderViewportCaptureProtocol,
    IRenderSceneImageProtocol,
    IRenderCameraConfigProtocol,
    IRenderHdriConfigProtocol,
):
    """Facade for render feature behavior."""

    @abstractmethod
    async def capture_viewport(
        self,
        request: ViewportCaptureVO,
    ) -> ViewportCaptureVO: ...

    @abstractmethod
    async def render_scene(
        self,
        request: RenderSceneVO,
    ) -> RenderSceneVO: ...

    @abstractmethod
    async def configure_camera(
        self,
        request: CameraConfigVO,
    ) -> CameraConfigVO: ...

    @abstractmethod
    async def configure_hdri(
        self,
        request: HdriConfigVO,
    ) -> HdriConfigVO: ...
```

### 7. Remove unused imports

```python
# modules/render/src/capabilities_render_scene_image_executor.py

# Remove:
# import uuid
# JobId
# TaskUuid
# OperationType
# RenderSubmittedToBackgroundEvent  # keep only when background submission is implemented
```

```python
# modules/render/src/capabilities_render_viewport_capture_executor.py

# Remove unused FilePath import if not used in annotations.
```

```python
# modules/render/src/capabilities_render_hdri_config_executor.py

# Remove unused FilePath import if not used in annotations.
```

### 8. Consume required viewport capture fields in code generation

Reference structure; the generated Blender code must use all FRD inputs:

```python
# modules/shared/src/render/utility_render_code_builder.py


def build_viewport_capture_code(request: ViewportCaptureVO) -> PythonCode:
    output_path = str(request.output_path)
    image_format = str(request.image_format).upper()
    max_size = int(request.max_size)
    view_angle = str(request.view_angle)
    shading = str(request.shading)
    show_overlays = bool(request.show_overlays)
    focus_object = str(request.focus_object or "")
    overwrite_policy = str(request.overwrite_policy)

    lines = [
        "import bpy",
        "import json",
        "",
        f"output_path = {output_path!r}",
        f"image_format = {image_format!r}",
        f"max_size = {max_size!r}",
        f"view_angle = {view_angle!r}",
        f"shading = {shading!r}",
        f"show_overlays = {show_overlays!r}",
        f"focus_object = {focus_object!r}",
        f"overwrite_policy = {overwrite_policy!r}",
        "",
        "# TODO: resolve 3D viewport area",
        "# TODO: apply view_angle (perspective/orthographic/active_camera)",
        "# TODO: apply shading mode",
        "# TODO: toggle overlays",
        "# TODO: focus object if provided",
        "# TODO: enforce max_size while preserving aspect ratio",
        "# TODO: resolve overwrite policy",
        "# TODO: use viewport capture (for example bpy.ops.render.opengl) not scene render",
        "",
        "result = {",
        "    'artifact_path': output_path,",
        "    'width': 0,",
        "    'height': 0,",
        "    'format': image_format",
        "}",
        "",
        "print(json.dumps(result))",
    ]

    return PythonCode("\n".join(lines))
```

### 9. Consume overwrite policy in scene/HDRI code generation

Reference structure:

```python
# modules/shared/src/render/utility_render_code_builder.py


def build_scene_render_code(request: RenderSceneVO) -> PythonCode:
    output_path = str(request.output_path)
    overwrite_policy = str(request.overwrite_policy)
    camera_ref = str(request.camera_ref or "")

    lines = [
        "import bpy",
        "import json",
        "",
        f"output_path = {output_path!r}",
        f"overwrite_policy = {overwrite_policy!r}",
        f"camera_ref = {camera_ref!r}",
        "",
        "# TODO: resolve camera_ref deterministically",
        "# TODO: apply overwrite_policy (overwrite/reject/unique)",
        "# TODO: render to temporary path and finalize atomically",
    ]

    return PythonCode("\n".join(lines))
```

```python
# modules/shared/src/render/utility_render_code_builder.py


def build_hdri_config_code(request: HdriConfigVO) -> PythonCode:
    hdri_path = str(request.hdri_path)
    overwrite_policy = str(request.overwrite_policy)

    lines = [
        "import bpy",
        "import json",
        "",
        f"hdri_path = {hdri_path!r}",
        f"overwrite_policy = {overwrite_policy!r}",
        "",
        "# TODO: reuse existing world/environment when policy allows",
        "# TODO: reject when overwrite_policy == 'reject' and environment exists",
        "# TODO: create unique environment variant when policy == 'unique'",
    ]

    return PythonCode("\n".join(lines))
```