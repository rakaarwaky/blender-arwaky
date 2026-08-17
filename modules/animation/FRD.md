# FRD — Native Blender Animation

## Purpose

Expose bounded native Blender animation primitives through canonical MCP and CLI actions. The feature provides timeline, Action, keyframe, pose asset, shape-key, import, and NLA operations. Animation planning, artistic decisions, and complex provider workflows remain responsibilities of the external AI harness or plugins.

The core animation feature does not create procedural walk cycles, natural-language animation, Rigify semantic mappings, facial performances, or motion-capture retargeting. Those workflows are provider-owned and may be added later through external plugins.

## Canonical actions

| Action | Type | Contract |
|---|---|---|
| `get_animation_state` | Read-only | Object Action, scene range, and bounded F-curve points |
| `insert_object_keyframe` | Mutation | Native object location, rotation, or scale keyframe |
| `set_timeline_range` | Mutation | Bounded scene start, end, and current frame |
| `list_object_keyframes` | Read-only | Bounded native F-curve keyframe listing |
| `list_animation_actions` | Read-only | Native Blender Actions, optionally filtered to an armature |
| `import_animation_file` | Mutation | Native FBX or BVH import with imported object and Action report |
| `link_action_to_armature` | Mutation | Assign one existing native Action to an armature |
| `list_pose_assets` | Read-only | List native Blender pose assets |
| `create_pose_asset` | Mutation | Create a native pose asset from the active armature pose |
| `apply_pose_asset` | Mutation | Apply a native pose asset with optional mirror |
| `blend_pose_asset` | Mutation | Blend a native pose asset with optional mirror |
| `set_shape_key_keyframe` | Mutation | Set and keyframe one mesh shape-key value |
| `create_nla_track` | Mutation | Create or reuse a native NLA track |
| `add_nla_strip` | Mutation | Add an existing Action to a native NLA track |
| `set_nla_strip` | Mutation | Update native NLA strip timing and blend properties |
| `set_animation_layer` | Mutation | Set native NLA track mute, solo, blend, and influence |
| `set_animation_mask` | Mutation | Set a bounded NLA strip bone mask |
| `remove_nla_strip` | Mutation | Remove one native NLA strip |
| `bake_nla_assembly` | Mutation | Bake evaluated NLA layers into an editable Action |
| `validate_nla_assembly` | Read-only | Validate native NLA tracks, strips, Action linkage, ranges, and warnings |

## Native boundary

The executor calls bounded Blender-native operations. It does not decide which poses to create, how a character should walk, which Rigify controls to select, or how a motion-capture source should be retargeted. An external AI harness may compose the primitive operations, and an external plugin may provide provider-specific workflows.

FBX and BVH import remains a native import boundary. Imported Actions are reported and can be inspected or linked, but the core does not automatically map them to a character rig.

Pose assets use Blender's native pose library operations. NLA operations use Blender's native tracks, strips, blending, masking, and bake behavior. The core does not attach semantic character meaning to any bone name.

## Invariants

Object animation accepts only `location`, `rotation_euler`, and `scale`. Frames are bounded to the executor frame policy, indexes are bounded, and output is limited per request. Timeline current frame must remain inside the requested range. Import accepts only explicitly supported native formats. Armature linking requires an existing armature and Action. Shape-key values are bounded. NLA operations validate Action names, tracks, strips, timing, blend, influence, repeat, extrapolation, and masks.

## Exclusions

This feature excludes Rigify control inspection, FK/IK semantic switching, facial and hand control systems, custom character mappings, motion-capture retargeting, rest-pose mapping, root-motion policy abstraction, procedural walk-cycle generation, natural-language animation generation, export packaging, and plugin-specific animation adapters.

Those capabilities are not deleted from the product concept; they are deferred to external provider plugins so that the core remains small, native, stable, and maintainable.
