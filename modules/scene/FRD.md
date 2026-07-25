# FRD — scene (Scene Feature Module)

## System Overview

The scene module manages Blender scene-level operations — information retrieval and cleanup. It provides the scene operate protocol and scene inspection capabilities. Orchestration is handled by the agent layer.

## Functional Requirements

### FR-SCN-001: Get Scene Info

- **Description**: Retrieve current scene state including all objects, render engine, and resolution
- **Input**: GetSceneInfoRequestVO (empty)
- **Output**: GetSceneInfoResponseVO (success, scene_info: SceneInfo, message)
- **Business Rules**: Returns full scene state; objects list includes all visible objects
- **Edge Cases**: Empty scene, no active object, missing render engine
- **Error Handling**: ConnectionError if Blender not connected

### FR-SCN-002: Cleanup Scene

- **Description**: Remove objects from scene based on cleanup mode
- **Input**: CleanupSceneRequestVO (mode: KEEP_CAMERA | KEEP_LIGHTS | REMOVE_ALL)
- **Output**: CleanupSceneResponseVO (success, objects_removed: int, message)
- **Business Rules**: Camera/light preservation based on mode; undo-able operation
- **Edge Cases**: Scene already empty, only camera/light remaining, linked objects
- **Error Handling**: SceneValidationError for invalid cleanup mode

## API Contract

| Operation | Input | Output | Description |
|-----------|-------|--------|-------------|
| `get_scene_info` | GetSceneInfoRequestVO | GetSceneInfoResponseVO | Get scene state |
| `cleanup_scene` | CleanupSceneRequestVO | CleanupSceneResponseVO | Remove objects |

## Integration Points

- **Internal**: shared (taxonomy VOs, contracts), server (Blender connection)
- **External**: Blender Python API (bpy) — via server module

## Non-functional Requirements

- Performance: Scene info retrieval within 1 second
- Reliability: Cleanup operations are atomic (all-or-nothing)

## Test Scenarios / QA Checklist

- [ ] Get scene info returns complete scene state
- [ ] Cleanup with KEEP_CAMERA preserves camera object
- [ ] Cleanup with REMOVE_ALL removes all objects

## Assumptions & Constraints

- Blender must be running with addon enabled

## Glossary

- **SceneInfo**: Value object containing full scene state
- **CleanupMode**: Enum for object preservation strategy

## Reference

- PRD: [../../PRD.md](../../PRD.md)
- FRD shared: [../shared/FRD.md](../shared/FRD.md)
