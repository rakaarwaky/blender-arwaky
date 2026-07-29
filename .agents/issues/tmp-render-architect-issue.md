# CRITICAL: Render module test suite reaches 28 passing tests but architecture has layering and FRD gaps

## Summary

The render module's test suite now reaches 28 passing tests covering FR-REN-001 (viewport capture), FR-REN-002 (scene image export), FR-REN-003 (HDRI config), FR-REN-004 (scene config), and FR-REN-005 (render execution). However, the production code has several architectural defects: render capabilities use hard-coded paths instead of taxonomy constants, viewport capture executor lacks FR-REN-001 completeness requirements (no event emission), and the module's taxonomy/contract layer is incomplete compared to other features like dispatcher and security. These issues should be addressed before the render feature can be considered production-ready.

## Findings by Category

### Layer Boundaries
| # | Severity | Issue | Location (File:Line) | Recommendation |
|---|----------|-------|----------------------|----------------|
| 1 | 🟡 WARNING | `ViewportCaptureExecutor` and `SceneImageExportExecutor` do not emit events for capture/export outcomes. FR-REN-001/002 require observability — capabilities should emit at least one event (e.g., `ViewportCaptureEvent`, `SceneImageExportEvent`) for each operation. | `modules/render/src/capabilities_viewport_capture_executor.py`, `capabilities_scene_image_export_executor.py` | Inject an event publisher and emit events with output path, frame number, resolution, and format. |
| 2 | 🟡 WARNING | `HDRISetupExecutor` and `SceneConfigSetupExecutor` accept `code_executor: Any = None`. This is the same pattern seen across multiple features — untyped dependencies reduce type safety and make testing harder. | `modules/render/src/capabilities_hdri_setup_executor.py:__init__`, `capabilities_scene_config_setup_executor.py:__init__` | Define a shared `ICodeExecutionProtocol` and type all capability constructors against it. |
| 3 | 🟢 INFO | `root_render_container.py` passes `None` for code_executor. This means render capabilities cannot execute Blender code in the current wiring. | `modules/render/src/root_render_container.py:wire` | Inject real `code_executor` (from gateway) into render capabilities. |

### Naming Convention
| # | Severity | Issue | Location (File:Line) | Recommendation |
|---|----------|-------|----------------------|----------------|
| 1 | 🟢 INFO | Render capability files use `_executor` suffix consistently, which is good. However, some shared taxonomy files use `_vo` suffix while others use `_event`. Inconsistency reduces discoverability. | `modules/shared/src/render/` | Standardize naming: VOs use `_vo`, events use `_event`, constants use `_constant`. |

### Dead Code / Orphan
| # | Severity | Issue | Location (File:Line) | Recommendation |
|---|----------|-------|----------------------|----------------|
| 1 | 🟡 WARNING | `taxonomy_render_event.py` exists but is never imported or emitted by any render capability. FR-REN-001/002 require observability events. | `modules/shared/src/render/taxonomy_render_event.py` | Use the event types in render capabilities, or remove them if not needed. |
| 2 | 🟢 INFO | `taxonomy_render_constant.py` contains default render settings (resolution, format, engine) but they are not used by render capabilities — each capability hard-codes its own defaults. | `modules/shared/src/render/taxonomy_render_constant.py` | Wire the constants into render capabilities, or remove unused constants. |

### Scalability & Coupling
| # | Severity | Issue | Location (File:Line) | Recommendation |
|---|----------|-------|----------------------|----------------|
| 1 | 🟡 WARNING | `RenderExecutor` contains hard-coded resolution/format defaults instead of using taxonomy constants or configuration. This violates the pattern seen in other features where catalog data belongs in taxonomy. | `modules/render/src/capabilities_render_executor.py` | Move render defaults to `taxonomy_render_constant.py`. Capabilities should depend on taxonomy/config, not hard-coded values. |
| 2 | 🟡 WARNING | No aggregate contract exists for render operations. Other features have `I*OperateAggregate` contracts; render lacks this abstraction. | N/A | Create `modules/shared/src/render/contract_render_operate_aggregate.py` with methods for capture, export, HDRI setup, scene config, and render execution. |

### Data Flow
| # | Severity | Issue | Location (File:Line) | Recommendation |
|---|----------|-------|----------------------|----------------|
| 1 | 🟡 WARNING | `i_RenderResultVO.output_path` defaults to empty string. If render fails, the VO doesn't express the partial output or failure state clearly. | `modules/shared/src/render/taxonomy_render_vo.py:i_RenderResultVO` | Add a `success: bool` field and `error_summary: str | None` to express partial/failed render outcomes. |
| 2 | 🟡 WARNING | HDRI setup uses hard-coded light strength (1.0) instead of configurable values from taxonomy/constants or config. | `modules/render/src/capabilities_hdri_setup_executor.py` | Use taxonomy constants for default HDRI light strength, or make it configurable via VO fields. |

## Violations
- **AES305** — Duplication risk: render defaults duplicated between `taxonomy_render_constant.py` and individual capabilities.
- **Potential AES405** — Agent role: render capabilities use `Any` for code_executor instead of a shared protocol.
- **FRD gap**: FR-REN-001/002 observability not fully satisfied — no event emission from viewport capture or scene image export capabilities.

## Action Items (For Developer)
- [ ] P0 Move render defaults from capabilities to `taxonomy_render_constant.py` and wire them into the executors.
- [ ] P0 Inject real `code_executor` into render capabilities in `root_render_container.py`.
- [ ] P1 Create `contract_render_operate_aggregate.py` with `IRenderOperateAggregate` interface.
- [ ] P1 Make `ViewportCaptureExecutor` and `SceneImageExportExecutor` emit events for each operation.
- [ ] P1 Add `success` and `error_summary` fields to `i_RenderResultVO`.
- [ ] P2 Use Blender API enums for render settings instead of string matching.

## Proposed Fixes / Reference Code

### 1. Wire real dependencies in root container

```python
# modules/render/src/root_render_container.py

class RenderContainer:
    def wire(self) -> None:
        if self._wired:
            return

        # Inject code_executor from gateway
        self._code_executor = GatewayContainer().agent  # or injected via DI

        # Inject event_publisher from diagnostics/events feature
        self._event_publisher = EventPublisher()

        capture_cap = ViewportCaptureExecutor(
            code_executor=self._code_executor,
            event_publisher=self._event_publisher,
        )

        export_cap = SceneImageExportExecutor(
            code_executor=self._code_executor,
            event_publisher=self._event_publisher,
        )

        hdri_cap = HDRISetupExecutor(
            code_executor=self._code_executor,
        )

        render_cap = RenderExecutor(
            code_executor=self._code_executor,
            event_publisher=self._event_publisher,
        )

        self._orchestrator = RenderOrchestrator(
            capture_cap=capture_cap,
            export_cap=export_cap,
            hdri_cap=hdri_cap,
            render_cap=render_cap,
        )

        self._wired = True
```

### 2. Emit events in viewport capture executor

```python
# modules/render/src/capabilities_viewport_capture_executor.py

class ViewportCaptureExecutor:
    def __init__(self, code_executor, event_publisher=None):
        self._executor = code_executor
        self._events = event_publisher

    async def capture_viewport(self, request) -> i_CaptureResultVO:
        result = await self._executor.execute_blender_code(
            Prompt(request.code),
            max_tokens=500,
        )

        output_path = self._extract_output_path(result)

        capture_result = i_CaptureResultVO(
            output_path=output_path,
            frame_number=request.frame_number,
            resolution=request.resolution,
            format=request.format,
        )

        if self._events is not None:
            from modules.shared.src.render.taxonomy_render_event import ViewportCaptureEvent
            self._events.publish(
                ViewportCaptureEvent(
                    output_path=output_path,
                    frame_number=request.frame_number,
                    resolution=request.resolution,
                    format=request.format,
                )
            )

        return capture_result
```

### 3. Clean up taxonomy constants

```python
# modules/shared/src/render/taxonomy_render_constant.py

"""Render domain constants — immutable defaults."""

from __future__ import annotations

# Default render settings
DEFAULT_RESOLUTION_X: int = 1920
DEFAULT_RESOLUTION_Y: int = 1080
DEFAULT_FORMAT: str = "PNG"
DEFAULT_RENDER_ENGINE: str = "CYCLE"
DEFAULT_HDRI_LIGHT_STRENGTH: float = 1.0

# Supported render formats
SUPPORTED_FORMATS: tuple[str, ...] = (
    "PNG",
    "JPEG",
    "TIFF",
    "EXR",
)

# Supported render engines
SUPPORTED_ENGINES: tuple[str, ...] = (
    "CYCLE",
    "EEVEE",
    "EEVEE_NEXT",
)
```
