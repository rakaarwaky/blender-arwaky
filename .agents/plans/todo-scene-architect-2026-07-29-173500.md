# Review Plan: scene — Architect (Phase 1)

## Summary

The scene feature module (`modules/scene/`) follows AES layered architecture with 2 capabilities, 1 agent orchestrator, 1 surface command, 1 root container, and shared taxonomy/contract/utility files in `modules/shared/src/scene/`. The overall structure is sound — layer boundaries are respected, naming conventions are compliant, imports follow AES201 rules, and no orphan or circular-import issues were found. The primary findings concern test file size (755 lines vs 1000 limit), the `__init__.py` barrel file exposing capabilities directly instead of through aggregates, and a missing taxonomy constant VO for `SceneCleanupPolicyVO` that exists in the shared taxonomy but is duplicated as a local class in the capabilities layer.

## Findings by Category

### Layer Boundaries

| # | Severity | Issue | Location (File:Line) | Recommendation |
|---|----------|-------|----------------------|----------------|
| 1 | 🟡 WARNING | `modules/scene/src/__init__.py` exports `SceneCleanupExecutor` and `SceneInspectionExecutor` directly from capabilities layer. Per AES201 (sub-condition 7), capabilities should not be directly exported by barrel files — they should only expose the aggregate (`ISceneAggregate`) or surface entry points. This bypasses the abstraction boundary. | `modules/scene/src/__init__.py:15-18` | Remove direct capability exports from `__init__.py`. Export only `SceneOrchestrator`, `SceneContainer`, and factory functions. Surface layers should consume through `ISceneAggregate` aggregate, not capabilities directly. |
| 2 | 🟡 WARNING | `modules/scene/src/root_scene_container.py` imports from `modules.shared.src.gateway.contract_code_execution_protocol` (line 10). While root may depend on all layers, this creates a direct coupling between the scene container and gateway protocol. The dependency is valid per AES201 sub-condition 12 (root may import all layers), but should be verified that no other layer transitively depends on the scene container to avoid circular wiring. | `modules/scene/src/root_scene_container.py:10` | Verify no circular wiring through gateway → scene → gateway chain. If clean, leave as-is since root is allowed to import all layers. |
| 3 | 🟢 INFO | `modules/shared/src/scene/taxonomy_scene_vo.py` defines `SceneCleanupPolicyVO` (line 89) as a frozen dataclass in taxonomy, while `capabilities_scene_cleanup_executor.py` defines its own `SceneCleanupPolicy` class with nearly identical structure (lines 184-215). This creates two parallel representations of the same resolved policy concept. | `modules/shared/src/scene/taxonomy_scene_vo.py:89-97`, `modules/scene/src/capabilities_scene_cleanup_executor.py:184-215` | Consolidate to use only `SceneCleanupPolicyVO` from taxonomy. Remove the local `SceneCleanupPolicy` class and have the capability consume the taxonomy VO directly. |

### Naming Convention

| # | Severity | Issue | Location (File:Line) | Recommendation |
|---|----------|-------|----------------------|----------------|
| 4 | 🟢 INFO | `modules/scene/src/surface_scene_command.py` uses `_command` suffix which is allowed for smart surfaces per AES102. However, the file contains only delegation logic (2 methods) and no actual command handling or user-facing interaction. Consider whether this should be a utility surface (`_hook`) or if it serves a necessary surface boundary role. | `modules/scene/src/surface_scene_command.py` | If the surface is not called by any entry point, it may be an orphan per AES506. Verify it's wired into the MCP entry or CLI router. |

### Dead Code / Orphan

| # | Severity | Issue | Location (File:Line) | Recommendation |
|---|----------|-------|----------------------|----------------|
| 5 | 🟢 INFO | `modules/scene/tests/test_scene_inspection.py` is 755 lines and contains inline mock executors (`MockCodeExecutor`, `EmptyExecutor`, etc.) defined within test functions. While not dead code, this inflates the test file and makes individual tests harder to maintain. The test file approaches the AES301 threshold (1000 lines). | `modules/scene/tests/test_scene_inspection.py:1-755` | Extract mock executors into a separate `modules/scene/tests/fixtures.py` or use pytest fixtures with `@pytest.fixture` for reusable mocks. This keeps the test file under 600 lines and improves reusability. |
| 6 | 🟢 INFO | `modules/scene/src/surface_scene_command.py` is not imported by any entry point (MCP, CLI, or dispatcher). Checking import graph: no file in `modules/mcp/`, `modules/cli/`, or `modules/dispatcher/` imports `surface_scene_command`. Per AES506, smart surfaces must be imported by entry/router. | `modules/scene/src/surface_scene_command.py` | Either wire the surface into an entry point (e.g., MCP handler in `modules/mcp/`) or remove if not needed. If it's a future-facing API contract, add a comment noting its intended consumer. |

### Scalability & Coupling

| # | Severity | Issue | Location (File:Line) | Recommendation |
|---|----------|-------|----------------------|----------------|
| 7 | 🟢 INFO | `modules/shared/src/scene/utility_scene_code_builder.py` generates Blender Python code as inline f-strings. While this satisfies the utility layer's requirement for stateless functions, the generated code is tightly coupled to Blender's specific API (`bpy.context`, `bpy.data`). If the system needs to support other 3D applications (e.g., Godot, Three.js), the code builder would need complete rewrites. | `modules/shared/src/scene/utility_scene_code_builder.py:1-275` | Consider abstracting the generated code into a template format (e.g., Jinja2 or a domain-specific DSL) that can be compiled to different target languages. This is a forward-looking scalability concern, not a current blocker. |
| 8 | 🟢 INFO | `capabilities_scene_cleanup_executor.py` imports `SceneCleanupPolicy` from within its own file scope (line 65) and uses it as a local class. This couples the capability to its own internal definition rather than a shared contract. If other capabilities or agents need to reason about cleanup policy, they would need to duplicate the logic. | `modules/scene/src/capabilities_scene_cleanup_executor.py:65` | Move `SceneCleanupPolicy` (or reuse `SceneCleanupPolicyVO`) to the taxonomy layer as a resolved policy VO, making it available for cross-capability reuse. |

### Data Flow

| # | Severity | Issue | Location (File:Line) | Recommendation |
|---|----------|-------|----------------------|----------------|
| 9 | 🟢 INFO | Data flow is correctly unidirectional bottom-up: taxonomy → contract → utility → capabilities → agent → surface → root. No cycles detected. The `__init__.py` barrel file's lazy-loading pattern for `SceneContainer` (via `__getattr__`) prevents circular imports but adds runtime overhead on first access. | `modules/scene/src/__init__.py:20-28` | The lazy-loading is a valid workaround for circular surface↔root imports. Leave as-is; the runtime overhead is negligible for container creation (one-time cost). |

## Violations

- **AES506 (HIGH)**: `surface_scene_command.py` — smart surface not imported by any entry point or router. May be an orphan if not wired into MCP/CLI dispatch.
- **AES201 sub-condition 7 (WARNING)**: `__init__.py` exports capabilities directly instead of through aggregates, bypassing the abstraction boundary.

## Action Items

- [ ] P1 Wire `surface_scene_command.py` into an entry point (MCP handler) or document as future-facing API contract
- [ ] P2 Remove direct capability exports from `modules/scene/src/__init__.py`; export only aggregate and container
- [ ] P3 Consolidate duplicate `SceneCleanupPolicy` — use `SceneCleanupPolicyVO` from taxonomy instead of local class in capabilities
- [ ] P4 Extract mock executors from `test_scene_inspection.py` into pytest fixtures for better test organization

## Fixed Code

### `modules/scene/src/__init__.py` — Remove direct capability exports

```python
# BEFORE (lines 13-18):
from .agent_scene_orchestrator import SceneOrchestrator
from .capabilities_scene_cleanup_executor import SceneCleanupExecutor
from .capabilities_scene_inspection_executor import SceneInspectionExecutor

__all__ = [
    "SceneOrchestrator",
    "SceneCleanupExecutor",
    "SceneInspectionExecutor",
    "SceneContainer",
    "create_scene_container",
]

# AFTER:
from .agent_scene_orchestrator import SceneOrchestrator

__all__ = [
    "SceneOrchestrator",
    "SceneContainer",
    "create_scene_container",
]


def __getattr__(name: str):
    """Lazy-load root module to break circular surface↔root import chain."""
    if name in ("SceneContainer", "create_scene_container"):
        from .root_scene_container import SceneContainer as _SceneContainer
        from .root_scene_container import create_scene_container as _create_scene_container
        if name == "SceneContainer":
            return _SceneContainer
        return _create_scene_container
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
```

### `modules/scene/src/capabilities_scene_cleanup_executor.py` — Use taxonomy VO instead of local policy class

```python
# BEFORE (lines 184-215, local SceneCleanupPolicy class):
class SceneCleanupPolicy:
    """Frozen data carrier for resolved cleanup policy.

    Extracted from executor to satisfy SRP — contains no I/O or business logic
    beyond simple data resolution from request VOs.
    """

    def __init__(
        self,
        mode: str,
        preserve_cameras: bool,
        preserve_lights: bool,
        include_hidden_objects: bool,
        child_handling_policy: str,
        dependent_handling_policy: str,
        protect_active_camera: bool,
        protect_sole_camera: bool,
    ) -> None:
        self.mode = mode
        ...

    @classmethod
    def from_request(cls, request: SceneCleanupVO) -> SceneCleanupPolicy:
        """Resolve policy from cleanup request."""
        preservation = set(request.preservation_list)
        return cls(...)
        ...

# AFTER — import and use the taxonomy VO directly (no local class needed):
# SceneCleanupPolicyVO is already imported from modules.shared.src.scene.taxonomy_scene_vo
# The capability should consume it directly instead of building its own policy class.
```

**Note**: This requires updating `build_cleanup_code()` utility to accept `SceneCleanupPolicyVO` directly (it already does, per line 108 of `utility_scene_code_builder.py`). The local `SceneCleanupPolicy.from_request()` should be replaced with a simple VO construction in the capability or extracted as a factory function in the taxonomy layer.

### `modules/scene/src/surface_scene_command.py` — Wire into MCP entry point

```python
# ADD to modules/mcp/src/capabilities_mcp_bootstrap.py (or relevant MCP handler):

from modules.scene.src.surface_scene_command import SceneCommand, ISceneAggregate

# In the MCP handler registration:
def register_scene_handlers(server: mcp.Server):
    """Register scene feature handlers."""
    aggregate = get_scene_aggregate()  # from container
    command = SceneCommand(aggregate)

    @server.tool()
    async def inspect_scene(request: dict) -> str:
        vo = SceneInspectionVO(**request)
        result = await command.inspect(vo)
        return result.model_dump_json()

    @server.tool()
    async def cleanup_scene(request: dict) -> str:
        vo = SceneCleanupVO(**request)
        result = await command.cleanup(vo)
        return result.model_dump_json()
```

**Note**: If MCP already has scene handlers through a different path, this step can be deferred. The surface file should either be wired or documented as intentionally unused (e.g., "reserved for REST API future").