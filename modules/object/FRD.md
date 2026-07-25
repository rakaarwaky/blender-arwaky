# FRD — object (Object Feature Module)

## System Overview

The object module handles all Blender object operations for **blender-arwaky** — it  handle object manipulaion like  creation, transformation, material assignment, modifier management, deletion, object inspection.

The module covers:

- placing existing objects or previously imported assets
- creating primitive objects
- updating object transforms
- assigning or creating materials
- adding, updating, removing, or applying modifiers
- deleting objects safely
- retrieving object information

The module does not handle:

- asset file import or export
- network communication with Blender
- rendering operations
- global scene environment setup
- long-running job tracking beyond delegating operation status

## Functional Requirements

### FR-OBJ-001: Place Asset in Scene

- **Description**: Position an existing scene object or previously imported asset at specified coordinates in the scene
- **Input**: Object reference or imported asset reference, target location, target rotation, target scale, placement policy
- **Output**: Placement result containing success indicator, resolved object reference, final transform summary, and message
- **Business Rules**:
  - Target object must already exist in the scene or be resolvable through an imported asset reference
  - If the asset has not yet been imported, the request must either be rejected or delegated to the asset module depending on configuration
  - Coordinates must be valid finite three-component vector values
  - Rotation interpretation follows the object rotation mode or scene default rotation convention
  - Scale values must be finite and non-zero unless zero scale is explicitly allowed by policy
  - Object resolution must be deterministic:
    - prefer unique object identifier when available
    - fall back to exact object name
    - fall back to qualified object path or collection context when supported
  - If object reference is ambiguous, return an ambiguity error
  - Placement operation should preserve object identity unless overwrite policy is specified
  - Placement operation should be idempotent when the same object reference and target transform are supplied
  - Final object name or reference returned must reflect the resolved object after placement
- **Edge Cases**: Object not found, imported asset not yet present, ambiguous object reference, invalid coordinates, non-finite numeric values, zero scale, locked transform channels, hidden object, object inside protected collection, instanced object, linked object, unit mismatch, stale object reference
- **Error Handling**: Scene validation error for missing objects; request validation error for invalid parameters; ambiguity error for multiple matching objects; delegated server error for Blender execution failure

### FR-OBJ-002: Create Primitive Object

- **Description**: Create a basic geometric or scene primitive from the supported primitive catalog
- **Input**: Primitive type, location, optional name, optional size, optional rotation, optional scale, optional target collection
- **Output**: Creation result containing success indicator, resolved object reference, generated object name, and message
- **Business Rules**:
  - Primitive type must be included in the supported primitive catalog
  - Supported primitive catalog includes at least basic mesh primitives such as cube, sphere, cylinder, plane, cone, and torus
  - Basic non-mesh object types such as empty, camera, and light may also be supported as primitive object categories
  - Requested object name must be unique or resolved through naming policy
  - Naming policy may be one of:
    - reject duplicate name
    - automatically generate unique suffix
    - overwrite existing object when explicitly allowed
  - Size must be positive and finite unless primitive type defines special rules
  - Created object must be added to the active scene and to the default or specified target collection
  - Initial transform must be applied as requested
  - Operation must return the canonical object reference after creation
  - Operation should report generated name when requested name is adjusted automatically
- **Edge Cases**: Invalid primitive type, duplicate name, zero size, negative size, non-finite transform values, missing target collection, creation not permitted in current editor mode, object limit reached, memory failure, unsupported primitive in current Blender version
- **Error Handling**: Request validation error for invalid parameters; scene validation error for missing target collection; delegated server error for Blender execution failure

### FR-OBJ-003: Set Object Transform

- **Description**: Modify location, rotation, or scale of an existing object
- **Input**: Object reference, optional location, optional rotation, optional scale, optional transform mode
- **Output**: Transform result containing success indicator, final transform summary, and message
- **Business Rules**:
  - Object must exist and be resolvable
  - Transform values must be valid finite three-component vectors
  - Rotation representation must be interpreted according to object rotation mode or request metadata
  - Operation may support absolute and relative transform modes
  - If a transform component is omitted, existing value must be preserved
  - Locked transform channels should be respected unless explicit override is allowed
  - Operation should be idempotent for identical absolute transform values
  - Operation should return final resolved transform after update
  - Transform update should not modify shared object data unless explicitly intended
- **Edge Cases**: Object not found, invalid transform values, non-finite values, locked transform channels, constrained object, instanced object, linked object data, active animation overriding transform, physics simulation controlling transform, object hidden or disabled in viewport
- **Error Handling**: Scene validation error for missing objects; request validation error for invalid transform values; transform lock error when locked channel cannot be modified; delegated server error for Blender execution failure

### FR-OBJ-004: Set Material

- **Description**: Assign or create a material for an object
- **Input**: Object reference, material name or material slot reference, base color, metallic, roughness, alpha, material creation and reuse policy
- **Output**: Material result containing success indicator, resolved material reference, assigned material slot, and message
- **Business Rules**:
  - Object must exist and support material slots
  - Material properties must be within valid normalized ranges
  - Color values must be normalized internally when provided as numeric channels or hex-like representation
  - Metallic and roughness values must be within normalized range
  - Alpha value must be within normalized range
  - If material name already exists and reuse policy is enabled, reuse existing material
  - If material name does not exist, create new material
  - If object has no material slot, create a new slot
  - If material slot reference is provided, assign material to that slot
  - If no slot reference is provided, assign to active or first available slot
  - Operation should not modify shared material data unless explicitly allowed
  - Operation should return resolved material reference and assigned slot
- **Edge Cases**: Object not found, object type does not support material slots, invalid color values, out-of-range metallic or roughness values, missing material name, material slot conflict, shared material linked across multiple objects, unsupported shading model, material limit reached
- **Error Handling**: Scene validation error for missing objects; request validation error for invalid material properties; material assignment error for incompatible object; delegated server error for Blender execution failure

### FR-OBJ-005: Apply Modifier

- **Description**: Add, update, remove, or apply a modifier on an object
- **Input**: Object reference, modifier type, optional modifier name, modifier parameters, optional modifier action
- **Output**: Modifier result containing success indicator, resolved modifier reference, applied action summary, and message
- **Business Rules**:
  - Object must exist and support modifiers
  - Modifier type must be valid for the target object type
  - Modifier parameters must satisfy type-specific parameter schema
  - If modifier name already exists, update existing modifier by default
  - If modifier name does not exist, add new modifier
  - Supported modifier actions may include:
    - add
    - update
    - remove
    - apply destructively
  - Destructive apply action must be explicitly requested
  - Destructive apply action may require confirmation policy depending on configuration
  - Operation should respect object visibility, edit mode constraints, and modifier stack order
  - Operation should report whether modifier remains non-destructive or was applied destructively
  - Operation should preserve modifier stack position when updating existing modifier unless otherwise specified
- **Edge Cases**: Object type does not support modifiers, invalid modifier type, invalid modifier parameters, modifier stack order conflict, dependent modifier missing, destructive apply changes geometry irreversibly, object in incompatible edit mode, linked or proxy data not editable, modifier not available in current Blender version
- **Error Handling**: Scene validation error for incompatible objects; request validation error for invalid modifier parameters; destructive action confirmation error when confirmation is required but not provided; delegated server error for Blender execution failure

### FR-OBJ-006: Delete Object

- **Description**: Remove an object from the scene
- **Input**: Object reference or object filter, deletion policy, confirmation flag for protected object categories
- **Output**: Deletion result containing success indicator, deleted object references, and message
- **Business Rules**:
  - Object must exist and be resolvable
  - Deletion may target a single object or a filtered set of objects
  - Protected object categories such as active camera, sole camera, lights, or objects marked protected require explicit confirmation
  - Deletion policy defines behavior for children and dependents:
    - delete hierarchy
    - detach children
    - reject deletion when dependents exist
  - Operation should remove object from all relevant collections before final removal when required by Blender runtime behavior
  - Operation should not delete an entire scene unless explicitly requested and confirmed
  - Deletion is non-idempotent by default
  - If idempotent deletion policy is enabled, deleting a missing object may return success
  - Operation should return references of successfully deleted objects
- **Edge Cases**: Object not found, last object in scene, linked objects, instanced objects, protected object, active camera, object used as constraint target, object with children, object in hidden or locked collection, multi-user object data, object referenced by other scene entities
- **Error Handling**: Scene validation error for missing objects; deletion protection error for protected object without confirmation; request validation error for invalid object filter; delegated server error for Blender execution failure

### FR-OBJ-007: Get Object Info

- **Description**: Retrieve detailed information about a specific object
- **Input**: Object reference, optional detail level
- **Output**: Object information result containing success indicator and object domain representation
- **Business Rules**:
  - Object must exist and be resolvable
  - Returned object domain representation must include at least:
    - object name
    - unique object identifier when available
    - object type
    - transform state
    - visibility state
    - parent relationship
    - collection membership
    - material references
    - modifier summaries
  - Optional mesh statistics may be included for mesh objects when detail level requests it
  - Operation is read-only and idempotent
  - Response must avoid cyclic references and must serialize safely
  - Response may include capability flags indicating supported operations for the object
- **Edge Cases**: Object not found, deleted object reference, object with very large mesh, object with unsupported data type, circular parent relationships, missing data blocks, stale reference after scene change, object with complex dependency graph
- **Error Handling**: Scene validation error for missing objects; serialization error for unsafe cyclic data; delegated server error for Blender execution failure

## API Contract


| Operation        | Input                                                          | Output                    | Description                                |
| ------------------ | ---------------------------------------------------------------- | --------------------------- | -------------------------------------------- |
| Place asset      | Object or asset reference, target transform, placement policy  | Placement result          | Position existing object or imported asset |
| Create primitive | Primitive type, transform, naming policy, target collection    | Creation result           | Create geometric or scene primitive        |
| Set transform    | Object reference, transform fields, transform mode             | Transform result          | Modify object transform                    |
| Set material     | Object reference, material properties, slot policy             | Material result           | Assign or create material                  |
| Apply modifier   | Object reference, modifier type, parameters, action            | Modifier result           | Add, update, remove, or apply modifier     |
| Delete object    | Object reference or filter, deletion policy, confirmation flag | Deletion result           | Remove object from scene                   |
| Get object info  | Object reference, detail level                                 | Object information result | Retrieve object details                    |

Common contract behavior:

- All operations return a structured result containing success indicator, human-readable message, and error category when failed
- All operations may accept a request correlation identifier for tracing
- All mutating operations delegate execution to Blender through the server module
- All operations that modify Blender state must respect server-side serialization constraints
- Read-only operations should not require destructive confirmation
- Destructive operations must expose explicit confirmation or policy flags

## Integration Points

- **Internal**:
  - shared module: taxonomy concepts for object reference, transform values, material properties, modifier metadata, result envelope, and error categories
  - server module: Blender connection, operation dispatch, response parsing, queueing, and timeout handling
  - asset module: imported asset reference handoff and asset placement readiness
  - command catalog module: registration of object capabilities, parameter schema, and operation metadata
- **External**:
  - Blender scripting interface — accessed via server module
  - Blender scene data: objects, materials, modifiers, collections, constraints, dependencies, and object data blocks

## Non-functional Requirements

- **Performance**: Standard object operations complete within 2 seconds excluding heavy mesh processing, large asset handling, or server queue wait time
- **Reliability**: Operations fail with categorized errors; no partial success is silently ignored; delegated server communication errors are propagated consistently
- **Consistency**: Object references are resolved deterministically; naming policy is applied consistently; transform and material values are normalized before execution
- **Safety**: Destructive operations require explicit policy or confirmation; protected object categories are guarded; shared data is not modified unintentionally
- **Thread Safety**: Module does not perform concurrent Blender calls directly; relies on server-side serialization due to Blender main-thread constraints
- **Observability**: Log operation type, object reference, result status, duration, and error category; avoid logging sensitive or oversized payload data
- **Portability**: Behavior remains consistent across supported Blender versions where scripting capabilities are available
- **Extensibility**: New primitive types, modifier types, and material properties can be added through configuration or capability registration without modifying core object operation flow

## Test Scenarios / QA Checklist

- [ ]  Place asset at valid coordinates succeeds
- [ ]  Place asset with missing object returns scene validation error
- [ ]  Place asset with ambiguous object reference returns ambiguity error
- [ ]  Place asset with invalid transform values returns request validation error
- [ ]  Place asset with non-finite numeric values returns request validation error
- [ ]  Place asset with zero scale is rejected unless explicitly allowed
- [ ]  Place asset operation is idempotent for same object reference and transform
- [ ]  Create primitive with valid type succeeds
- [ ]  Create primitive with invalid type returns request validation error
- [ ]  Create primitive with duplicate name follows configured naming policy
- [ ]  Create primitive with zero or negative size returns request validation error
- [ ]  Create primitive in missing target collection returns scene validation error
- [ ]  Create primitive returns resolved object reference and generated name
- [ ]  Set transform on existing object succeeds
- [ ]  Set transform on missing object returns scene validation error
- [ ]  Set transform with non-finite values returns request validation error
- [ ]  Set transform respects locked transform channels unless override allowed
- [ ]  Set transform with relative mode updates object correctly
- [ ]  Set transform preserves omitted transform components
- [ ]  Set material on valid object succeeds
- [ ]  Set material creates new material when material does not exist
- [ ]  Set material reuses existing material when reuse policy enabled
- [ ]  Set material with out-of-range values returns request validation error
- [ ]  Set material on object without material slots creates slot
- [ ]  Set material on incompatible object returns material assignment error
- [ ]  Apply modifier to compatible object succeeds
- [ ]  Apply modifier to incompatible object returns scene validation error
- [ ]  Apply modifier with invalid parameters returns request validation error
- [ ]  Update existing modifier succeeds
- [ ]  Remove modifier succeeds
- [ ]  Destructive modifier apply without confirmation returns confirmation error
- [ ]  Delete object succeeds and removes object from scene
- [ ]  Delete missing object returns scene validation error unless idempotent deletion policy enabled
- [ ]  Delete protected object without confirmation returns deletion protection error
- [ ]  Delete object with children follows configured hierarchy policy
- [ ]  Delete active camera without confirmation returns deletion protection error
- [ ]  Delete object used as constraint target handles dependent entities safely
- [ ]  Get info on existing object returns object domain representation
- [ ]  Get info on missing object returns scene validation error
- [ ]  Get info on large object respects detail level and serializes safely
- [ ]  Object operations delegate to server module and propagate server errors
- [ ]  Concurrent object operations are serialized through server-side queue

## Assumptions & Constraints

- Blender 3.0+ or compatible Blender runtime must be running with scripting interface enabled
- Blender bridge or addon component must be enabled and reachable through server module
- Object operations are delegated to Blender via server module
- Import/export operations are handled by asset module
- Blender main-thread constraint requires serialized execution of state-modifying operations
- Object names may not be globally stable; unique identifier should be preferred when available
- Some operations are destructive and require explicit policy or confirmation
- Modifier and material capabilities depend on object type and Blender version
- Large mesh operations may exceed standard performance target
- Object deletion may affect dependent objects, constraints, instances, or hierarchy relationships

## Glossary

- **Object domain representation**: Conceptual entity representing a Blender object with full or partial state
- **Primitive type**: Supported basic geometric or scene object category
- **Three-component vector**: Conceptual 3D value used for location, rotation, or scale
- **Object reference**: Deterministic identifier or name used to resolve a target object
- **Naming policy**: Rule for handling duplicate or requested object names
- **Deletion policy**: Rule for handling children, dependents, and protected objects during deletion
- **Protected object category**: Object category requiring confirmation before destructive operation
- **Modifier action**: Conceptual operation applied to a modifier, such as add, update, remove, or destructive apply
- **Material slot**: Object-level assignment point for material data
- **Object manipulation contract**: Abstraction for object operation capabilities exposed to higher layers

## Reference

- Product Requirements Document for blender-arwaky
- Shared feature requirements documentation
- Server feature requirements documentation
- Asset feature requirements documentation
