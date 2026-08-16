# FRD — Native Animation and Rigify Wave 5

## Purpose

Expose bounded native Blender animation inspection, FBX/BVH import, Action linking, timeline operations, Rigify control inspection, native Pose Library assets, pose mirroring, session pose copy/paste, Rigify pose keyframing, facial and hand control inspection, Rigify FK/IK switching, MPFB2 shape-key keyframing, facial control animation, native motion-capture import, explicit bone mapping, rest-pose validation, Action retargeting, root-motion policy, baking, NLA track/strip assembly, layering, Rigify control masks, NLA baking, and NLA validation through canonical MCP/CLI actions. The feature is an executor only: natural-language interpretation and animation planning belong to the external AI harness.

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
| `import_motion_capture` | Mutation | Import native BVH or FBX motion data and report source Actions |
| `build_bone_mapping` | Read-only | Build an explicit exact, Mixamo, or BVH source-to-target mapping |
| `validate_rest_pose` | Read-only | Validate mapped rest-bone lengths and report warnings |
| `retarget_animation` | Mutation | Write supported source transform channels to a new Rigify target Action |
| `set_root_motion` | Mutation | Store the explicit preserve, separate, or ignore root-motion policy |
| `bake_retarget_action` | Mutation | Bake target pose animation through native `bpy.ops.nla.bake` |
| `validate_animation_result` | Read-only | Validate target Action ownership, mapped channels, frame range, and key count |
| `create_nla_track` | Mutation | Create or reuse a native NLA track with mute and solo state |
| `add_nla_strip` | Mutation | Add an existing Action with bounded timing, blend, influence, repeat, and reverse settings |
| `set_nla_strip` | Mutation | Update native NLA strip timing and blend properties |
| `set_animation_layer` | Mutation | Set track mute/solo and apply layer blend/influence to its strips |
| `set_animation_mask` | Mutation | Store and validate an explicit Rigify control-bone mask for an NLA strip |
| `remove_nla_strip` | Mutation | Remove one named NLA strip from a track |
| `bake_nla_assembly` | Mutation | Bake evaluated NLA layers into one editable Action using native NLA bake |
| `validate_nla_assembly` | Read-only | Validate NLA tracks, strips, Action linkage, ranges, influence, and warnings |

## Native boundary

The executor does not create walk cycles, run cycles, jump cycles, facial performances, or natural-language plans. It provides native pose assets and pose-buffer primitives so an external AI harness can compose those workflows explicitly. A caller imports motion or pose data, inspects the result, links an Action, edits or bakes it, assembles NLA tracks and strips, and validates the outcome. Rigify-specific logic includes bounded domain inspection, explicit generated-control references, allowlisted `IK_FK` mutation on limb-parent controls, facial control keyframing, and retarget output directed to mapped control bones; it never treats `DEF-`, `MCH-`, or `ORG-` bones as animator targets.

The current import contract supports `fbx` and `bvh`. FBX import maps to Blender's `bpy.ops.import_scene.fbx`; BVH import maps to `bpy.ops.import_anim.bvh`. The implementation reports the actual importer and newly created objects/actions. Imported Actions are not assumed to be automatically linked to the target armature.

## Invariants

The legacy object transform action accepts only `location`, `rotation_euler`, and `scale`. Rigify pose keyframing uses native pose-bone location, rotation mode appropriate rotation channels, and scale channels. Frames are bounded to -100000 through 100000, indexes to 0 through 3, and curve/point output to 1000 records per request. Timeline current frame must remain inside the requested range. Import accepts only explicitly supported native formats and rejects unsupported extensions before the Blender gateway is called. Armature linking requires an existing armature and existing Action. Rigify control inspection is read-only and classifies `DEF-`, `_ik`, `_pole`, `MCH-`, and `ORG-` naming families without mutating the scene. Face and hand inspection is bounded to 1000 records and excludes generated mechanism/deform/original bones. FK/IK mode accepts only `arm` or `leg`, `left` or `right`, and `fk` or `ik`; only the `IK_FK` custom property is mutable. Shape-key values are bounded to 0.0 through 1.0. Mapping payloads are bounded to 5,000 entries to support the 1,090-bone generated Rigify evidence rig while remaining within strict payload limits. Retargeting accepts only supported transform channels, integer bounded frames, explicit mappings, and root-motion policies `preserve`, `separate`, or `ignore`. NLA strips accept bounded Action timing, scale, repeat, blend, influence, extrapolation, and reverse state. NLA masks may contain only existing animator control bones and reject `DEF-`, `MCH-`, and `ORG-` names. Baking uses native NLA bake with explicit frame range and step.

## Security and verification

The feature accepts bounded object/action/armature names, numeric frame values, and bounded source paths. Unit tests cover Action listing, pose asset result mapping, mirror/blend bounds, pose-buffer result mapping, face/hand domain mapping, FK/IK validation, shape-key bounds, facial control mapping, bone-mapping conversion, rest-pose conversion, retarget result conversion, root-motion validation, baking conversion, result validation, NLA track/strip/layer/mask/bake/validation conversion, Rigify role classification, importer validation, import result conversion, Action linking, legacy frame/keyframe bounds, and orchestrator delegation. Dispatcher contract tests cover ownership and read-only/mutation flags. Blender smoke tests must cover a native source Action, a generated Rigify target armature, exact mapping across 1,090 bones, approved rest-pose validation, root-motion policy, native Action retargeting, and preservation of the source Action. Wave 5 smoke additionally covers two NLA tracks, Action strips, ADD layering, Rigify control mask metadata, strip update/removal, assembly validation, and NLA bake output.

## Exclusions

This feature does not provide natural-language parsing, planning, proprietary plugin adapters, motion synthesis, facial performance generation, automatic walk-cycle creation, automatic mapping approval, export packaging, or direct MCP registration. Wave 5 provides NLA assembly primitives; the external AI harness decides which Actions and layers to compose. Retargeting is intentionally explicit and deterministic: an AI harness must inspect or provide the mapping and decide whether rest-pose warnings are acceptable before mutation. Pose asset application uses Blender's native operator when an Asset Browser context exists and a native Action-evaluation fallback in headless execution, preserving the same asset and Rigify semantics.
