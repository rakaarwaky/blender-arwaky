
# FRD — scene (Scene Feature Module)

## System Overview

The scene module manages Blender scene-level operations for **blender-arwaky**, primarily scene information retrieval and scene cleanup. It provides a scene operation contract and scene inspection capabilities. Higher-level orchestration, such as multi-step scene composition or AI-guided workflows, is handled by the agent layer or workflow module.

This module is responsible for translating scene-level intents into validated Blender-side operations. It inspects scene state, summarizes objects and render settings, and performs controlled cleanup operations with preservation policies. Actual execution against Blender is delegated to the server module through the Blender scripting interface.

The module covers:

- retrieving current scene state
- summarizing objects, cameras, lights, render settings, and scene metadata
- cleaning up scene objects based on preservation mode
- protecting important scene objects during cleanup
- reporting cleanup results deterministically
- supporting safe destructive operations through confirmation and undo-aware behavior

The module does not handle:

- object creation or transformation, which belongs to object module
- rendering or viewport capture, which belongs to render module
- asset discovery or import, which belongs to asset module
- network communication with Blender, which belongs to server module

## Functional Requirements

### FR-SCN-001: Get Scene Info

- **Description**: Retrieve current scene state including objects, active camera, render engine, resolution, and scene metadata
- **Input**: Scene information request concept containing optional detail level, optional object filter, and optional inclusion flag for hidden objects
- **Output**: Scene information result concept containing success indicator, scene state representation, and message
- **Business Rules**:
  - Returns full scene state or summarized scene state depending on requested detail level
  - Scene state representation should include at least:
    - scene name or scene identifier
    - object list
    - active object reference
    - active camera reference
    - light summary
    - camera summary
    - render engine information
    - resolution settings
    - sample count when available
    - frame range
    - frame rate
    - unit system
    - world or environment summary
    - collection summary
  - Object list includes all visible objects by default
  - Hidden objects may be included when explicitly requested
  - Object entries should include lightweight object metadata such as:
    - object name
    - unique object reference when available
    - object type
    - visibility state
    - transform summary
    - parent reference when available
    - collection membership summary
  - Read-only operation must not mutate scene state
  - Operation must be idempotent
  - Missing active object or active camera should be represented as empty reference, not as failure
  - Missing or unavailable render engine information should be represented as unknown or unavailable, not as fatal error
  - Large scenes should support summarized detail level to avoid oversized response
  - Response must serialize safely and avoid cyclic references
  - Response may include capability flags indicating supported scene operations
  - Object ordering should be deterministic, for example by name or by scene order
- **Edge Cases**: Empty scene, no active object, no active camera, missing render engine, large scene with many objects, hidden objects, linked collections, instanced objects, protected objects, stale object references, serialization limit, Blender not connected, timeout during scene inspection
- **Error Handling**: Connection error if Blender not connected; timeout error when scene inspection exceeds configured limit; serialization error when scene graph cannot be safely summarized; delegated server error for Blender execution failure

### FR-SCN-002: Cleanup Scene

- **Description**: Remove objects from scene based on cleanup mode and preservation policy
- **Input**: Cleanup request concept containing cleanup mode, optional object filter, confirmation flag, child handling policy, dependent handling policy, and protected object policy
- **Output**: Cleanup result concept containing success indicator, removed object count, removed object references, preserved object references, skipped object references, and message
- **Business Rules**:
  - Cleanup mode must be one of the supported preservation strategies:
    - keep cameras
    - keep lights
    - keep cameras and lights
    - remove all objects
  - Cleanup operation must respect preservation mode:
    - camera objects are preserved when mode keeps cameras
    - light objects are preserved when mode keeps lights
    - active camera should be preserved unless explicit override is confirmed
  - Cleanup operation should be undoable when Blender undo capability is available
  - If undo capability is unavailable, operation must require explicit confirmation before destructive execution
  - Cleanup operation may support dry-run preview mode that returns objects that would be removed without modifying scene
  - Cleanup operation should not remove world environment, render settings, or scene metadata unless explicitly requested
  - Child handling policy may be one of:
    - delete hierarchy
    - detach children
    - reject cleanup when children exist
  - Dependent handling policy may be one of:
    - ignore dependents
    - reject cleanup when dependents exist
    - remove direct dependents when safe
  - Protected object policy may preserve objects marked as protected, active camera, sole camera, or objects inside protected collections
  - Linked objects and instanced objects must be handled carefully to avoid unintended removal of shared data
  - Cleanup operation should remove object instances from scene while preserving shared data blocks when policy requires
  - Cleanup operation should return deterministic summary of removed, preserved, and skipped objects
  - Cleanup operation should be atomic or undo-backed when supported; partial failure must be reported clearly
  - Cleanup operation should support object filter to remove only selected, hidden, empty, or orphaned objects when configured
  - Cleanup operation must not delete entire scene data unless explicit full-scene reset policy is requested and confirmed
- **Edge Cases**: Scene already empty, only camera remaining, only light remaining, only camera and light remaining, linked objects, instanced objects, multi-user object data, active camera, locked objects, protected collections, hidden objects, objects with children, objects used as constraint targets, large scene, cleanup timeout, partial failure, undo unavailable
- **Error Handling**: Scene validation error for invalid cleanup mode; confirmation error when destructive operation requires confirmation but not provided; connection error if Blender not connected; delegated server error for Blender execution failure; partial failure error when cleanup cannot be completed atomically

## API Contract


| Operation      | Input                             | Output                           | Description                               |
| ---------------- | ----------------------------------- | ---------------------------------- | ------------------------------------------- |
| Get scene info | Scene information request concept | Scene information result concept | Get current scene state                   |
| Cleanup scene  | Cleanup request concept           | Cleanup result concept           | Remove objects based on preservation mode |

Common contract behavior:

- All operations return structured result containing success indicator, human-readable message, and error category when failed
- All operations may accept request correlation identifier for tracing
- Scene information operation is read-only and idempotent
- Cleanup operation is destructive and must expose explicit confirmation or dry-run preview capability
- Cleanup result should include removed, preserved, and skipped object references
- Operations delegate execution to Blender through server module
- Operations must respect server-side serialization constraints due to Blender main-thread behavior
- Error categories should distinguish between connection error, validation error, scene state error, confirmation error, timeout error, and delegated server error

## Integration Points

- **Internal**:
  - shared module: taxonomy concepts for scene state representation, object reference, cleanup mode, cleanup policy, result envelope, and error categories
  - server module: Blender connection, command dispatch, response parsing, queueing, timeout handling, and undo-aware execution support
  - object module: object reference resolution and object deletion behavior when cleanup delegates detailed object removal
  - configuration module: default cleanup policies, protected object rules, detail level limits, and timeout settings
- **External**:
  - Blender scripting interface — accessed via server module
  - Blender scene data: objects, cameras, lights, collections, constraints, dependencies, and undo history

## Non-functional Requirements

- **Performance**:

  - Scene information retrieval within 1 second for standard scenes
  - Scene cleanup within 2 seconds for standard scenes excluding very large scenes or complex dependency cleanup
  - Summarized detail level should be used for large scenes to avoid oversized responses
  - Dry-run preview should complete faster than full destructive cleanup when supported
- **Reliability**:

  - Cleanup operations are atomic or undo-backed when supported by Blender runtime
  - Partial cleanup failure must be reported with clear status and affected object references
  - Scene information retrieval must gracefully handle missing active object or active camera
  - Large scene inspection must not crash or produce cyclic serialized output
- **Safety**:

  - Destructive cleanup requires explicit confirmation unless undo-backed safety is available
  - Protected object categories must be respected
  - Active camera and sole camera should be preserved by default
  - Shared or linked data should not be removed unintentionally
  - Cleanup should not affect render settings or world environment unless explicitly requested
- **Observability**:

  - Log operation type, scene identifier, result status, duration, and error category
  - Log cleanup mode, removed object count, preserved object count, and skipped object count
  - Log dry-run preview status when applicable
  - Avoid logging full object payload for very large scenes unless debug detail level is explicitly enabled
- **Consistency**:

  - Object filtering and ordering must be deterministic
  - Cleanup results must distinguish removed, preserved, and skipped objects
  - Scene state representation must use stable object references when available
- **Thread Safety**:

  - Module does not perform concurrent Blender calls directly
  - Scene operations rely on server-side serialization due to Blender main-thread constraints

## Test Scenarios / QA Checklist

- [ ]  Get scene info returns complete scene state for standard scene
- [ ]  Get scene info returns summarized state when detail level is reduced
- [ ]  Get scene info includes visible objects by default
- [ ]  Get scene info includes hidden objects when explicitly requested
- [ ]  Get scene info returns empty object list for empty scene
- [ ]  Get scene info handles missing active object gracefully
- [ ]  Get scene info handles missing active camera gracefully
- [ ]  Get scene info handles unavailable render engine information gracefully
- [ ]  Get scene info serializes large scene safely
- [ ]  Get scene info avoids cyclic reference issues
- [ ]  Get scene info returns deterministic object ordering
- [ ]  Cleanup with keep cameras mode preserves camera objects
- [ ]  Cleanup with keep lights mode preserves light objects
- [ ]  Cleanup with keep cameras and lights mode preserves both camera and light objects
- [ ]  Cleanup with remove all mode removes all non-protected objects
- [ ]  Cleanup preserves active camera by default
- [ ]  Cleanup with explicit override removes active camera only when confirmed
- [ ]  Cleanup with dry-run preview returns expected removal list without modifying scene
- [ ]  Cleanup with invalid mode returns scene validation error
- [ ]  Cleanup without required confirmation returns confirmation error
- [ ]  Cleanup on already empty scene returns success with zero removed objects
- [ ]  Cleanup handles linked objects without deleting shared data unintentionally
- [ ]  Cleanup handles instanced objects safely
- [ ]  Cleanup handles objects with children according to child handling policy
- [ ]  Cleanup handles objects used as constraint targets according to dependent handling policy
- [ ]  Cleanup returns removed, preserved, and skipped object references
- [ ]  Cleanup operation is undoable when Blender undo capability is available
- [ ]  Cleanup partial failure reports clear error and affected objects
- [ ]  Scene operations delegate to server module and propagate server errors
- [ ]  Scene operations respect server-side serialization constraints

## Assumptions & Constraints

- Blender must be running with bridge or addon enabled
- Scene operations are delegated to Blender via server module
- Blender scripting interface must be available and reachable
- Undo capability depends on Blender runtime state and configuration
- Large scenes may exceed standard performance targets and may require summarized responses
- Cleanup operations primarily affect objects, not render settings or world environment, unless explicitly extended
- Protected object handling depends on configured policy and scene state
- Linked and instanced objects require careful handling to avoid unintended data removal
- Scene inspection may be limited by serialization size and response transport constraints

## Glossary

- **Scene state representation**: Conceptual value containing full or summarized scene state
- **Cleanup mode**: Conceptual preservation strategy for cleanup operation
- **Protected object**: Object preserved during cleanup due to role, configuration, or explicit protection flag
- **Cleanup policy**: Rule set defining how children, dependents, linked data, and protected objects are handled
- **Active camera**: Camera currently used by the scene for rendering
- **Visible object**: Object currently included in viewport or scene visibility rules
- **Linked object**: Object referencing shared or external data that may not be safe to delete directly
- **Undoable operation**: Operation that can be reverted through Blender undo mechanism when available
- **Dry-run preview**: Non-destructive mode that reports intended cleanup result without modifying scene
- **Scene operation contract**: Abstraction for scene-level capabilities exposed to higher layers

## Reference

- Product Requirements Document for blender-arwaky
- Shared feature requirements documentation
- Server feature requirements documentation
