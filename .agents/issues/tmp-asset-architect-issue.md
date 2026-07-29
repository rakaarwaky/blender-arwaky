# CRITICAL: Asset module test suite reaches 20 passing tests but architecture has layering and FRD gaps

## Summary

The asset module's test suite now reaches 20 passing tests covering FR-ASSET-001 (GLB import), FR-ASSET-002 (GLTF export), FR-ASSET-003 (OBJ import), FR-ASSET-004 (STL export), and FR-ASSET-005 (file info). However, the production code has several architectural defects: asset capabilities use hard-coded paths instead of taxonomy constants, GLB import executor lacks FR-ASSET-001 completeness requirements (no event emission), and the module's taxonomy/contract layer is incomplete compared to other features like dispatcher and security. These issues should be addressed before the asset feature can be considered production-ready.

## Findings by Category

### Layer Boundaries
| # | Severity | Issue | Location (File:Line) | Recommendation |
|---|----------|-------|----------------------|----------------|
| 1 | 🟡 WARNING | `GLBImportExecutor` and `OBJImportExecutor` do not emit events for import outcomes. FR-ASSET-001/003 require observability — capabilities should emit at least one event (e.g., `AssetImportEvent`) for each operation. | `modules/asset/src/capabilities_glb_import_executor.py`, `capabilities_obj_import_executor.py` | Inject an event publisher and emit events with asset name, file path, object count, and material count. |
| 2 | 🟡 WARNING | `GLTFExportExecutor` and `STLExportExecutor` accept `code_executor: Any = None`. This is the same pattern seen across multiple features — untyped dependencies reduce type safety and make testing harder. | `modules/asset/src/capabilities_gltf_export_executor.py:__init__`, `capabilities_stl_export_executor.py:__init__` | Define a shared `ICodeExecutionProtocol` and type all capability constructors against it. |
| 3 | 🟢 INFO | `root_asset_container.py` passes `None` for code_executor. This means asset capabilities cannot execute Blender code in the current wiring. | `modules/asset/src/root_asset_container.py:wire` | Inject real `code_executor` (from gateway) into asset capabilities. |

### Naming Convention
| # | Severity | Issue | Location (File:Line) | Recommendation |
|---|----------|-------|----------------------|----------------|
| 1 | 🟢 INFO | Asset capability files use `_executor` suffix consistently, which is good. However, some shared taxonomy files use `_vo` suffix while others use `_event`. Inconsistency reduces discoverability. | `modules/shared/src/asset/` | Standardize naming: VOs use `_vo`, events use `_event`, constants use `_constant`. |

### Dead Code / Orphan
| # | Severity | Issue | Location (File:Line) | Recommendation |
|---|----------|-------|----------------------|----------------|
| 1 | 🟡 WARNING | `taxonomy_asset_event.py` exists but is never imported or emitted by any asset capability. FR-ASSET-001/003 require observability events. | `modules/shared/src/asset/taxonomy_asset_event.py` | Use the event types in asset capabilities, or remove them if not needed. |
| 2 | 🟢 INFO | `taxonomy_asset_constant.py` contains default import/export settings (merge_objects, apply_modifiers, include_types) but they are not used by asset capabilities — each capability hard-codes its own defaults. | `modules/shared/src/asset/taxonomy_asset_constant.py` | Wire the constants into asset capabilities, or remove unused constants. |

### Scalability & Coupling
| # | Severity | Issue | Location (File:Line) | Recommendation |
|---|----------|-------|----------------------|----------------|
| 1 | 🟡 WARNING | `GLBImportExecutor` contains hard-coded import defaults (`merge_objects=True`, `apply_modifiers=False`) instead of using taxonomy constants or configuration. This violates the pattern seen in other features where catalog data belongs in taxonomy. | `modules/asset/src/capabilities_glb_import_executor.py` | Move import defaults to `taxonomy_asset_constant.py`. Capabilities should depend on taxonomy/config, not hard-coded values. |
| 2 | 🟡 WARNING | No aggregate contract exists for asset operations. Other features have `I*OperateAggregate` contracts; asset lacks this abstraction. | N/A | Create `modules/shared/src/asset/contract_asset_operate_aggregate.py` with methods for import, export, and file info operations. |

### Data Flow
| # | Severity | Issue | Location (File:Line) | Recommendation |
|---|----------|-------|----------------------|----------------|
| 1 | 🟡 WARNING | `i_AssetImportResultVO.object_count` defaults to `0`. If import fails, the VO doesn't express the partial import or failure state clearly. | `modules/shared/src/asset/taxonomy_asset_vo.py:i_AssetImportResultVO` | Add a `success: bool` field and `error_summary: str | None` to express partial/failed import outcomes. |
| 2 | 🟡 WARNING | File info capability assumes all file types have `file_size_bytes`. This may not be true for all file formats or network sources. | `modules/asset/src/capabilities_file_info_executor.py` | Make `file_size_bytes` optional in the VO and handle missing size gracefully. |

## Violations
- **AES305** — Duplication risk: import/export defaults duplicated between `taxonomy_asset_constant.py` and individual capabilities.
- **Potential AES405** — Agent role: asset capabilities use `Any` for code_executor instead of a shared protocol.
- **FRD gap**: FR-ASSET-001/003 observability not fully satisfied — no event emission from GLB/OBJ import capabilities.

## Action Items (For Developer)
- [ ] P0 Move import/export defaults from capabilities to `taxonomy_asset_constant.py` and wire them into the executors.
- [ ] P0 Inject real `code_executor` into asset capabilities in `root_asset_container.py`.
- [ ] P1 Create `contract_asset_operate_aggregate.py` with `IAssetOperateAggregate` interface.
- [ ] P1 Make `GLBImportExecutor` and `OBJImportExecutor` emit events for each import operation.
- [ ] P1 Add `success` and `error_summary` fields to `i_AssetImportResultVO`.
- [ ] P2 Use Blender API enums for import/export settings instead of string matching.

## Proposed Fixes / Reference Code

### 1. Wire real dependencies in root container

```python
# modules/asset/src/root_asset_container.py

class AssetContainer:
    def wire(self) -> None:
        if self._wired:
            return

        # Inject code_executor from gateway
        self._code_executor = GatewayContainer().agent  # or injected via DI

        # Inject event_publisher from diagnostics/events feature
        self._event_publisher = EventPublisher()

        import_cap = GLBImportExecutor(
            code_executor=self._code_executor,
            event_publisher=self._event_publisher,
        )

        export_cap = GLTFExportExecutor(
            code_executor=self._code_executor,
            event_publisher=self._event_publisher,
        )

        self._orchestrator = AssetOrchestrator(
            import_cap=import_cap,
            export_cap=export_cap,
        )

        self._wired = True
```

### 2. Emit events in GLB import executor

```python
# modules/asset/src/capabilities_glb_import_executor.py

class GLBImportExecutor:
    def __init__(self, code_executor, event_publisher=None):
        self._executor = code_executor
        self._events = event_publisher

    async def import_glb(self, request) -> i_AssetImportResultVO:
        result = await self._executor.execute_blender_code(
            Prompt(request.code),
            max_tokens=500,
        )

        asset_name = self._extract_asset_name(result)

        import_result = i_AssetImportResultVO(
            asset_name=asset_name,
            file_path=request.file_path,
            object_count=result.object_count,
            material_count=result.material_count,
        )

        if self._events is not None:
            from modules.shared.src.asset.taxonomy_asset_event import AssetImportEvent
            self._events.publish(
                AssetImportEvent(
                    asset_name=asset_name,
                    file_path=request.file_path,
                    object_count=result.object_count,
                    material_count=result.material_count,
                )
            )

        return import_result
```

### 3. Clean up taxonomy constants

```python
# modules/shared/src/asset/taxonomy_asset_constant.py

"""Asset domain constants — immutable defaults."""

from __future__ import annotations

# Default import settings
DEFAULT_MERGE_OBJECTS: bool = True
DEFAULT_APPLY_MODIFIERS: bool = False
DEFAULT_INCLUDE_TYPES: tuple[str, ...] = ("MESH", "CAMERA", "LIGHT", "EMPTY")

# Default export settings
DEFAULT_SELECTED_ONLY: bool = False
DEFAULT_CODEC: str = "ZIP"
DEFAULT_MAX_TREE_DEPTH: int = 1024

# Supported file formats
SUPPORTED_IMPORT_FORMATS: tuple[str, ...] = (
    "GLB",
    "GLTF",
    "OBJ",
    "STL",
)

SUPPORTED_EXPORT_FORMATS: tuple[str, ...] = (
    "GLTF",
    "GLB",
    "OBJ",
    "STL",
)
```
