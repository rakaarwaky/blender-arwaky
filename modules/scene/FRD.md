
# FRD — Scene Management Feature

## Purpose

Manages scene-level inspection and bulk cleanup for **blender-arwaky**.

This feature owns scene-wide awareness and bulk operation policy. It is responsible for understanding the current state of the scene, summarizing scene contents, deciding which objects should be preserved during cleanup, and producing a cleanup report. Technical deletion of individual objects is delegated to the object feature.

The scene feature is policy-oriented and report-oriented, not a low-level object manipulation feature.

## Scope

- Inspect scene state
- Scene metadata summary
- Object summary by type and visibility
- Camera summary
- Light summary
- Active camera and active object awareness
- Render settings summary
- Collection summary
- Protected object awareness
- Bulk cleanup
- Preservation policy resolution
- Dry-run cleanup preview
- Cleanup reporting
- Deterministic filtering and ordering
- Event emission for inspection and cleanup completion
- Configuration-driven default preservation and dry-run behavior

## Out of Scope

- Single object create, read, update, or delete operations — owner: object feature
- Material detail management — owner: object feature
- Modifier detail management — owner: object feature
- Render execution — owner: render feature
- Asset import — owner: asset feature
- Queue management — owner: gateway feature
- Background task tracking — owner: job feature
- Long-running job polling — owner: job feature
- Network transport and Blender connectivity — owner: gateway feature
- Final licensing or usage compliance decisions — owner: higher-level product policy

## Depends On

- gateway feature for Blender command execution and connection state
- object feature for single-object deletion primitives and object reference resolution
- config feature for default preservation policy, dry-run default, inspection limits, and protection rules
- shared feature for common taxonomy, result envelope, and error category concepts

## Provides To

- dispatcher feature
- observability or diagnostics consumers when event and report data are exposed
- higher-level workflow or agent orchestration layers that need scene awareness

## Functional Requirements

### FR-SCN-001: Inspect Scene State

Scene returns an overview of current scene state.

- **Description**: Retrieve a structured summary of the active scene, including object count, camera list, light list, render settings summary, and scene metadata
- **Input**: Scene inspection request concept containing optional detail level, optional object filter, and optional inclusion flag for hidden objects
- **Output**: Scene inspection result concept containing success indicator, scene state summary, and message
- **Business Rules**:
  - Inspection is read-only and must not mutate scene state
  - Inspection must be idempotent
  - Scene state summary should include:
    - scene name or scene identifier
    - total object count
    - object count by type
    - visible object count
    - hidden object count when requested
    - camera list summary
    - light list summary
    - active camera reference
    - active object reference when available
    - render settings summary
    - resolution summary
    - render engine summary
    - frame range summary
    - unit system summary
    - collection summary
    - world or environment summary when available
    - protected object summary
  - Object list should be deterministic, ordered by stable object reference or object name
  - Hidden objects are excluded by default unless explicitly requested
  - Large scenes should support summarized detail level to avoid oversized response
  - Missing active camera or active object should be represented as empty reference, not as failure
  - Response should serialize safely and avoid cyclic references
  - Inspection may include capability flags indicating supported scene operations
- **Edge Cases**: Empty scene, no active object, no active camera, missing render engine information, large scene, hidden objects, linked objects, instanced objects, protected objects, stale object references, serialization limit, gateway not connected, inspection timeout
- **Error Handling**: Connection error when gateway is unavailable; timeout error when inspection exceeds configured limit; scene state error when scene cannot be safely inspected; delegated gateway error for Blender execution failure

### FR-SCN-002: Cleanup Scene Objects

Scene determines preservation policy and delegates actual deletion to object feature.

- **Description**: Remove objects from scene based on preservation policy, cleanup filter, and confirmation rules
- **Input**: Cleanup request concept containing cleanup mode, preservation list, optional object filter, dry-run flag, confirmation flag, child handling policy, dependent handling policy, and protected object policy
- **Output**: Cleanup report concept containing success indicator, removed object count, preserved object count, skipped object count, removed object references, preserved object references, skipped object references, dry-run indicator, and message
- **Business Rules**:
  - Scene feature owns policy resolution:
    - which objects are candidates for removal
    - which objects must be preserved
    - whether dry-run preview is active
    - whether confirmation is required
  - Object feature owns deletion execution:
    - resolving individual object reference
    - performing single-object deletion
    - handling low-level deletion constraints
    - reporting deletion outcome
  - Preservation policy may preserve:
    - camera objects
    - light objects
    - active camera
    - sole camera
    - objects marked protected
    - objects inside protected collections
  - Default preservation policy is resolved from configuration when request does not specify explicit policy
  - Dry-run mode must return cleanup preview without modifying scene
  - Dry-run report must use the same structure as actual cleanup report
  - Cleanup operation should be deterministic and repeatable for identical scene state and policy
  - Cleanup operation should return removed, preserved, and skipped object references
  - Cleanup operation should not remove world environment, render settings, or scene metadata unless explicitly extended by policy
  - Cleanup operation should support child handling policy:
    - delete hierarchy
    - detach children
    - reject cleanup when children exist
  - Cleanup operation should support dependent handling policy:
    - ignore dependents
    - reject cleanup when dependents exist
    - remove direct dependents when safe
  - Linked objects and instanced objects must be handled carefully to avoid unintended removal of shared data
  - Cleanup operation should be undo-aware when Blender undo capability is available
  - If undo capability is unavailable and operation is destructive, explicit confirmation is required
  - Cleanup operation may emit cleanup completion event after final report is produced
  - Partial failure must be reported clearly and should not be silently ignored
- **Edge Cases**: Scene already empty, only camera remaining, only light remaining, only protected objects remaining, linked objects, instanced objects, multi-user object data, active camera, locked objects, protected collections, hidden objects, objects with children, objects used as constraint targets, large scene, cleanup timeout, partial deletion failure, missing confirmation, dry-run with no removable objects
- **Error Handling**: Scene state error when scene is invalid for cleanup; protection error when protected object deletion is attempted without override; validation error for invalid cleanup mode or policy; confirmation error when destructive cleanup lacks required confirmation; delegated deletion error when object feature reports deletion failure

## Boundary: Scene vs Object

- Scene:

  - bulk operations
  - scene-wide inspection
  - preservation policy resolution
  - cleanup filtering
  - dry-run preview
  - cleanup reporting
  - protected object policy decisions
- Object:

  - single object technical operations
  - single object deletion execution
  - object reference resolution
  - low-level deletion constraints
  - object-level hierarchy handling as directed by scene policy
  - linked or instanced object safety at execution level

Conceptual separation:

- Scene cleanup request with preserve cameras enabled produces a preservation policy and cleanup report
- Object deletion request performs the actual removal of a single object reference

The scene feature decides what should happen.
The object feature executes the technical deletion safely.

## Error Categories

- scene state error — scene is in invalid state for requested operation
- protection error — attempted to delete protected object without valid override or confirmation
- validation error — invalid cleanup mode, invalid preservation policy, invalid filter, or invalid request concept
- confirmation error — destructive operation requires confirmation but confirmation was not provided
- delegated deletion error — object feature failed to delete one or more objects
- timeout error — scene inspection or cleanup exceeded configured time limit
- connection error — gateway or Blender execution channel is unavailable

## Events

- scene inspection completed event — emitted after scene inspection successfully produces scene state summary
- scene cleanup completed event — emitted after actual cleanup operation finishes and cleanup report is produced
- scene cleanup dry-run completed event — emitted after dry-run preview finishes and preview report is produced
- scene cleanup failed event — emitted when cleanup operation fails or partially fails

Event payloads should include:

- operation type
- success indicator
- summary counts
- dry-run indicator
- error category when failed
- correlation identifier when available

Event payloads should avoid full object dumps for large scenes and must avoid sensitive data.

## Configuration Keys


| Configuration Concept                | Description                                                                                            | Typical Default                                                           |
| -------------------------------------- | -------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------- |
| Default preservation list            | Default object categories preserved during cleanup when request does not specify explicit preservation | Preserve cameras and lights                                               |
| Default dry-run mode                 | Whether cleanup defaults to preview-only mode                                                          | Disabled                                                                  |
| Include hidden objects in inspection | Whether hidden objects are included in scene inspection by default                                     | Disabled                                                                  |
| Maximum inspection detail limit      | Limit for object detail returned during inspection to avoid oversized response                         | Configured safe limit                                                     |
| Protected object policy              | Rules for protecting active camera, sole camera, lights, and explicitly protected objects              | Active camera protected                                                   |
| Cleanup confirmation required        | Whether destructive cleanup requires explicit confirmation when undo is unavailable                    | Enabled                                                                   |
| Child handling default               | Default behavior for children of deleted objects                                                       | Detach children or reject when children exist, depending on safety policy |
| Dependent handling default           | Default behavior for dependents such as constraints or references                                      | Reject when dependents exist or handle only when safe                     |
| Cleanup timeout                      | Maximum allowed duration for cleanup operation before timeout category is returned                     | Configured timeout                                                        |

## QA Checklist

- [ ]  Scene inspection returns object summary
- [ ]  Scene inspection returns camera summary
- [ ]  Scene inspection returns light summary
- [ ]  Scene inspection returns render settings summary
- [ ]  Scene inspection returns active camera reference when available
- [ ]  Scene inspection handles empty scene gracefully
- [ ]  Scene inspection handles missing active camera gracefully
- [ ]  Scene inspection excludes hidden objects by default
- [ ]  Scene inspection includes hidden objects when explicitly requested
- [ ]  Scene inspection uses deterministic object ordering
- [ ]  Scene inspection supports summarized detail level for large scenes
- [ ]  Cleanup uses preservation policy
- [ ]  Cleanup preserves cameras when preservation policy requires it
- [ ]  Cleanup preserves lights when preservation policy requires it
- [ ]  Cleanup preserves active camera by default
- [ ]  Cleanup supports dry-run mode
- [ ]  Dry-run cleanup does not mutate scene
- [ ]  Dry-run cleanup returns same report structure as actual cleanup
- [ ]  Cleanup delegates actual deletion to object feature
- [ ]  Cleanup report includes removed object count
- [ ]  Cleanup report includes preserved object count
- [ ]  Cleanup report includes skipped object count
- [ ]  Cleanup report includes removed object references
- [ ]  Cleanup handles linked objects without removing shared data unintentionally
- [ ]  Cleanup handles instanced objects safely
- [ ]  Cleanup handles objects with children according to configured child policy
- [ ]  Cleanup handles protected objects according to configured protection policy
- [ ]  Cleanup without required confirmation returns confirmation error
- [ ]  Cleanup partial failure is reported clearly
- [ ]  No overlap with object feature for single-object technical operations
- [ ]  No overlap with render feature for render execution
- [ ]  No overlap with asset feature for asset import
- [ ]  No overlap with job feature for background task tracking
