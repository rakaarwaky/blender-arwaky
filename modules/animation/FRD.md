# FRD — Native Animation and Rigify Wave 1

## Purpose

Expose bounded native Blender animation inspection, FBX/BVH import, Action linking, timeline operations, and generated Rigify control inspection through canonical MCP/CLI actions. The feature is an executor only: natural-language interpretation and animation planning belong to the external AI harness.

## Canonical actions

| Action | Type | Contract |
|---|---|---|
| `get_animation_state` | Read-only | Object action, scene range, and bounded F-curve points |
| `insert_object_keyframe` | Mutation | Transform data path, bounded frame, optional array index |
| `set_timeline_range` | Mutation | Bounded scene start/end/current frame |
| `list_object_keyframes` | Read-only | Explicit keyframe listing alias with the same bounded read model |
| `list_animation_actions` | Read-only | Native Blender Actions, optionally filtered to an armature's active Action |
| `inspect_rigify_controls` | Read-only | Generated Rigify control, deform, IK, pole, mechanism, and side metadata |
| `import_animation_file` | Mutation | Native FBX or BVH import with created object and Action report |
| `link_action_to_armature` | Mutation | Assign one existing native Action to an armature and report the previous Action |

## Native boundary

The executor does not create walk cycles, run cycles, jump cycles, facial performances, or natural-language plans. A caller imports motion or pose data, inspects the result, links an Action, edits or bakes it, and validates the outcome. Rigify-specific logic is limited to inspecting generated controls and preserving explicit armature/action references.

The current import contract supports `fbx` and `bvh`. FBX import maps to Blender's `bpy.ops.import_scene.fbx`; BVH import maps to `bpy.ops.import_anim.bvh`. The implementation reports the actual importer and newly created objects/actions. Imported Actions are not assumed to be automatically linked to the target armature.

## Invariants

Only `location`, `rotation_euler`, and `scale` can be keyed by the legacy transform keyframe action. Frames are bounded to -100000 through 100000, indexes to 0 through 3, and curve/point output to 1000 records per request. Timeline current frame must remain inside the requested range. Import accepts only explicitly supported native formats and rejects unsupported extensions before the Blender gateway is called. Armature linking requires an existing armature and existing Action. Rigify control inspection is read-only and classifies `DEF-`, `_ik`, `_pole`, `MCH-`, and `ORG-` naming families without mutating the scene.

## Security and verification

The feature accepts bounded object/action/armature names, numeric frame values, and bounded source paths. Unit tests cover Action listing, Rigify role classification, importer validation, import result conversion, Action linking, legacy frame/keyframe bounds, and orchestrator delegation. Dispatcher contract tests cover ownership and read-only/mutation flags. Blender smoke tests must cover a native Action, a generated Rigify armature, Action linking, control inspection, and valid/invalid import dispatch.

## Exclusions

This feature does not provide natural-language parsing, planning, proprietary plugin adapters, motion synthesis, retargeting solvers, facial performance generation, automatic walk-cycle creation, or direct MCP registration. Retargeting and pose-asset import remain subsequent waves built on this native foundation.
