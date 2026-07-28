# Review Plan: scene — Architect

## Summary

The scene feature module (`modules/scene/`) follows the AES layered architecture with Agent (SceneOrchestrator), Capabilities (SceneInspectionExecutor, SceneCleanupExecutor), and Root (SceneContainer) layers well implemented. Two findings are flagged: a **missing surface layer** that breaks the 7-layer vertical slice pattern, and **hardcoded logger names** (`"BlenderMCPServer"`) instead of `__name__` in both capability files. The Agent layer is functionally orphaned from a Surface consumer (Surface layer absent), and the `__init__.py` docstring omits the Surface layer reference. No critical AES layering violations or security issues detected.

## Findings by Category

### Layer Boundaries
| # | Severity | Issue | Location (File:Line) | Recommendation |
|---|----------|-------|----------------------|----------------|
| 1 | 🟡 WARNING | Missing surface layer breaks the 7-layer vertical slice. No `surface_scene_*.py` file exists despite ARCHITECTURE.md mandating `surface_<concern>_<role>.py`. | `modules/scene/src/` (all files) | Add a `surface_scene_router.py` file that exposes the feature's public API. Surface should be the entry point consumed by Root or external callers, insulating Agent from direct external references. |
| 2 | 🟡 WARNING | Root layer (`root_scene_container.py`) imports gateway contract `ICodeExecutionProtocol` from `modules.shared.src.gateway`. This is a cross-feature dependency that could create a coupling between scene and gateway features at the Root composition level. | `root_scene_container.py:5` | Acceptable for now since gateway is a shared infrastructure contract, but note as a latent coupling risk if gateway feature is ever split out. |

### Naming Convention
| # | Severity | Issue | Location (File:Line) | Recommendation |
|---|----------|-------|----------------------|----------------|
| 3 | 🟢 INFO | All member files comply with `prefix_concern_suffix` naming: `agent_scene_orchestrator`, `capabilities_scene_inspection_executor`, `capabilities_scene_cleanup_executor`, `root_scene_container`. All 3+ words, lowercase, underscore-separated. | All files | No action needed. |

### Dead Code / Orphan
| # | Severity | Issue | Location (File:Line) | Recommendation |
|---|----------|-------|----------------------|----------------|
| 4 | 🟡 WARNING | Agent Orphan risk (AES505): `SceneOrchestrator` in the Agent layer is not called by any Surface file. The only consumer is `SceneContainer` (Root layer), which skips the Surface layer entirely. This means Surface-to-Agent traceability is broken. | `agent_scene_orchestrator.py` — unreachable from any surface file | Either add a Surface layer file that calls `SceneOrchestrator`, or document that Root directly orchestrates Agent (deviation from standard AES). |
| 5 | 🟢 INFO | Utility layer files (`utility_scene_code_builder.py`, `utility_scene_result_parser.py`) live in `modules/shared/src/scene/`, not in the feature's own `src/`. This is by design (shared cross-cutting code), but means the feature does not own its utility layer. | `modules/shared/src/scene/utility_scene_code_builder.py` (and _parser) | No action needed; this is the expected pattern for shared utilities per AES spec. |

### Scalability & Coupling
| # | Severity | Issue | Location (File:Line) | Recommendation |
|---|----------|-------|----------------------|----------------|
| 6 | 🟢 INFO | `SceneOrchestrator` has only 2 methods (`get_scene_info`, `cleanup_scene`), which is appropriate for its current scope. As the feature grows with additional FRDs (e.g., scene transform, scene snapshot), the orchestrator could grow. Consider splitting into sub-orchestrators if it exceeds 5 methods. | `agent_scene_orchestrator.py` | Monitor — no action needed now. |

### Data Flow
| # | Severity | Issue | Location (File:Line) | Recommendation |
|---|----------|-------|----------------------|----------------|
| 7 | 🟢 INFO | Data flow is correctly unidirectional bottom-up: Taxonomy → Contract → Utility → Capabilities → Agent → Root. No cycles detected. | All files | No action needed. |

## Violations

- **AES401 (Taxonomy Role)**: No violation. Taxonomy files in `shared/src/scene/` contain only VOs, constants, errors, and events.
- **AES403 (Capabilities Role)**: No violation. Both capabilities implement their protocols and stay within 3 type declarations (class + dunder + constructor methods count as one type).
- **AES405 (Agent Role)**: No violation. `SceneOrchestrator` has an aggregate implementation (delegates to capabilities), uses no `Any` annotations, and has 2 methods (well within limits).
- **AES505 (Agent Orphan)**: 🟡 WARNING — Agent (`SceneOrchestrator`) has no Surface consumer. Only Root (`SceneContainer`) imports it. Per AES505, a Surface file should import the Agent.
- **AES101/AES102 (Naming)**: No violation. All files follow the naming convention.
- **AES201 (Forbidden Import)**: No violation. No cross-layer forbidden imports detected.

## Action Items

- [ ] HIGH Add `surface_scene_router.py` to `modules/scene/src/` following the `surface_<concern>_rolle.py` naming convention (AES101), implementing the public surface API that calls `SceneOrchestrator` (AES405 — fix Agent Orphan)
- [ ] MEDIUM Replace hardcoded `logging.getLogger("BlenderMCPServer")` with `logging.getLogger(__name__)` in both `capabilities_scene_inspection_executor.py` and `capabilities_scene_cleanup_executor.py` for proper logger naming (convention improvement)
- [ ] LOW Update `modules/scene/src/__init__.py` docstring to include the planned Surface layer entry

## Fixed Code

### Proposed: `modules/scene/src/surface_scene_router.py`

```python
"""Surface: Scene router.

Public entry point for scene feature operations.
Delegates to SceneOrchestrator (Agent layer).
"""

from __future__ import annotations

from modules.scene.src.agent_scene_orchestrator import SceneOrchestrator
from modules.scene.src.taxonomy_scene_vo import SceneInspectionVO, SceneCleanupVO


class SceneRouter:
    """Surface router exposing scene operations to external callers."""

    # ─── Block 1: definition + constructor ─────────────
    def __init__(self, orchestrator: SceneOrchestrator) -> None:
        self._orchestrator = orchestrator

    # ─── Block 2: surface methods only ──────────────
    async def inspect(self, request: SceneInspectionVO) -> SceneInspectionVO:
        """Public inspection API — delegates to orchestrator."""
        return await self._orchestrator.get_scene_info(request)

    async def cleanup(self, request: SceneCleanupVO) -> SceneCleanupVO:
        """Public cleanup API — delegates to orchestrator."""
        return await self._orchestrator.cleanup_scene(request)

    # ─── Block 3: dunders / factories / helpers ───────────────
    def __repr__(self) -> str:
        return "SceneRouter()"
```

### Proposed: Replace hardcoded logger names

In `capabilities_scene_inspection_executor.py`:
```python
# Before:
logger = logging.getLogger("BlenderMCPServer")
# After:
logger = logging.getLogger(__name__)
```

In `capabilities_scene_cleanup_executor.py`:
```python
# Before:
logger = logging.getLogger("BlenderMCPServer")
# After:
logger = logging.getLogger(__name__)
```
