# FRD — Object Management Feature

## Purpose

Single authority for single-object technical operations on objects in the scene: create primitives, place existing objects, transform, assign materials, manage modifiers, delete individual objects, inspect state. Validates object-level requests, resolves references deterministically, enforces naming/protection policies, delegates execution to Blender via gateway. Bulk scene decisions belong to scene feature.

## Scope

- Create primitive objects from supported catalog
- Place existing object at target transform
- Transform object (location, rotation, scale)
- Material assignment with PBR properties
- Modifier management (add, remove, configure)
- Delete single object with protection policy
- Get detailed object information
- Deterministic object reference resolution
- Naming policy enforcement
- Locked transform channel handling
- Linked/instanced object safety
- Object lifecycle observability events

## Out of Scope

Asset download/import, scene cleanup bulk ops, render execution, camera lens/framing, HDRI lighting, queue management, background task lifecycle, scene-wide inspection, viewport capture/output artifacts.

## Depends On

gateway (Blender command transport + scene-mutating serialization), config (naming policy, unit convention, primitive defaults, protection rules), security policy (destructive confirmation, redaction).

## Provides To

dispatcher, scene (delegates individual deletions during bulk cleanup).

## Functional Requirements

### FR-OBJ-001: Place Existing Object

- **Description**: Position object that already exists in scene at specified transform
- **Input**: Object ref, target location/rotation/scale, optional placement policy
- **Output**: Placement result (success, resolved ref, final transform summary)
- **Rules**: Object must already exist in scene. Not-yet-imported → rejected with guidance to asset feature. Reference resolution deterministic: unique ID → exact name → qualified path/collection. Ambiguous → ambiguous reference error. Transform values must be finite 3-vectors. Rotation follows object rotation mode or scene default. Zero scale rejected unless explicitly allowed. Preserves identity (no rename/duplicate). Idempotent for identical ref + transform. Locked channels respected unless explicit override.
- **Edge Cases**: Not found, not imported, ambiguous ref, invalid/non-finite coordinates, zero scale, locked channels, hidden/protected/instanced/linked object, unit mismatch, stale ref
- **Error Handling**: Not found error; ambiguous reference error; validation error; transform lock error

### FR-OBJ-002: Create Primitive

- **Description**: Create basic object from supported primitive catalog
- **Input**: Primitive type, location, optional name/size/rotation/scale/target collection
- **Output**: Creation result (success, resolved ref, generated name)
- **Rules**: Type must be in supported catalog. Mesh primitives: cube, sphere, cylinder, plane, cone, torus. Non-mesh: empty, camera, light (may be supported). Default type applied when omitted. Name uniqueness via configured policy: reject/auto-suffix/overwrite. Size positive + finite. Added to active scene + default/specified collection. Initial transform applied. Returns canonical ref + generated name. Reports adjusted name when policy modifies requested name.
- **Edge Cases**: Invalid type, duplicate name, zero/negative size, non-finite, missing collection, creation not permitted in current mode, object limit, unsupported primitive in runtime, naming conflict
- **Error Handling**: Validation error for invalid type/params; scene state error for missing collection; naming conflict resolved per policy

### FR-OBJ-003: Set Transform

- **Description**: Modify location/rotation/scale of existing object (absolute or relative)
- **Input**: Object ref, optional location/rotation/scale, optional mode
- **Output**: Transform result (success, final transform summary)
- **Rules**: Object must exist + resolvable. Values finite 3-vectors. Rotation per object rotation mode or request metadata. Unit convention from config. Absolute + relative modes. Omitted components preserved. Locked channels respected unless override. Idempotent for identical absolute values. Final transform returned. No modification of shared object data unless explicitly intended. Constrained/animated objects accepted with warning.
- **Edge Cases**: Not found, invalid/non-finite values, locked channels, constrained/instanced/linked/disabled object, active animation overriding, physics sim controlling, hidden, unit mismatch
- **Error Handling**: Not found error; validation error; transform lock error

### FR-OBJ-004: Set Material

- **Description**: Assign existing material or create new PBR material on object
- **Input**: Object ref, material name or slot ref, base color, metallic, roughness, alpha, optional creation/reuse policy
- **Output**: Material result (success, resolved material ref, assigned slot)
- **Rules**: Object must exist + support material slots. PBR properties: base color, metallic, roughness, alpha. Colors normalized from numeric channels or hex. Metallic/roughness/alpha in normalized range. Name exists + reuse enabled → reuse. Name not exist → create. Object without slot → new slot created. Slot ref provided → assign to that slot; omitted → active/first slot. Shared material linked across objects not modified unless explicitly allowed. Returns resolved ref + slot.
- **Edge Cases**: Not found, object type without slots, invalid color/out-of-range values, missing name, slot conflict, linked shared material, unsupported shading model, material limit
- **Error Handling**: Not found error; validation error; material assignment error

### FR-OBJ-005: Manage Modifiers

- **Description**: Add/configure/remove modifiers on object
- **Input**: Object ref, modifier type/name/params/action
- **Output**: Modifier result (success, resolved modifier ref, action summary)
- **Rules**: Object must exist + support modifiers. Type valid for target object type. Params satisfy type-specific schema. Actions: add/configure/remove. Name exists + configure → update. Name not exist + add → create. Configure preserves stack position unless specified. Remove detaches without applying. Destructive application = separate explicit action requiring confirmation. Reports destructive vs non-destructive. Respects edit mode constraints + linked data limitations.
- **Edge Cases**: Object type without modifier support, invalid type/params, stack order conflict, missing dependent modifier, incompatible edit mode, linked/proxy data not editable, unavailable in runtime, destructive without confirmation
- **Error Handling**: Not found error; validation error; modifier compatibility error; confirmation error

### FR-OBJ-006: Delete Object

- **Description**: Remove single object from scene (bulk cleanup → scene feature)
- **Input**: Object ref, optional confirmation flag, child/dependent handling policy
- **Output**: Deletion result (success, deleted ref)
- **Rules**: Exactly one object. Must exist + resolvable. Protected categories require confirmation: active camera, sole camera, marked protected, inside protected collections. Child policy: delete hierarchy/detach/reject. Dependent policy: ignore/reject/remove direct. Removed from all collections before final removal. Linked/instanced: remove instances, preserve shared data unless explicitly allowed. Non-idempotent by default (optional idempotent policy may return success for missing object). Returns deleted ref.
- **Edge Cases**: Not found, protected without confirmation, active/sole camera, children, used as constraint target, linked/instanced/multi-user, hidden/locked collection, last object in scene
- **Error Handling**: Not found error; deletion protection error; validation error; scene state error

### FR-OBJ-007: Get Object Info

- **Description**: Retrieve detailed structured object information
- **Input**: Object ref, optional detail level
- **Output**: Object information (success, object state representation)
- **Rules**: Must exist + resolvable. State: name, unique ref, type, transform, visibility, parent, collections, materials, modifiers. Optional mesh statistics for mesh objects at request. Read-only + idempotent. Safe serialization (no cyclic refs). Capability flags for supported operations. Large object data respects detail level to avoid oversized response.
- **Edge Cases**: Not found, stale ref, very large mesh, unsupported data type, circular parent, missing data blocks, object changed after ref captured
- **Error Handling**: Not found error; serialization error for unsafe cyclic data; detail level reduction for oversized data

## Boundary: Object vs Scene

Object: single-object technical ops (one per request, precise ref resolution, low-level deletion). Scene: scene-level/bulk ops (inspection, preservation policy, bulk cleanup filtering, reporting). Scene decides which objects to remove; object executes each removal safely.

## Boundary: Object vs Render

Object: generic transform on any object including cameras (location/rotation/scale). Render: camera-specific setup (lens, focal length, framing, active camera, depth of field). Higher layers compose render camera config for optical setup + object transform for positional adjustment.

## Error Categories

- object not found — invalid/missing/stale ref
- ambiguous reference — multiple matches
- transform lock — channel constrained/locked
- validation error — invalid params
- material assignment — incompatible type or slot
- modifier compatibility — unsupported for object type/runtime
- deletion protection — protected object without confirmation
- scene state — condition blocks operation
- confirmation error — destructive without required confirmation

## Events

- object created (primitive + generated name + ref)
- object placed (target transform)
- object transformed (final transform summary)
- material assigned (resolved slot)
- modifier updated (add/configure/remove/apply)
- object deleted (deleted ref)

Payloads: category, object ref + name, operation summary, tracking ID, duration, warning summary. Never: full mesh data, oversized dumps, sensitive paths, secrets.

## Configuration Keys

| Key | Description | Default |
|---|---|---|
| default_primitive_type | When request omits type | cube |
| transform_unit_convention | Location/rotation interpretation | Scene units, radians |
| naming_policy | Duplicate handling | auto unique suffix |
| zero_scale_policy | Accept zero scale components | Rejected |
| material_reuse_policy | Reuse existing material by name | Reuse enabled |
| destructive_modifier_confirmation | Require confirmation | Enabled |
| protected_deletion_confirmation | Require confirmation for protected | Enabled |
| transform_override_allowed | Override locked channels explicitly | Disabled |

## QA Checklist

- [ ] Place existing object at target transform succeeds
- [ ] Not-yet-imported → guidance to asset feature
- [ ] Ambiguous ref → ambiguous reference error
- [ ] Each supported primitive type creates correctly
- [ ] Default type applied when omitted
- [ ] Duplicate name handled per policy; zero/negative size rejected
- [ ] Set transform: absolute + relative modes; omitted components preserved
- [ ] Locked channel → transform lock error; non-finite → validation error
- [ ] Assign PBR material: reuse if exists, create if not, create slot if none
- [ ] Out-of-range values → validation error; shared material not modified unless allowed
- [ ] Add/configure/remove modifier; destructive apply requires confirmation
- [ ] Incompatible type → modifier compatibility error
- [ ] Single delete succeeds; bulk → scene feature
- [ ] Protected object requires confirmation; child/dependent policy respected
- [ ] Linked instance: removed, shared data preserved
- [ ] Get object info: name, type, transform, materials, modifiers
- [ ] Detail level respected for large mesh; safe serialization
- [ ] No overlap with asset (import), scene (bulk cleanup), render (camera optics)
- [ ] All 6 events emitted
