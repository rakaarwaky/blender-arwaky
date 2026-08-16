# FRD — Native Animation and Rigify Wave 3

## Purpose

Expose bounded native Blender animation inspection, FBX/BVH import, Action linking, timeline operations, Rigify control inspection, native Pose Library assets, pose mirroring, session pose copy/paste, Rigify pose keyframing, facial and hand control inspection, Rigify FK/IK switching, MPFB2 shape-key keyframing, and facial control animation through canonical MCP/CLI actions. The feature is an executor only: natural-language interpretation and animation planning belong to the external AI harness.

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
| `list_pose_assets` | Read-only | List native Blender Actions marked as pose assets |
| `create_pose_asset` | Mutation | Create a persistent native pose asset from the active Rigify pose |
| `apply_pose_asset` | Mutation | Apply a pose asset, with optional native left-right mirroring |
| `blend_pose_asset` | Mutation | Blend a pose asset by bounded factor, with optional mirroring |
| `copy_rigify_pose` | Mutation | Copy selected Rigify pose to Blender's session pose buffer |
| `paste_rigify_pose` | Mutation | Paste the session pose buffer, optionally flipped and selection-limited |
| `keyframe_rigify_pose` | Mutation | Insert native location, rotation, and scale keyframes for Rigify controls |
| `inspect_face_animation_channels` | Read-only | Inspect bounded Rigify facial controls and optional mesh shape keys |
| `inspect_hand_animation_controls` | Read-only | Inspect bounded Rigify hand and finger controls by side |
| `set_rigify_fk_ik_mode` | Mutation | Set and optionally key the allowlisted `IK_FK` property on a Rigify limb parent |
| `set_shape_key_keyframe` | Mutation | Set and keyframe one bounded MPFB2 mesh shape-key value |
| `edit_face_control_animation` | Mutation | Keyframe an allowlisted Rigify facial control transform |

## Native boundary

The executor does not create walk cycles, run cycles, jump cycles, facial performances, or natural-language plans. It provides native pose assets and pose-buffer primitives so an external AI harness can compose those workflows explicitly. A caller imports motion or pose data, inspects the result, links an Action, edits or bakes it, and validates the outcome. Rigify-specific logic includes bounded domain inspection, explicit generated-control references, allowlisted `IK_FK` mutation on limb-parent controls, and facial control keyframing; it never keys `DEF-`, `MCH-`, or `ORG-` bones through the facial action.

The current import contract supports `fbx` and `bvh`. FBX import maps to Blender's `bpy.ops.import_scene.fbx`; BVH import maps to `bpy.ops.import_anim.bvh`. The implementation reports the actual importer and newly created objects/actions. Imported Actions are not assumed to be automatically linked to the target armature.

## Invariants

The legacy object transform action accepts only `location`, `rotation_euler`, and `scale`. Rigify pose keyframing uses native pose-bone location, rotation mode appropriate rotation channels, and scale channels. Frames are bounded to -100000 through 100000, indexes to 0 through 3, and curve/point output to 1000 records per request. Timeline current frame must remain inside the requested range. Import accepts only explicitly supported native formats and rejects unsupported extensions before the Blender gateway is called. Armature linking requires an existing armature and existing Action. Rigify control inspection is read-only and classifies `DEF-`, `_ik`, `_pole`, `MCH-`, and `ORG-` naming families without mutating the scene. Face and hand inspection is bounded to 1000 records and excludes generated mechanism/deform/original bones. FK/IK mode accepts only `arm` or `leg`, `left` or `right`, and `fk` or `ik`; only the `IK_FK` custom property is mutable. Shape-key values are bounded to 0.0 through 1.0.

## Security and verification

The feature accepts bounded object/action/armature names, numeric frame values, and bounded source paths. Unit tests cover Action listing, pose asset result mapping, mirror/blend bounds, pose-buffer result mapping, face/hand domain mapping, FK/IK validation, shape-key bounds, facial control mapping, Rigify role classification, importer validation, import result conversion, Action linking, legacy frame/keyframe bounds, and orchestrator delegation. Dispatcher contract tests cover ownership and read-only/mutation flags. Blender smoke tests must cover a native Action, a generated Rigify armature, Action linking, control inspection, pose assets, face and hand discovery, FK/IK switching, facial control keyframing, MPFB2 shape-key keyframing, and valid/invalid import dispatch.

## Exclusions

This feature does not provide natural-language parsing, planning, proprietary plugin adapters, motion synthesis, retargeting solvers, facial performance generation, automatic walk-cycle creation, or direct MCP registration. Pose asset application uses Blender's native operator when an Asset Browser context exists and a native Action-evaluation fallback in headless execution, preserving the same asset and Rigify semantics.
