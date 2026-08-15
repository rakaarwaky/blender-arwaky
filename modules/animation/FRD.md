# FRD — Animation Feature

## Purpose

Expose bounded timeline, transform keyframe, action, and F-curve inspection through canonical dispatcher actions.

## Canonical actions

| Action | Type | Contract |
|---|---|---|
| `get_animation_state` | Read-only | Object action, scene range, and bounded F-curve points |
| `insert_object_keyframe` | Mutation | Transform data path, bounded frame, optional array index |
| `set_timeline_range` | Mutation | Bounded scene start/end/current frame |
| `list_object_keyframes` | Read-only | Explicit keyframe listing alias with the same bounded read model |

## Invariants

Only `location`, `rotation_euler`, and `scale` can be keyed. Frames are bounded to -100000 through 100000, indexes to 0 through 3, and curve/point output to 1000 records per request. Timeline current frame must remain inside the requested range. The feature does not create private animation jobs or direct transport connections.

## Security and verification

The feature accepts object names and numeric frame values only. Unit tests cover bounds and orchestrator delegation; Blender smoke tests cover timeline update, keyframe insertion, state inspection, and invalid path errors.
