# FRD — Native Blender Animation

## System Overview
The Animation module exposes bounded native Blender animation primitives through canonical MCP and CLI actions. It acts as a bridge between external AI orchestrators and Blender's internal Action, keyframe, NLA, and pose asset systems, strictly avoiding procedural generation or semantic character mapping.

## Functional Requirements

### FR-001: Native Animation State & Keyframing
- **Description**: Inspect and mutate native object keyframes and F-curves.
- **Input**: `object_name` (required), `frame` (required), `data_path` (required), `index` (optional), `limit` (optional).
- **Output**: `UnifiedEnvelope` containing bounded F-curve points, Action states, or mutation confirmation.
- **Business Rules**: Accepts only `location`, `rotation_euler`, and `scale`. Frames are bounded to executor policy. Timeline current frame must remain inside the requested range.
- **Edge Cases**: Missing object; locked transform channels; non-existent Action; out-of-bounds frame index.
- **Error Handling**: `not_found` for missing objects/Actions; `validation_error` for out-of-bounds frames; `execution_error` for Blender-side failures.

### FR-002: Timeline & NLA Management
- **Description**: Control scene timeline ranges and manipulate Non-Linear Animation (NLA) tracks and strips.
- **Input**: `frame_start`, `frame_end`, `current_frame`, NLA track/strip names, timing, blend properties, bone masks.
- **Output**: `UnifiedEnvelope` with updated timeline state or NLA assembly validation results.
- **Business Rules**: NLA operations validate Action names, tracks, strips, timing, blend, influence, repeat, extrapolation, and masks. Bake operations evaluate NLA layers into editable Actions.
- **Edge Cases**: Cyclic NLA dependencies; missing target armature; invalid bone mask names; strip timing overlaps.
- **Error Handling**: `validation_error` for invalid NLA parameters; `state_error` for corrupt NLA tracks; `execution_error` for bake failures.

### FR-003: Pose Assets & Shape Keys
- **Description**: Manage native Blender pose libraries and mesh shape-key keyframes.
- **Input**: `armature_name`, `pose_asset_name`, `mirror` (boolean), `shape_key_name`, `value`, `slider_min`, `slider_max`.
- **Output**: `UnifiedEnvelope` confirming asset creation, application, or shape-key mutation.
- **Business Rules**: Pose assets use Blender's native pose library operations. Shape-key values and slider limits are finite and bounded.
- **Edge Cases**: Missing armature; non-existent pose asset; shape-key value exceeding slider limits; mesh lacking shape-keys.
- **Error Handling**: `not_found` for missing assets/shape-keys; `validation_error` for out-of-bounds values.

### FR-004: Animation Import & Linking
- **Description**: Import native animation files (FBX/BVH) and link Actions to armatures.
- **Input**: `file_path` (required), `armature_name` (required), `action_name` (required).
- **Output**: `UnifiedEnvelope` with imported object and Action report.
- **Business Rules**: FBX and BVH import remains a native boundary. Imported Actions are reported and can be inspected or linked. Core does not automatically map them to a character rig.
- **Edge Cases**: Unsupported format; missing local file; armature lacks compatible bone structure for Action linkage.
- **Error Handling**: `asset_not_found` for missing files; `validation_error` for unsupported formats; `execution_error` for import failures.

## API Contract

| Operation | Input | Output | Description |
|---|---|---|---|
| `get_animation_state` | `object_name`, `limit` | `UnifiedEnvelope` | Read-only bounded F-curve and Action state |
| `insert_object_keyframe` | `object_name`, `frame`, `data_path`, `index` | `UnifiedEnvelope` | Mutate native object keyframe |
| `set_timeline_range` | `frame_start`, `frame_end`, `current_frame` | `UnifiedEnvelope` | Mutate scene timeline bounds |
| `list_object_keyframes` | `object_name`, `limit` | `UnifiedEnvelope` | Read-only bounded keyframe listing |
| `list_animation_actions` | `armature_name` (opt) | `UnifiedEnvelope` | Read-only native Actions |
| `import_animation_file` | `file_path` | `UnifiedEnvelope` | Native FBX/BVH import |
| `link_action_to_armature` | `armature_name`, `action_name` | `UnifiedEnvelope` | Assign Action to armature |
| `list_pose_assets` | None | `UnifiedEnvelope` | List native pose assets |
| `create_pose_asset` | `armature_name`, `asset_name` | `UnifiedEnvelope` | Create pose from active armature |
| `apply_pose_asset` | `asset_name`, `mirror` | `UnifiedEnvelope` | Apply native pose asset |
| `blend_pose_asset` | `asset_name`, `mirror` | `UnifiedEnvelope` | Blend native pose asset |
| `set_shape_key_keyframe` | `object_name`, `shape_key`, `value` | `UnifiedEnvelope` | Keyframe mesh shape-key |
| `create_nla_track` | `track_name` | `UnifiedEnvelope` | Create native NLA track |
| `add_nla_strip` | `track_name`, `action_name` | `UnifiedEnvelope` | Add Action to NLA track |
| `set_nla_strip` | `strip_name`, `timing`, `blend` | `UnifiedEnvelope` | Update NLA strip properties |
| `set_animation_layer` | `track_name`, `mute`, `solo` | `UnifiedEnvelope` | Set NLA track layer properties |
| `set_animation_mask` | `strip_name`, `bone_mask` | `UnifiedEnvelope` | Set NLA strip bone mask |
| `remove_nla_strip` | `strip_name` | `UnifiedEnvelope` | Remove native NLA strip |
| `bake_nla_assembly` | `armature_name` | `UnifiedEnvelope` | Bake NLA layers to Action |
| `validate_nla_assembly` | `armature_name` | `UnifiedEnvelope` | Validate NLA tracks and linkage |

## Integration Points

- **3rd Party**: No 3rd party integrations.
- **Internal**: `gateway` (Blender command transport), `dispatcher` (action routing), `asset` (FBX/BVH file acquisition).

## Non-functional Requirements (Detailed)

- **Performance**: Keyframe listing bounded to 1000 records per request. Timeline operations execute synchronously within 500ms.
- **Security**: File paths for animation imports are validated by the `security` module to prevent path traversal.
- **Scalability**: NLA track operations are serialized via the `gateway` queue to respect Blender's main-thread constraints.

## Test Scenarios / QA Checklist

- [ ] Verify `insert_object_keyframe` correctly applies location/rotation/scale bounds.
- [ ] Verify `import_animation_file` rejects non-FBX/BVH formats with `validation_error`.
- [ ] Verify `bake_nla_assembly` correctly evaluates layered strips into a single Action.
- [ ] Verify `set_timeline_range` rejects `frame_end` < `frame_start`.

## Assumptions & Constraints

- Animation planning, artistic decisions, and complex provider workflows remain responsibilities of the external AI harness.
- The core does not attach semantic character meaning to any bone name.
- Rigify control inspection and FK/IK semantic switching are explicitly excluded.

## Glossary

- **Action**: A native Blender data-block containing animation keyframes.
- **NLA (Non-Linear Animation)**: Blender's system for blending and layering multiple Actions.
- **UnifiedEnvelope**: The standardized JSON response wrapper containing success indicator, data payload, error category, tracking ID, and warnings.
- **TrackingID**: UUIDv4 string for request correlation across logs, metrics, and audit events.

## Reference

- PRD: `./PRD.md`
- Depends On: `gateway`, `dispatcher`, `asset`
