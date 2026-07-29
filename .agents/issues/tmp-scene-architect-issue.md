# CRITICAL: Scene module test suite reaches 28 passing tests but architecture has layering and FRD gaps

## Summary

The scene module's test suite now reaches 28 passing tests covering FR-SCN-001 (scene inspection), with comprehensive coverage of i_InspectionResultVO, i_SceneInfoVO, CleanupMode, DeleteMode, ProtectionLevel, and i_CleanupResultVO. However, the production code has several architectural defects: scene cleanup executor uses hard-coded protection lists instead of taxonomy constants, inspection capability lacks FR-SCN-001 observability requirements (no event emission), and the module's taxonomy/contract layer is incomplete compared to other features like dispatcher and security. These issues should be addressed before the scene feature can be considered production-ready.

## Findings by Category

### Layer Boundaries
| # | Severity | Issue | Location (File:Line) | Recommendation |
|---|----------|-------|----------------------|----------------|
| 1 | 🟡 WARNING | `SceneCleanupExecutor` contains hard-coded protection lists (`PROTECTED_CATEGORIES`, `PROTECTED_OBJECTS`) instead of using taxonomy constants or configuration. This violates the pattern seen in other features where catalog data belongs in taxonomy. | `modules/scene/src/capabilities_scene_cleanup_executor.py:PROTECTED_CATEGORIES, PROTECTED_OBJECTS` | Move protection lists to `taxonomy_scene_constant.py` as immutable constants. Capabilities should depend on taxonomy/config, not hard-coded values. |
| 2 | 🟡 WARNING | `SceneInspectionCapability` does not emit events for inspection outcomes. FR-SCN-001 requires observability — the capability should emit at least one event (e.g., `SceneInspectionEvent`) for each inspection operation. | `modules/scene/src/capabilities_scene_inspection.py:inspect_scene` | Inject an event publisher and emit `SceneInspectionEvent` with summary counts, frame range, resolution, render engine, and object type distribution. |
| 3 | 🟢 INFO | `root_scene_container.py` passes `None` for code_executor and event_publisher. This means scene capabilities cannot execute Blender code or emit events in the current wiring. | `modules/scene/src/root_scene_container.py:wire` | Inject real `code_executor` (from gateway) and `event_publisher` (from diagnostics/events feature) into scene capabilities. |

### Naming Convention
| # | Severity | Issue | Location (File:Line) | Recommendation |
|---|----------|-------|----------------------|----------------|
| 1 | 🟢 INFO | `SceneCleanupExecutor` and `SceneInspectionCapability` use different role suffixes (`Executor` vs `Capability`). Inconsistent naming reduces discoverability. | `modules/scene/src/capabilities_scene_cleanup_executor.py`, `capabilities_scene_inspection.py` | Standardize on one role suffix pattern, e.g., all `_executor` or all `_capability`. |

### Dead Code / Orphan
| # | Severity | Issue | Location (File:Line) | Recommendation |
|---|----------|-------|----------------------|----------------|
| 1 | 🟡 WARNING | `taxonomy_scene_event.py` exists but is never imported or emitted by any scene capability. FR-SCN-001 requires observability events. | `modules/shared/src/scene/taxonomy_scene_event.py` | Use the event types in `SceneInspectionCapability` and `SceneCleanupExecutor`, or remove them if not needed. |
| 2 | 🟢 INFO | `taxonomy_scene_constant.py` contains `DEFAULT_PROTECTION_LEVELS` and `DEFAULT_PROTECTED_OBJECTS` but they are not used by `SceneCleanupExecutor`. | `modules/shared/src/scene/taxonomy_scene_constant.py` | Wire the constants into the cleanup executor, or remove unused constants. |

### Scalability & Coupling
| # | Severity | Issue | Location (File:Line) | Recommendation |
|---|----------|-------|----------------------|----------------|
| 1 | 🟡 WARNING | `SceneCleanupExecutor._check_protection()` uses string matching (`"Camera"` in obj.type, `"Camera"` in obj.name). This is fragile and doesn't handle Blender API changes. | `modules/scene/src/capabilities_scene_cleanup_executor.py:_check_protection` | Use Blender API enums where available, or define version-agnostic protection criteria in taxonomy/constants. |
| 2 | 🟡 WARNING | Scene capabilities accept `code_executor: Any = None`. This is the same pattern seen in object/gateway features — untyped dependencies reduce type safety. | `modules/scene/src/capabilities_scene_cleanup_executor.py:__init__`, `capabilities_scene_inspection.py:__init__` | Define a shared `ICodeExecutionProtocol` and type all capability constructors against it. |
| 3 | 🟡 WARNING | No aggregate contract exists for scene operations. Other features have `I*OperateAggregate` contracts; scene lacks this abstraction. | N/A | Create `modules/shared/src/scene/contract_scene_operate_aggregate.py` with methods for cleanup, inspection, and future operations. |

### Data Flow
| # | Severity | Issue | Location (File:Line) | Recommendation |
|---|----------|-------|----------------------|----------------|
| 1 | 🟡 WARNING | `i_SceneInfoVO.frame_range` uses `[0, 250]` as default. This is a magic number and should be configurable or sourced from scene metadata. | `modules/shared/src/scene/taxonomy_scene_vo.py:i_SceneInfoVO` | Use taxonomy constants for default frame ranges, or make the field optional and computed from actual scene data. |
| 2 | 🟡 WARNING | `i_CleanupResultVO.objects_deleted` defaults to `0`. If cleanup encounters errors, the VO doesn't express partial success or failure state. | `modules/shared/src/scene/taxonomy_scene_vo.py:i_CleanupResultVO` | Add a `success: bool` field and `error_summary: str | None` to express partial/failed cleanup outcomes. |

## Violations
- **AES305** — Duplication risk: protection lists duplicated between `taxonomy_scene_constant.py` and `SceneCleanupExecutor`.
- **Potential AES405** — Agent role: scene capabilities use `Any` for code_executor instead of a shared protocol.
- **FRD gap**: FR-SCN-001 observability not fully satisfied — no event emission from inspection capability.

## Action Items (For Developer)
- [ ] P0 Move protection lists from `SceneCleanupExecutor` to `taxonomy_scene_constant.py` and wire them into the executor.
- [ ] P0 Inject real `code_executor` and `event_publisher` into scene capabilities in `root_scene_container.py`.
- [ ] P1 Create `contract_scene_operate_aggregate.py` with `ISceneOperateAggregate` interface.
- [ ] P1 Make `SceneInspectionCapability` emit `SceneInspectionEvent` for each inspection operation.
- [ ] P1 Add `success` and `error_summary` fields to `i_CleanupResultVO`.
- [ ] P2 Standardize capability role naming (all `_executor` or all `_capability`).
- [ ] P2 Use Blender API enums for protection checks instead of string matching.

## Proposed Fixes / Reference Code

### 1. Wire real dependencies in root container

```python
# modules/scene/src/root_scene_container.py

class SceneContainer:
    def wire(self) -> None:
        if self._wired:
            return

        # Inject code_executor from gateway
        self._code_executor = GatewayContainer().agent  # or injected via DI

        # Inject event_publisher from diagnostics/events feature
        self._event_publisher = EventPublisher()

        cleanup_cap = SceneCleanupExecutor(
            code_executor=self._code_executor,
            protection_level=ProtectionLevel.STANDARD,
        )

        inspection_cap = SceneInspectionCapability(
            code_executor=self._code_executor,
            event_publisher=self._event_publisher,
        )

        self._orchestrator = SceneOrchestrator(
            cleanup_cap=cleanup_cap,
            inspection_cap=inspection_cap,
        )

        self._wired = True
```

### 2. Emit events in inspection capability

```python
# modules/scene/src/capabilities_scene_inspection.py

class SceneInspectionCapability:
    def __init__(self, code_executor, event_publisher=None):
        self._executor = code_executor
        self._events = event_publisher

    async def inspect_scene(self, request) -> i_InspectionResultVO:
        result = await self._executor.execute_blender_code(
            Prompt(request.code),
            max_tokens=500,
        )

        summary = self._parse_summary(result)

        inspection_result = i_InspectionResultVO(
            scene_info=i_SceneInfoVO(...),
            object_counts=summary.object_counts,
            frame_range=summary.frame_range,
            resolution=summary.resolution,
            render_engine=summary.render_engine,
        )

        if self._events is not None:
            from modules.shared.src.scene.taxonomy_scene_event import SceneInspectionEvent
            self._events.publish(
                SceneInspectionEvent(
                    object_counts=summary.object_counts,
                    frame_range=summary.frame_range,
                    resolution=summary.resolution,
                    render_engine=summary.render_engine,
                )
            )

        return inspection_result
```

### 3. Clean up taxonomy constants

```python
# modules/shared/src/scene/taxonomy_scene_constant.py

"""Scene domain constants — immutable defaults."""

from __future__ import annotations

from .taxonomy_scene_vo import ProtectionLevel

# Default protection levels (overridable via config)
DEFAULT_PROTECTION_LEVELS: list[ProtectionLevel] = [
    ProtectionLevel.CAMERA,
    ProtectionLevel.LIGHT,
    ProtectionLevel.CAMERA_AND_LIGHT,
]

# Default protected objects (immutable by convention)
DEFAULT_PROTECTED_OBJECTS: tuple[str, ...] = (
    "Camera",
    "Light",
    "World",
    "SceneCollection",
)
```
