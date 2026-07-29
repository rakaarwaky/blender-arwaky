# Issue: scene — Architectural Review & Refactoring

## Summary
The `modules/scene` feature has a mostly correct AES layer skeleton: surface delegates to an aggregate, the agent orchestrates via contracts, capabilities implement protocols, and shared taxonomy/contract/utility files are separated. However, the feature contains critical execution-path defects and FRD boundary violations: scene cleanup generates raw Blender code that does not actually delete objects, inspection code builders can emit invalid Python, and capabilities parse gateway results using a nonexistent `output` field. In addition, scene cleanup bypasses the required Object-feature delegation boundary, event emission is not wired through a typed contract, several taxonomy constants/policy fields are unused, and the gateway contract consumed by scene uses primitive types in protocol signatures. This issue should be addressed before the scene feature can be considered safe, observable, and AES-compliant.

Issue ID: `issue-scene-architect-2026-07-30-000000`

## Findings by Category

### Layer Boundaries
| # | Severity | Issue | Location (File:Line) | Recommendation |
|---|----------|-------|----------------------|----------------|
| 1 | 🔴 **CRITICAL** | Scene cleanup owns raw Blender deletion code instead of delegating technical deletion to the Object feature. FRD explicitly states: scene decides policy, object executes deletion. Current scene utility builds Blender deletion code and scene capability executes it through gateway. | `modules/shared/src/scene/utility_scene_code_builder.py:build_cleanup_code`; `modules/scene/src/capabilities_scene_cleanup_executor.py:SceneCleanupExecutor.cleanup_scene` | Introduce an Object-domain deletion contract, for example `IObjectDeletionProtocol`, in shared/object contracts. Scene cleanup should resolve candidates/preservation and delegate deletion execution to the object contract. |
| 2 | 🟡 **WARNING** | Event emitter dependency is typed as `object | None`, creating an implicit, untyped contract. This weakens dependency inversion and makes event emission untestable. | `modules/scene/src/capabilities_scene_cleanup_executor.py:SceneCleanupExecutor.__init__` | Define a shared event emitter protocol, for example `IEventEmitterProtocol`, and inject that protocol into capabilities. |
| 3 | 🟡 **WARNING** | Root container does not provide an event emitter. Cleanup capability supports optional emission, but the container always constructs it with `None`, so FRD events are never emitted. | `modules/scene/src/root_scene_container.py:SceneContainer.get_aggregate` | Accept an optional event emitter in `SceneContainer` / `create_scene_container` and pass it to both inspection and cleanup capabilities. |
| 4 | 🟡 **WARNING** | Scene capabilities consume `ICodeExecutionProtocol`, whose methods use primitive `str` / `int` in contract signatures. This violates AES402 contract-role expectations: contracts should use taxonomy VOs. | `modules/shared/src/gateway/contract_code_execution_protocol.py:ICodeExecutionProtocol` | Replace primitive parameters/returns with taxonomy VOs such as `PythonCode`, `RequestId`, `TaskUuid`, and a typed count VO for `cleanup_expired`. |
| 5 | 🟡 **WARNING** | `SceneError` is a frozen dataclass but does not extend `Exception`. Python taxonomy guidance requires domain errors to extend `Exception`. This prevents idiomatic raise/catch flow and blurs taxonomy error semantics. | `modules/shared/src/scene/taxonomy_scene_error.py:SceneError` | Make `SceneError` extend `Exception`, or introduce a separate exception type wrapping the immutable error VO. |
| 6 | 🟢 **INFO** | Aggregate contract imports taxonomy VOs only to satisfy AES202, but does not use them. This creates a dummy-import smell. | `modules/shared/src/scene/contract_scene_aggregate.py` | Remove unused imports, or adjust AES202 expectations for aggregate contracts that inherit protocol methods already typed by taxonomy VOs. |

### Naming Convention
| # | Severity | Issue | Location (File:Line) | Recommendation |
|---|----------|-------|----------------------|----------------|
| 1 | 🟡 **WARNING** | Detail levels and render defaults are represented as ad-hoc strings in utility code instead of using taxonomy constants. This weakens traceability and invites magic-string drift. | `modules/shared/src/scene/utility_scene_code_builder.py:build_inspection_code`; `modules/shared/src/scene/utility_scene_result_parser.py:parse_scene_state_summary` | Use `DETAIL_LEVEL_MINIMAL`, `DETAIL_LEVEL_STANDARD`, `DETAIL_LEVEL_DETAILED`, `DETAIL_LEVEL_SUMMARY`, and render/unit defaults from taxonomy constants. |
| 2 | 🟢 **INFO** | `SceneCommand` is not exported from the scene package `__init__.py`. The surface may still be imported directly, but public discovery is weaker. | `modules/scene/src/__init__.py` | Export `SceneCommand` if it is the intended public smart surface, or document the direct import path in the feature README/FRD. |

### Dead Code / Orphan
| # | Severity | Issue | Location (File:Line) | Recommendation |
|---|----------|-------|----------------------|----------------|
| 1 | 🟡 **WARNING** | Unused taxonomy imports aliased as `_SceneCleanupVO` and `_SceneInspectionVO`. These are not referenced in the aggregate contract. AES203/AES204 risk. | `modules/shared/src/scene/contract_scene_aggregate.py` | Remove the unused imports unless a linter rule explicitly requires them; if required, configure the rule instead of adding dummy imports. |
| 2 | 🟡 **WARNING** | Several constants are exported but not consumed by scene behavior: timeout constants, max inspection limit, some protected-object policies, and some detail-level constants. | `modules/shared/src/scene/taxonomy_scene_constant.py` | Either enforce these constants in capabilities/utilities or remove them to avoid orphan taxonomy. |
| 3 | 🟡 **WARNING** | `SceneCleanupPolicyVO.include_hidden_objects`, `protect_active_camera`, and `protect_sole_camera` are defined but not consumed by `build_cleanup_code`. | `modules/shared/src/scene/taxonomy_scene_vo.py:SceneCleanupPolicyVO`; `modules/shared/src/scene/utility_scene_code_builder.py:build_cleanup_code` | Consume the fields in generated cleanup policy, or remove them until required. |
| 4 | 🟡 **WARNING** | `SceneCommand` is not referenced by any entry/router/container in the provided snapshot. This may be an AES506 surface orphan depending on external wiring. | `modules/scene/src/surface_scene_command.py`; `modules/scene/src/__init__.py` | Verify that CLI/MCP/dispatcher entry points import and use `SceneCommand`. If not, wire it or remove it. |
| 5 | 🟢 **INFO** | `SceneInspectionCompletedEvent` is constructed but never emitted. It is only logged, making the event effectively dead telemetry. | `modules/scene/src/capabilities_scene_inspection_executor.py:SceneInspectionExecutor.get_scene_info` | Inject an event emitter and emit the event, or remove event construction until emission is supported. |

### Scalability & Coupling
| # | Severity | Issue | Location (File:Line) | Recommendation |
|---|----------|-------|----------------------|----------------|
| 1 | 🔴 **CRITICAL** | `build_cleanup_code` increments `removed_count` but never deletes objects. The cleanup report can claim removals while the scene remains unchanged. | `modules/shared/src/scene/utility_scene_code_builder.py:build_cleanup_code` | Implement actual deletion in Blender, preferably by delegating to Object-feature deletion primitives. Ensure removed/preserved/skipped refs reflect real mutation. |
| 2 | 🔴 **CRITICAL** | Standard and detailed inspection builders emit invalid Python because double braces are used in ordinary strings, not format templates. Example: `objects_by_type = {{}}` becomes invalid generated code. | `modules/shared/src/scene/utility_scene_code_builder.py:_build_standard_inspection_code`; `modules/shared/src/scene/utility_scene_code_builder.py:_build_detailed_inspection_code` | Use proper templating. If using f-strings, double braces are okay because they collapse to single braces; if using plain strings, use single braces. Add unit tests that compile generated code. |
| 3 | 🟡 **WARNING** | Cleanup capability hardcodes `preserve_cameras=True` and does not derive preservation fully from request/config. This reduces configurability and contradicts FRD policy resolution expectations. | `modules/scene/src/capabilities_scene_cleanup_executor.py:SceneCleanupExecutor.cleanup_scene` | Resolve preservation policy from request and configuration. If cameras are always protected, encode that rule explicitly in taxonomy/config, not as an inline surprise. |
| 4 | 🟡 **WARNING** | Cleanup pre-flight validates child/dependent policies but does not validate `mode` against `VALID_CLEANUP_MODES`. | `modules/scene/src/capabilities_scene_cleanup_executor.py:SceneCleanupExecutor._pre_flight_check` | Add validation for cleanup mode using `VALID_CLEANUP_MODES`. |
| 5 | 🟡 **WARNING** | Timeout constants exist but are not enforced. Capabilities do not wrap gateway execution with timeout control. | `modules/scene/src/capabilities_scene_cleanup_executor.py:SceneCleanupExecutor.cleanup_scene`; `modules/scene/src/capabilities_scene_inspection_executor.py:SceneInspectionExecutor.get_scene_info` | Use `asyncio.wait_for` with `CLEANUP_TIMEOUT_SECONDS` and `INSPECTION_TIMEOUT_SECONDS`, mapping timeout to `SceneErrorCategory.TIMEOUT`. |
| 6 | 🟡 **WARNING** | Broad `except Exception` maps many failure modes to `SCENE_STATE`, hiding root causes and making diagnostics harder. | `modules/scene/src/capabilities_scene_cleanup_executor.py:SceneCleanupExecutor.cleanup_scene`; `modules/scene/src/capabilities_scene_inspection_executor.py:SceneInspectionExecutor.get_scene_info` | Catch specific exceptions and preserve cause context. Use delegated-deletion, validation, connection, timeout, and protection categories where appropriate. |
| 7 | 🟡 **WARNING** | Frozen VOs expose mutable structures such as `dict` and list-backed NewTypes. This weakens value-object immutability. | `modules/shared/src/scene/taxonomy_scene_vo.py:SceneStateSummaryVO`; `modules/shared/src/scene/taxonomy_scene_vo.py:CameraInfoVO`; `modules/shared/src/scene/taxonomy_scene_vo.py:LightInfoVO` | Prefer tuples, frozen mappings, or immutable vector types for VO fields. |
| 8 | 🟢 **INFO** | Event emission try/except blocks are repeated multiple times inside cleanup capability. | `modules/scene/src/capabilities_scene_cleanup_executor.py:SceneCleanupExecutor.cleanup_scene` | Extract a private `_emit_event` helper in Block 3. |

### Data Flow
| # | Severity | Issue | Location (File:Line) | Recommendation |
|---|----------|-------|----------------------|----------------|
| 1 | 🔴 **CRITICAL** | `_execute_code` expects `result.output`, but `ExecutionResult` exposes `data`, not `output`. The fallback `str(result)` causes parsers to receive the string representation of `ExecutionResult`, not Blender JSON output. | `modules/scene/src/capabilities_scene_cleanup_executor.py:SceneCleanupExecutor._execute_code`; `modules/scene/src/capabilities_scene_inspection_executor.py:SceneInspectionExecutor._execute_code` | Read `ExecutionResult.status` and `ExecutionResult.data`. Convert `data` to string/JSON explicitly and raise typed errors when status is not success. |
| 2 | 🟡 **WARNING** | Inspection capability does not emit inspection events. FRD requires event emission for inspection completion. | `modules/scene/src/capabilities_scene_inspection_executor.py:SceneInspectionExecutor.get_scene_info` | Add event emitter dependency and emit `SceneInspectionCompletedEvent` and failure events. |
| 3 | 🟡 **WARNING** | Parser silently substitutes defaults for missing render settings, collections, and protected object summary. This can mask incomplete inspection payloads. | `modules/shared/src/scene/utility_scene_result_parser.py:parse_scene_state_summary` | Distinguish absent fields from real defaults, validate required fields, and return explicit capability/message metadata when payload is partial. |
| 4 | 🟡 **WARNING** | Cleanup dry-run and actual cleanup share report shape, but actual cleanup currently does not mutate the scene. Downstream consumers receive misleading state transitions. | `modules/shared/src/scene/utility_scene_code_builder.py:build_cleanup_code`; `modules/scene/src/capabilities_scene_cleanup_executor.py:SceneCleanupExecutor.cleanup_scene` | Ensure actual cleanup performs deletion and emits `SceneCleanupCompletedEvent` only after successful mutation. |
| 5 | 🟢 **INFO** | Standard inspection payload omits render settings, unit system, collections, and protected-object summary required by FR-SCN-001. Parser then fills defaults, creating false completeness. | `modules/shared/src/scene/utility_scene_code_builder.py:_build_standard_inspection_code`; `modules/shared/src/scene/utility_scene_result_parser.py:parse_scene_state_summary` | Extend standard inspection code to include required summary fields, or clearly mark omitted fields as unavailable. |

## Violations
- **AES203 / AES204**: Unused or dummy taxonomy imports in `contract_scene_aggregate.py`.
- **AES402**: `ICodeExecutionProtocol` uses primitive `str` and `int` in contract method signatures instead of taxonomy VOs.
- **AES506 potential**: `SceneCommand` is not referenced by an entry/router in the provided snapshot; verify surface wiring.
- **AES401-related taxonomy role concern**: `SceneError` does not extend `Exception`, weakening Python domain-error semantics.
- **Architecture boundary violation**: Scene cleanup performs raw Blender deletion logic instead of delegating technical deletion to the Object feature, contrary to the scene FRD boundary.
- **Value-object immutability concern**: Frozen scene VOs expose mutable `dict`/list-backed fields.

## Action Items (For Developer)
- [ ] P0 Fix `_execute_code` in both scene capabilities to consume `ExecutionResult.status` and `ExecutionResult.data` correctly.
- [ ] P0 Fix invalid generated Python in `_build_standard_inspection_code` and `_build_detailed_inspection_code`.
- [ ] P0 Make cleanup truthful: either implement actual deletion in generated code or, preferably, delegate deletion to an Object-feature contract.
- [ ] P0 Introduce and use an Object deletion protocol so scene owns policy and object owns execution.
- [ ] P1 Add typed event emitter protocol and wire it through `SceneContainer` into both capabilities.
- [ ] P1 Emit inspection completed/failed events and cleanup completed/dry-run/failed events through the injected emitter.
- [ ] P1 Enforce timeouts using `INSPECTION_TIMEOUT_SECONDS` and `CLEANUP_TIMEOUT_SECONDS`.
- [ ] P1 Validate cleanup mode against `VALID_CLEANUP_MODES`.
- [ ] P1 Replace primitive types in `ICodeExecutionProtocol` with taxonomy VOs: `PythonCode`, `RequestId`, `TaskUuid`, typed count VO.
- [ ] P1 Make `SceneError` an exception type or wrap it in a dedicated exception.
- [ ] P2 Remove unused taxonomy imports, unused constants, and unused policy fields, or implement their intended behavior.
- [ ] P2 Replace mutable VO fields with immutable tuples/frozen mappings.
- [ ] P2 Verify `SceneCommand` is wired into CLI/MCP/dispatcher entry points and export it if public.

## Proposed Fixes / Reference Code

### `modules/shared/src/scene/contract_scene_aggregate.py`
Remove dummy taxonomy imports.

```python
"""Scene domain contract: scene aggregate."""

from __future__ import annotations

from .contract_scene_cleanup_protocol import ISceneCleanupProtocol
from .contract_scene_inspection_protocol import ISceneInspectionProtocol


class ISceneAggregate(ISceneInspectionProtocol, ISceneCleanupProtocol):
    """Facade for scene feature behavior.

    Combines:
    - FR-SCN-001 inspection
    - FR-SCN-002 cleanup
    """
```

---

### `modules/shared/src/scene/taxonomy_scene_error.py`
Make scene errors raisable.

```python
from dataclasses import dataclass
from enum import Enum
from typing import NewType

from ..common.taxonomy_core_vo import Prompt

SceneErrorDetails = NewType("SceneErrorDetails", tuple[Prompt, ...])


class SceneErrorCategory(str, Enum):
    CONNECTION = "connection"
    TIMEOUT = "timeout"
    SCENE_STATE = "scene_state"
    PROTECTION = "protection"
    VALIDATION = "validation"
    CONFIRMATION = "confirmation"
    DELEGATED_DELETION = "delegated_deletion"


@dataclass(frozen=True)
class SceneError(Exception):
    """Immutable scene domain error that can be raised and caught."""

    category: SceneErrorCategory
    message: Prompt
    retryable: bool = False
    details: SceneErrorDetails = ()

    def __str__(self) -> str:
        return str(self.to_prompt())

    def to_prompt(self) -> Prompt:
        return Prompt(f"[{self.category.value}] {self.message}")
```

---

### `modules/shared/src/gateway/contract_code_execution_protocol.py`
Use taxonomy VOs in contract signatures.

```python
from __future__ import annotations

from abc import ABC, abstractmethod

from ..common.taxonomy_core_vo import PythonCode, RequestId, TaskUuid
from .taxonomy_gateway_vo import ExecutionResult, TaskStatus


class ICodeExecutionProtocol(ABC):
    """Protocol for executing Python code in Blender and managing async tasks."""

    @abstractmethod
    async def execute_blender_code(
        self,
        code: PythonCode,
        request_id: RequestId | None = None,
    ) -> ExecutionResult: ...

    @abstractmethod
    async def execute_task(
        self,
        task_id: TaskUuid,
        code: PythonCode,
        request_id: RequestId | None = None,
    ) -> ExecutionResult: ...

    @abstractmethod
    def create_task(self, request_id: RequestId | None = None) -> TaskUuid: ...

    @abstractmethod
    def get_task(self, task_id: TaskUuid) -> TaskStatus: ...

    @abstractmethod
    async def poll_task_result(
        self,
        task_id: TaskUuid,
        request_id: RequestId | None = None,
    ) -> TaskStatus: ...

    @abstractmethod
    async def cancel_async_task(
        self,
        task_id: TaskUuid,
        request_id: RequestId | None = None,
    ) -> TaskStatus: ...
```

---

### `modules/scene/src/capabilities_scene_inspection_executor.py`
Correct gateway result extraction and add timeout enforcement.

```python
import asyncio
import json

from modules.shared.src.scene.taxonomy_scene_constant import INSPECTION_TIMEOUT_SECONDS


async def _execute_code(self, code: PythonCode) -> str:
    """Execute code via injected code executor and return raw string output."""
    try:
        result = await asyncio.wait_for(
            self._code_executor.execute_blender_code(code),
            timeout=INSPECTION_TIMEOUT_SECONDS,
        )
    except asyncio.TimeoutError as exc:
        raise TimeoutError("Scene inspection timed out") from exc

    if result.status != "success":
        message = result.error.message if result.error else "Blender code execution failed"
        raise RuntimeError(message)

    data = result.data
    if isinstance(data, str):
        return data
    if isinstance(data, bytes):
        return data.decode("utf-8")
    if data is None:
        return ""
    return json.dumps(data)
```

---

### `modules/scene/src/capabilities_scene_cleanup_executor.py`
Add mode validation and correct execution extraction.

```python
import asyncio
import json

from modules.shared.src.scene.taxonomy_scene_constant import (
    CLEANUP_TIMEOUT_SECONDS,
    VALID_CLEANUP_MODES,
)


def _pre_flight_check(self, request: SceneCleanupVO) -> SceneError | None:
    if request.mode not in VALID_CLEANUP_MODES:
        return SceneError(
            category=SceneErrorCategory.VALIDATION,
            message=Prompt(f"Invalid cleanup mode: {request.mode}"),
        )

    # existing child/dependent policy checks remain here
    return None


async def _execute_code(self, code: PythonCode) -> str:
    try:
        result = await asyncio.wait_for(
            self._code_executor.execute_blender_code(code),
            timeout=CLEANUP_TIMEOUT_SECONDS,
        )
    except asyncio.TimeoutError as exc:
        raise TimeoutError("Scene cleanup timed out") from exc

    if result.status != "success":
        message = result.error.message if result.error else "Blender code execution failed"
        raise SceneError(
            category=SceneErrorCategory.DELEGATED_DELETION,
            message=Prompt(message),
        )

    data = result.data
    if isinstance(data, str):
        return data
    if isinstance(data, bytes):
        return data.decode("utf-8")
    if data is None:
        return ""
    return json.dumps(data)
```

---

### `modules/shared/src/scene/utility_scene_code_builder.py`
Use valid Python generation and consume policy fields.

```python
import textwrap

from ..common.taxonomy_core_vo import PythonCode
from .taxonomy_scene_constant import (
    CLEANUP_MODE_ALL,
    CLEANUP_MODE_MESHES,
    CLEANUP_MODE_OBJECTS,
    DETAIL_LEVEL_DETAILED,
    DETAIL_LEVEL_MINIMAL,
    DETAIL_LEVEL_STANDARD,
    DETAIL_LEVEL_SUMMARY,
)
from .taxonomy_scene_vo import SceneCleanupPolicyVO, SceneInspectionVO


def build_inspection_code(request: SceneInspectionVO) -> PythonCode:
    include_hidden = bool(request.include_hidden_objects)
    detail_level = request.detail_level or DETAIL_LEVEL_STANDARD

    if detail_level == DETAIL_LEVEL_MINIMAL:
        return _build_minimal_inspection_code(include_hidden)
    if detail_level == DETAIL_LEVEL_DETAILED:
        return _build_detailed_inspection_code(include_hidden)
    if detail_level in (DETAIL_LEVEL_STANDARD, DETAIL_LEVEL_SUMMARY):
        return _build_standard_inspection_code(include_hidden)

    return _build_standard_inspection_code(include_hidden)


def _build_standard_inspection_code(include_hidden: bool) -> PythonCode:
    return PythonCode(
        textwrap.dedent(
            f"""
            import bpy
            import json

            include_hidden = {include_hidden!r}
            scene = bpy.context.scene
            view_layer = bpy.context.view_layer

            objects_by_type = {{}}
            visible_count = 0
            hidden_count = 0
            cameras = []
            lights = []

            for obj in scene.objects:
                is_hidden = bool(obj.hide_viewport)
                if is_hidden:
                    hidden_count += 1
                else:
                    visible_count += 1

                if not include_hidden and is_hidden:
                    continue

                obj_type = obj.type
                objects_by_type[obj_type] = objects_by_type.get(obj_type, 0) + 1

                if obj_type == 'CAMERA':
                    cameras.append({{'name': obj.name}})
                elif obj_type == 'LIGHT':
                    lights.append({{'name': obj.name}})

            result = {{
                'scene_name': scene.name,
                'total_object_count': len(scene.objects),
                'visible_object_count': visible_count,
                'hidden_object_count': hidden_count,
                'object_type_counts': objects_by_type,
                'cameras': cameras,
                'lights': lights,
                'active_camera_name': scene.camera.name if scene.camera else '',
                'active_object_name': view_layer.objects.active.name if view_layer.objects.active else '',
                'render_engine': scene.render.engine.lower(),
                'resolution_x': scene.render.resolution_x,
                'resolution_y': scene.render.resolution_y,
                'frame_start': scene.frame_start,
                'frame_end': scene.frame_end,
                'unit_system': scene.unit_system.lower(),
                'collections': [
                    {{'name': c.name, 'object_count': len(c.objects)}}
                    for c in scene.collection.children
                ],
            }}

            print(json.dumps(result))
            """
        )
    )
```

Cleanup builder should use policy fields and perform real deletion, or better, delegate deletion to Object feature. Minimal corrected Blender-side skeleton:

```python
def build_cleanup_code(policy: SceneCleanupPolicyVO, dry_run: bool = False) -> PythonCode:
    return PythonCode(
        textwrap.dedent(
            f"""
            import bpy
            import json

            mode = {str(policy.mode)!r}
            dry_run = {dry_run!r}
            include_hidden = {policy.include_hidden_objects!r}
            preserve_cameras = {policy.preserve_cameras!r}
            preserve_lights = {policy.preserve_lights!r}
            protect_active_camera = {policy.protect_active_camera!r}
            protect_sole_camera = {policy.protect_sole_camera!r}

            scene = bpy.context.scene
            active_camera = scene.camera
            camera_count = sum(1 for o in scene.objects if o.type == 'CAMERA')

            removed_refs = []
            preserved_refs = []
            skipped_refs = []

            def matches_mode(obj):
                if mode == '{CLEANUP_MODE_ALL}':
                    return True
                if mode == '{CLEANUP_MODE_MESHES}':
                    return obj.type == 'MESH'
                if mode == '{CLEANUP_MODE_OBJECTS}':
                    return obj.type not in {{'CAMERA', 'LIGHT'}}
                return False

            def should_preserve(obj):
                if protect_active_camera and obj == active_camera:
                    return True
                if protect_sole_camera and obj.type == 'CAMERA' and camera_count == 1:
                    return True
                if preserve_cameras and obj.type == 'CAMERA':
                    return True
                if preserve_lights and obj.type == 'LIGHT':
                    return True
                if obj.get('protected', False):
                    return True
                return False

            candidates = []

            for obj in list(scene.objects):
                if not include_hidden and obj.hide_viewport:
                    skipped_refs.append(obj.name)
                    continue

                if not matches_mode(obj):
                    preserved_refs.append(obj.name)
                    continue

                if should_preserve(obj):
                    preserved_refs.append(obj.name)
                    continue

                candidates.append(obj)

            if not dry_run:
                for obj in candidates:
                    removed_refs.append(obj.name)
                    bpy.data.objects.remove(obj, do_unlink=True)
            else:
                removed_refs.extend(obj.name for obj in candidates)

            result = {{
                'removed_count': len(removed_refs),
                'preserved_count': len(preserved_refs),
                'skipped_count': len(skipped_refs),
                'removed_refs': removed_refs,
                'preserved_refs': preserved_refs,
                'skipped_refs': skipped_refs,
            }}

            print(json.dumps(result))
            """
        )
    )
```

---

### `modules/scene/src/root_scene_container.py`
Wire event emitter into capabilities.

```python
from __future__ import annotations

import threading

from modules.shared.src.gateway.contract_code_execution_protocol import (
    ICodeExecutionProtocol,
)
from modules.shared.src.scene.contract_scene_aggregate import ISceneAggregate


class SceneContainer:
    """Dependency injection container for scene feature."""

    def __init__(
        self,
        code_executor: ICodeExecutionProtocol,
        event_emitter: object | None = None,
    ) -> None:
        self._code_executor = code_executor
        self._event_emitter = event_emitter
        self._aggregate: ISceneAggregate | None = None
        self._lock = threading.Lock()

    def get_aggregate(self) -> ISceneAggregate:
        if self._aggregate is not None:
            return self._aggregate

        with self._lock:
            if self._aggregate is None:
                from .agent_scene_orchestrator import SceneOrchestrator
                from .capabilities_scene_cleanup_executor import SceneCleanupExecutor
                from .capabilities_scene_inspection_executor import SceneInspectionExecutor

                inspection = SceneInspectionExecutor(
                    code_executor=self._code_executor,
                    event_emitter=self._event_emitter,
                )
                cleanup = SceneCleanupExecutor(
                    code_executor=self._code_executor,
                    event_emitter=self._event_emitter,
                )

                self._aggregate = SceneOrchestrator(
                    inspection=inspection,
                    cleanup=cleanup,
                )

        return self._aggregate
```

---

### `modules/shared/src/scene/taxonomy_scene_vo.py`
Prefer immutable VO fields.

```python
@dataclass(frozen=True)
class SceneStateSummaryVO:
    scene_name: str = ""
    scene_identifier: SceneId = field(default_factory=lambda: SceneId(""))
    total_object_count: ObjectCount = field(default_factory=lambda: ObjectCount(0))
    visible_object_count: ObjectCount = field(default_factory=lambda: ObjectCount(0))
    hidden_object_count: ObjectCount = field(default_factory=lambda: ObjectCount(0))

    # Replace mutable dict with immutable tuple pairs.
    object_type_counts: tuple[tuple[ObjectType, ObjectCount], ...] = ()

    cameras: tuple[CameraInfoVO, ...] = ()
    lights: tuple[LightInfoVO, ...] = ()
    active_camera_name: ObjectName = field(default_factory=lambda: ObjectName(""))
    active_object_name: ObjectName = field(default_factory=lambda: ObjectName(""))
    render_engine: RenderEngine = field(default_factory=lambda: RenderEngine("CYCLES"))
    resolution_x: ResolutionX = field(default_factory=lambda: ResolutionX(1920))
    resolution_y: ResolutionY = field(default_factory=lambda: ResolutionY(1080))
    frame_start: int = 1
    frame_end: int = 250
    frame_step: int = 1
    unit_system: str = "METRIC"
    collection_count: ObjectCount = field(default_factory=lambda: ObjectCount(0))
    collections: tuple[CollectionSummaryVO, ...] = ()
    protected_object_summary: ProtectedObjectSummaryVO = field(default_factory=ProtectedObjectSummaryVO)

    # Replace mutable dict with immutable tuple pairs.
    capability_flags: tuple[tuple[str, bool], ...] = ()

    message: Prompt = field(default_factory=lambda: Prompt(""))
```