# FRD — Object Management Feature

## Purpose

Manages 3D objects that already exist in the scene for **blender-arwaky**.

This feature is the single authority for single-object technical operations: creating primitives, placing existing objects, transforming objects, assigning materials, managing modifiers, deleting individual objects, and inspecting object state. It validates object-level requests, resolves object references deterministically, enforces naming and protection policies, and delegates execution to Blender through the gateway feature.

Bulk scene decisions, asset acquisition, and camera-specific rendering setup belong to other features. The object feature executes precise, well-defined operations on one object at a time.

## Scope

- Create primitive objects from supported catalog
- Place existing object at target transform
- Transform object location, rotation, and scale
- Material assignment with PBR material properties
- Modifier management: add, remove, configure
- Delete single object with protection policy
- Get detailed object information
- Deterministic object reference resolution
- Naming policy enforcement
- Locked transform channel handling
- Linked and instanced object safety
- Object lifecycle observability events

## Out of Scope

- Asset download, owned by asset feature
- Asset import, owned by asset feature
- Scene cleanup bulk operations, owned by scene feature
- Render execution, owned by render feature
- Camera lens and framing setup, owned by render feature
- HDRI environment lighting, owned by render feature
- Queue management, owned by gateway feature
- Background task lifecycle, owned by job feature
- Scene-wide inspection and reporting
- Viewport capture and output artifacts

## Depends On

- gateway feature for Blender command transport and scene-mutating serialization
- config feature for naming policy, unit convention, primitive defaults, and protection rules
- security policy feature for destructive confirmation guidance and redaction

## Provides To

- dispatcher feature
- scene feature, which delegates individual deletions during bulk cleanup

## Functional Requirements

### FR-OBJ-001: Place Existing Object

Place existing object reference. If asset not yet imported, caller must use asset feature first.

- **Description**: Position an object that already exists in the scene at a specified transform
- **Input**: Object reference concept, target location, target rotation, target scale, optional placement policy
- **Output**: Placement result concept containing success indicator, resolved object reference, final transform summary, and message
- **Business Rules**:
  - Target object must already exist in the scene
  - If the asset has not yet been imported, operation must be rejected with guidance that asset feature handles import
  - Object reference resolution must be deterministic:
    - prefer unique object identifier when available
    - fall back to exact object name
    - fall back to qualified path or collection context when supported
  - Ambiguous reference matching multiple objects must produce ambiguous reference error
  - Transform values must be finite three-component vectors
  - Rotation interpretation follows object rotation mode or scene default convention
  - Zero scale components are rejected unless explicitly allowed by configured policy
  - Placement preserves object identity and does not rename or duplicate the object
  - Placement is idempotent for identical object reference and target transform
  - Locked transform channels are respected unless explicit override is allowed
  - Result must reflect the resolved object and final transform after placement
- **Edge Cases**: Object not found, asset not yet imported, ambiguous reference, invalid coordinates, non-finite values, zero scale, locked transform channels, hidden object, object inside protected collection, instanced object, linked object, unit mismatch, stale object reference
- **Error Handling**: Object not found error for invalid reference; ambiguous reference error for multiple matches; validation error for invalid transform values; transform lock error when locked channel cannot be modified

### FR-OBJ-002: Create Primitive

Create primitive object (cube, sphere, plane, etc.) at specified location.

- **Description**: Create a basic object from the supported primitive catalog at a requested transform
- **Input**: Primitive type, location, optional name, optional size, optional rotation and scale, optional target collection
- **Output**: Creation result concept containing success indicator, resolved object reference, generated object name, and message
- **Business Rules**:
  - Primitive type must be included in supported primitive catalog
  - Supported mesh primitives include at least cube, sphere, cylinder, plane, cone, and torus
  - Basic non-mesh object types such as empty, camera, and light may be supported as primitive object categories
  - Default primitive type applies when request omits type and default is configured
  - Requested name must be unique or resolved through configured naming policy:
    - reject duplicate name
    - automatically generate unique suffix
    - overwrite existing object when explicitly allowed
  - Size must be positive and finite unless primitive type defines special rules
  - Created object must be added to active scene and default or specified target collection
  - Initial transform must be applied as requested
  - Result must return canonical object reference and generated name after creation
  - Creation must report adjusted name when naming policy modifies requested name
- **Edge Cases**: Invalid primitive type, duplicate name, zero size, negative size, non-finite transform values, missing target collection, creation not permitted in current mode, object limit reached, unsupported primitive in current runtime, naming policy conflict
- **Error Handling**: Validation error for invalid primitive type or parameters; scene state error for missing target collection; naming conflict resolved only through configured policy

### FR-OBJ-003: Set Transform

Set object location, rotation, and scale.

- **Description**: Modify location, rotation, or scale of an existing object with absolute or relative semantics
- **Input**: Object reference, optional location, optional rotation, optional scale, optional transform mode
- **Output**: Transform result concept containing success indicator, final transform summary, and message
- **Business Rules**:
  - Object must exist and be resolvable through deterministic reference resolution
  - Transform values must be finite three-component vectors
  - Rotation representation must be interpreted according to object rotation mode or request metadata
  - Transform values follow configured unit convention for location and rotation
  - Operation supports absolute and relative transform modes
  - Omitted transform components preserve existing values
  - Locked transform channels are respected unless explicit override is allowed
  - Operation is idempotent for identical absolute transform values
  - Result must return final resolved transform after update
  - Transform update must not modify shared object data unless explicitly intended
  - Constrained or animated objects may accept transform update with warning when constraint or animation is expected to override result
- **Edge Cases**: Object not found, invalid transform values, non-finite values, locked transform channels, constrained object, instanced object, linked object data, active animation overriding transform, physics simulation controlling transform, hidden or disabled object, unit convention mismatch
- **Error Handling**: Object not found error for invalid reference; validation error for invalid transform values; transform lock error when locked channel cannot be modified without override

### FR-OBJ-004: Set Material

Assign material to object. Support PBR material properties.

- **Description**: Assign an existing material or create a new one with PBR properties and attach it to an object slot
- **Input**: Object reference, material name or material slot reference, base color, metallic, roughness, alpha, optional material creation and reuse policy
- **Output**: Material result concept containing success indicator, resolved material reference, assigned material slot, and message
- **Business Rules**:
  - Object must exist and support material slots
  - Supported PBR material properties include at least base color, metallic, roughness, and alpha
  - Color values must be normalized internally when provided as numeric channels or hex-like representation
  - Metallic, roughness, and alpha values must be within normalized range
  - If material name already exists and reuse policy is enabled, existing material is reused
  - If material name does not exist, new material is created
  - If object has no material slot, new slot is created
  - If material slot reference is provided, material is assigned to that slot
  - If no slot reference is provided, material is assigned to active or first available slot
  - Shared material linked across multiple objects must not be modified unless explicitly allowed
  - Result must return resolved material reference and assigned slot
- **Edge Cases**: Object not found, object type without material slots, invalid color values, out-of-range metallic or roughness, out-of-range alpha, missing material name, material slot conflict, shared material linked across objects, unsupported shading model, material limit reached
- **Error Handling**: Object not found error for invalid reference; validation error for invalid material properties; material assignment error for incompatible object type

### FR-OBJ-005: Manage Modifiers

Add, remove, or configure modifiers on object.

- **Description**: Add new modifiers, configure existing modifiers, or remove modifiers from an object
- **Input**: Object reference, modifier type, optional modifier name, modifier parameters, optional modifier action
- **Output**: Modifier result concept containing success indicator, resolved modifier reference, applied action summary, and message
- **Business Rules**:
  - Object must exist and support modifiers
  - Modifier type must be valid for target object type
  - Modifier parameters must satisfy type-specific parameter schema
  - Supported modifier actions include add, configure, and remove
  - If modifier name already exists, configure action updates existing modifier
  - If modifier name does not exist, add action creates new modifier
  - Configure action preserves modifier stack position unless otherwise specified
  - Remove action detaches modifier without applying it
  - Destructive application of modifier is a separate explicit action requiring confirmation when enforced by policy
  - Result should report whether modifier remains non-destructive or was applied destructively
  - Modifier operation must respect object edit mode constraints and linked data limitations
- **Edge Cases**: Object type without modifier support, invalid modifier type, invalid modifier parameters, modifier stack order conflict, dependent modifier missing, object in incompatible edit mode, linked or proxy data not editable, modifier unavailable in current runtime, destructive application without confirmation
- **Error Handling**: Object not found error for invalid reference; validation error for invalid modifier type or parameters; modifier compatibility error for unsupported object type; confirmation error for destructive application without required confirmation

### FR-OBJ-006: Delete Object

Delete single object from scene. For bulk cleanup, use scene feature.

- **Description**: Remove one object from the scene with protection and dependency handling
- **Input**: Object reference, optional confirmation flag, optional child handling policy, optional dependent handling policy
- **Output**: Deletion result concept containing success indicator, deleted object reference, and message
- **Business Rules**:
  - Operation deletes exactly one object; bulk removal belongs to scene feature
  - Object must exist and be resolvable through deterministic reference resolution
  - Protected object categories require explicit confirmation when enforced by policy:
    - active camera
    - sole camera
    - objects marked protected
    - objects inside protected collections
  - Child handling policy may be one of:
    - delete hierarchy
    - detach children
    - reject deletion when children exist
  - Dependent handling policy may be one of:
    - ignore dependents
    - reject deletion when dependents exist
    - remove direct dependents when safe
  - Object must be removed from all collections before final removal when required by runtime behavior
  - Linked and instanced objects must be removed as instances while preserving shared data unless policy explicitly allows shared data removal
  - Deletion is non-idempotent by default; optional idempotent deletion policy may return success for missing object
  - Result must return deleted object reference
- **Edge Cases**: Object not found, protected object without confirmation, active camera, sole camera, object with children, object used as constraint target, linked object, instanced object, multi-user object data, object in hidden or locked collection, last object in scene
- **Error Handling**: Object not found error for invalid reference; deletion protection error for protected object without confirmation; validation error for invalid policy combination; scene state error when dependents block deletion under reject policy

### FR-OBJ-007: Get Object Info

Return detailed information about object: name, type, transform, materials, modifiers.

- **Description**: Retrieve detailed structured information about a specific object
- **Input**: Object reference, optional detail level
- **Output**: Object information result concept containing success indicator and object state representation
- **Business Rules**:
  - Object must exist and be resolvable through deterministic reference resolution
  - Object state representation must include at least:
    - object name
    - unique object reference when available
    - object type
    - transform state
    - visibility state
    - parent relationship
    - collection membership
    - material references
    - modifier summaries
  - Optional mesh statistics may be included for mesh objects when detail level requests it
  - Operation is read-only and idempotent
  - Response must serialize safely and avoid cyclic references
  - Response may include capability flags indicating supported operations for the object
  - Large object data should respect detail level to avoid oversized response
- **Edge Cases**: Object not found, stale object reference, object with very large mesh, object with unsupported data type, circular parent relationships, missing data blocks, object changed after reference captured
- **Error Handling**: Object not found error for invalid reference; serialization error for unsafe cyclic data; detail level reduction applied for oversized object data before failure

## Boundary: Object vs Scene

- Object feature owns single object technical operations:

  - one object per request
  - precise reference resolution
  - low-level deletion execution
  - object-level hierarchy and dependent handling as directed by policy
- Scene feature owns scene-level and bulk operations:

  - scene-wide inspection
  - preservation policy decisions
  - bulk cleanup filtering
  - cleanup reporting

Conceptual separation:

- Single object deletion is requested through the object feature delete operation
- Bulk cleanup with camera preservation is requested through the scene feature cleanup operation, which resolves preservation policy and delegates each individual deletion to the object feature

The scene feature decides which objects should be removed. The object feature executes each removal safely.

## Boundary: Object vs Render

- Object feature owns generic transform on any object, including camera objects:

  - location, rotation, and scale updates
  - no camera-specific optics or framing logic
- Render feature owns camera-specific setup:

  - lens and focal length configuration
  - framing and targeting behavior
  - active camera selection
  - depth of field configuration

Conceptual separation:

- Camera workflow such as lens, framing, and active camera selection is requested through the render feature camera configuration operation
- Direct generic transform of a camera object is requested through the object feature transform operation

When both are needed, higher layers compose render camera configuration for optical setup and object transform for positional adjustment.

## Error Categories

- object not found error — object reference invalid, missing, or stale
- ambiguous reference error — object reference matches multiple objects
- transform lock error — transform channel constrained or locked against modification
- validation error — invalid transform, material, modifier, or naming parameters
- material assignment error — object incompatible with material slots or assignment target
- modifier compatibility error — modifier unsupported for object type or runtime
- deletion protection error — protected object deletion attempted without confirmation
- scene state error — scene condition blocks operation, such as missing collection or blocking dependents
- confirmation error — destructive operation attempted without required confirmation

## Events

- object created event — primitive created with generated name and reference
- object placed event — existing object placed at target transform
- object transformed event — transform applied with final transform summary
- material assigned event — material assigned or created with resolved slot
- modifier updated event — modifier added, configured, removed, or applied
- object deleted event — single object removed with deleted reference

Event payloads should include:

- event category
- object reference and object name
- operation summary such as primitive type, modifier action, or material reference
- tracking identifier when available
- duration metadata
- warning summary when applicable

Event payloads must avoid:

- full mesh data
- oversized object dumps
- sensitive filesystem paths
- secret values

## Configuration Keys


| Configuration Concept             | Description                                                              | Typical Default                             |
| ----------------------------------- | -------------------------------------------------------------------------- | --------------------------------------------- |
| Default primitive type            | Primitive used when request omits type                                   | Cube                                        |
| Transform unit convention         | Unit interpretation for location and rotation values                     | Scene unit system with radians for rotation |
| Naming policy                     | Handling of duplicate or requested object names                          | Automatic unique suffix                     |
| Zero scale policy                 | Whether zero scale components are accepted                               | Rejected                                    |
| Material reuse policy             | Whether existing material with same name is reused                       | Reuse enabled                               |
| Destructive modifier confirmation | Whether destructive modifier application requires confirmation           | Enabled                                     |
| Protected deletion confirmation   | Whether protected object categories require confirmation before deletion | Enabled                                     |
| Transform override allowed        | Whether locked transform channels may be overridden explicitly           | Disabled                                    |

## QA Checklist

- [ ]  Place existing object at target transform succeeds
- [ ]  Place operation rejects not-yet-imported asset with guidance toward asset feature
- [ ]  Ambiguous object reference produces ambiguous reference error
- [ ]  Create primitive at location succeeds for each supported primitive type
- [ ]  Default primitive type applied when request omits type
- [ ]  Duplicate primitive name handled according to naming policy
- [ ]  Zero and negative primitive size rejected
- [ ]  Set transform applies location, rotation, and scale
- [ ]  Set transform preserves omitted components
- [ ]  Set transform relative mode updates correctly
- [ ]  Locked transform channel produces transform lock error without override
- [ ]  Non-finite transform values rejected with validation error
- [ ]  Assign material with PBR properties succeeds
- [ ]  Existing material reused when reuse policy enabled
- [ ]  New material created when name does not exist
- [ ]  Material slot created for object without slots
- [ ]  Out-of-range material values rejected with validation error
- [ ]  Shared material not modified unless explicitly allowed
- [ ]  Add modifier to compatible object succeeds
- [ ]  Configure existing modifier preserves stack position
- [ ]  Remove modifier detaches without applying
- [ ]  Destructive modifier application requires confirmation
- [ ]  Incompatible object type produces modifier compatibility error
- [ ]  Delete single object succeeds and returns deleted reference
- [ ]  Bulk cleanup delegated to scene feature, not object feature
- [ ]  Protected object deletion requires confirmation
- [ ]  Child handling policy respected during deletion
- [ ]  Linked object instance removed while shared data preserved
- [ ]  Get object info returns name, type, transform, materials, and modifiers
- [ ]  Get object info respects detail level for large mesh
- [ ]  Get object info serializes safely without cyclic references
- [ ]  No overlap with asset feature for import
- [ ]  No overlap with scene feature for bulk cleanup
- [ ]  No overlap with render feature for camera-specific setup
- [ ]  Object lifecycle events emitted for creation, placement, transform, material, modifier, and deletion
