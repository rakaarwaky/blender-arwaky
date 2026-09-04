# bpy.types.Constraint

# Constraint(bpy_struct)

 

base class — [`bpy_struct`](bpy.types.bpy_struct.html#bpy.types.bpy_struct)

  

Subclasses

  
- [ActionConstraint(Constraint)](bpy.types.ActionConstraint.html) 
- [ArmatureConstraint(Constraint)](bpy.types.ArmatureConstraint.html) 
- [CameraSolverConstraint(Constraint)](bpy.types.CameraSolverConstraint.html) 
- [ChildOfConstraint(Constraint)](bpy.types.ChildOfConstraint.html) 
- [ClampToConstraint(Constraint)](bpy.types.ClampToConstraint.html) 
- [CopyLocationConstraint(Constraint)](bpy.types.CopyLocationConstraint.html) 
- [CopyRotationConstraint(Constraint)](bpy.types.CopyRotationConstraint.html) 
- [CopyScaleConstraint(Constraint)](bpy.types.CopyScaleConstraint.html) 
- [CopyTransformsConstraint(Constraint)](bpy.types.CopyTransformsConstraint.html) 
- [DampedTrackConstraint(Constraint)](bpy.types.DampedTrackConstraint.html) 
- [FloorConstraint(Constraint)](bpy.types.FloorConstraint.html) 
- [FollowPathConstraint(Constraint)](bpy.types.FollowPathConstraint.html) 
- [FollowTrackConstraint(Constraint)](bpy.types.FollowTrackConstraint.html) 
- [GeometryAttributeConstraint(Constraint)](bpy.types.GeometryAttributeConstraint.html) 
- [KinematicConstraint(Constraint)](bpy.types.KinematicConstraint.html) 
- [LimitDistanceConstraint(Constraint)](bpy.types.LimitDistanceConstraint.html) 
- [LimitLocationConstraint(Constraint)](bpy.types.LimitLocationConstraint.html) 
- [LimitRotationConstraint(Constraint)](bpy.types.LimitRotationConstraint.html) 
- [LimitScaleConstraint(Constraint)](bpy.types.LimitScaleConstraint.html) 
- [LockedTrackConstraint(Constraint)](bpy.types.LockedTrackConstraint.html) 
- [MaintainVolumeConstraint(Constraint)](bpy.types.MaintainVolumeConstraint.html) 
- [ObjectSolverConstraint(Constraint)](bpy.types.ObjectSolverConstraint.html) 
- [PivotConstraint(Constraint)](bpy.types.PivotConstraint.html) 
- [ShrinkwrapConstraint(Constraint)](bpy.types.ShrinkwrapConstraint.html) 
- [SplineIKConstraint(Constraint)](bpy.types.SplineIKConstraint.html) 
- [StretchToConstraint(Constraint)](bpy.types.StretchToConstraint.html) 
- [TrackToConstraint(Constraint)](bpy.types.TrackToConstraint.html) 
- [TransformCacheConstraint(Constraint)](bpy.types.TransformCacheConstraint.html) 
- [TransformConstraint(Constraint)](bpy.types.TransformConstraint.html)     class bpy.types.Constraint(bpy_struct) 

Constraint modifying the transformation of objects and bones

   active 

Constraint is the one being edited (default False)

  Type: 

bool

      enabled 

Use the results of this constraint (default True)

  Type: 

bool

      error_location 

Amount of residual error in Blender space unit for constraints that work on position (in [-inf, inf], default 0.0, readonly)

  Type: 

float

      error_rotation 

Amount of residual error in radians for constraints that work on orientation (in [-inf, inf], default 0.0, readonly)

  Type: 

float

      influence 

Amount of influence constraint will have on the final solution (in [0, 1], default 0.0)

  Type: 

float

      is_override_data 

In a local override object, whether this constraint comes from the linked reference object, or is local to the override (default True, readonly)

  Type: 

bool

      is_valid 

Constraint has valid settings and can be evaluated (default True, readonly)

  Type: 

bool

      mute 

Enable/Disable Constraint (default False)

  Type: 

bool

      name 

Constraint name (default “”, never None)

  Type: 

str

      owner_space 

Space that owner is evaluated in (default `'WORLD'`)

  
- `WORLD` World Space – The constraint is applied relative to the world coordinate system. 
- `CUSTOM` Custom Space – The constraint is applied in local space of a custom object/bone/vertex group. 
- `POSE` Pose Space – The constraint is applied in Pose Space, the object transformation is ignored. 
- `LOCAL_WITH_PARENT` Local With Parent – The constraint is applied relative to the rest pose local coordinate system of the bone, thus including the parent-induced transformation. 
- `LOCAL` Local Space – The constraint is applied relative to the local coordinate system of the object.   Type: 

Literal[‘WORLD’, ‘CUSTOM’, ‘POSE’, ‘LOCAL_WITH_PARENT’, ‘LOCAL’]

      show_expanded 

Constraint’s panel is expanded in UI (default False)

  Type: 

bool

      space_object 

Object for Custom Space

  Type: 

[`Object`](bpy.types.Object.html#bpy.types.Object) | None

      space_subtarget 

Armature bone, mesh or lattice vertex group, … (default “”, never None)

  Type: 

str

      target_space 

Space that target is evaluated in (default `'WORLD'`)

  
- `WORLD` World Space – The transformation of the target is evaluated relative to the world coordinate system. 
- `CUSTOM` Custom Space – The transformation of the target is evaluated relative to a custom object/bone/vertex group. 
- `POSE` Pose Space – The transformation of the target is only evaluated in the Pose Space, the target armature object transformation is ignored. 
- `LOCAL_WITH_PARENT` Local With Parent – The transformation of the target bone is evaluated relative to its rest pose local coordinate system, thus including the parent-induced transformation. 
- `LOCAL` Local Space – The transformation of the target is evaluated relative to its local coordinate system. 
- `LOCAL_OWNER_ORIENT` Local Space (Owner Orientation) – The transformation of the target bone is evaluated relative to its local coordinate system, followed by a correction for the difference in target and owner rest pose orientations. When applied as local transform to the owner produces the same global motion as the target if the parents are still in rest pose..   Type: 

Literal[‘WORLD’, ‘CUSTOM’, ‘POSE’, ‘LOCAL_WITH_PARENT’, ‘LOCAL’, ‘LOCAL_OWNER_ORIENT’]

      type 

(default `'CAMERA_SOLVER'`, readonly)

  Type: 

Literal[[Constraint Type Items](bpy_types_enum_items/constraint_type_items.html#rna-enum-constraint-type-items)]

      classmethod bl_rna_get_subclass(id, default=None, /)  Parameters:  
- id (str) – The RNA type identifier. 
- default ([`bpy.types.Struct`](bpy.types.Struct.html#bpy.types.Struct) | None) – The value to return when not found.   Returns: 

The RNA type or default when not found.

  Return type: 

[`bpy.types.Struct`](bpy.types.Struct.html#bpy.types.Struct)

      classmethod bl_rna_get_subclass_py(id, default=None, /)  Parameters:  
- id (str) – The RNA type identifier. 
- default (type | None) – The value to return when not found.   Returns: 

The class or default when not found.

  Return type: 

type

      

## Inherited Properties

  
- [`bpy_struct.id_data`](bpy.types.bpy_struct.html#bpy.types.bpy_struct.id_data)       

## Inherited Functions

  
- [`bpy_struct.as_pointer`](bpy.types.bpy_struct.html#bpy.types.bpy_struct.as_pointer) 
- [`bpy_struct.driver_add`](bpy.types.bpy_struct.html#bpy.types.bpy_struct.driver_add) 
- [`bpy_struct.driver_remove`](bpy.types.bpy_struct.html#bpy.types.bpy_struct.driver_remove) 
- [`bpy_struct.get`](bpy.types.bpy_struct.html#bpy.types.bpy_struct.get) 
- [`bpy_struct.id_properties_clear`](bpy.types.bpy_struct.html#bpy.types.bpy_struct.id_properties_clear) 
- [`bpy_struct.id_properties_ensure`](bpy.types.bpy_struct.html#bpy.types.bpy_struct.id_properties_ensure) 
- [`bpy_struct.id_properties_ui`](bpy.types.bpy_struct.html#bpy.types.bpy_struct.id_properties_ui) 
- [`bpy_struct.is_property_hidden`](bpy.types.bpy_struct.html#bpy.types.bpy_struct.is_property_hidden) 
- [`bpy_struct.is_property_overridable_library`](bpy.types.bpy_struct.html#bpy.types.bpy_struct.is_property_overridable_library) 
- [`bpy_struct.is_property_readonly`](bpy.types.bpy_struct.html#bpy.types.bpy_struct.is_property_readonly) 
- [`bpy_struct.is_property_set`](bpy.types.bpy_struct.html#bpy.types.bpy_struct.is_property_set) 
- [`bpy_struct.items`](bpy.types.bpy_struct.html#bpy.types.bpy_struct.items)   
- [`bpy_struct.keyframe_delete`](bpy.types.bpy_struct.html#bpy.types.bpy_struct.keyframe_delete) 
- [`bpy_struct.keyframe_insert`](bpy.types.bpy_struct.html#bpy.types.bpy_struct.keyframe_insert) 
- [`bpy_struct.keys`](bpy.types.bpy_struct.html#bpy.types.bpy_struct.keys) 
- [`bpy_struct.path_from_id`](bpy.types.bpy_struct.html#bpy.types.bpy_struct.path_from_id) 
- [`bpy_struct.path_from_module`](bpy.types.bpy_struct.html#bpy.types.bpy_struct.path_from_module) 
- [`bpy_struct.path_resolve`](bpy.types.bpy_struct.html#bpy.types.bpy_struct.path_resolve) 
- [`bpy_struct.pop`](bpy.types.bpy_struct.html#bpy.types.bpy_struct.pop) 
- [`bpy_struct.property_overridable_library_set`](bpy.types.bpy_struct.html#bpy.types.bpy_struct.property_overridable_library_set) 
- [`bpy_struct.property_unset`](bpy.types.bpy_struct.html#bpy.types.bpy_struct.property_unset) 
- [`bpy_struct.rna_ancestors`](bpy.types.bpy_struct.html#bpy.types.bpy_struct.rna_ancestors) 
- [`bpy_struct.type_recast`](bpy.types.bpy_struct.html#bpy.types.bpy_struct.type_recast) 
- [`bpy_struct.values`](bpy.types.bpy_struct.html#bpy.types.bpy_struct.values)     

## References

  
- [`Object.constraints`](bpy.types.Object.html#bpy.types.Object.constraints) 
- [`ObjectConstraints.active`](bpy.types.ObjectConstraints.html#bpy.types.ObjectConstraints.active) 
- [`ObjectConstraints.copy`](bpy.types.ObjectConstraints.html#bpy.types.ObjectConstraints.copy) 
- [`ObjectConstraints.copy`](bpy.types.ObjectConstraints.html#bpy.types.ObjectConstraints.copy) 
- [`ObjectConstraints.new`](bpy.types.ObjectConstraints.html#bpy.types.ObjectConstraints.new) 
- [`ObjectConstraints.remove`](bpy.types.ObjectConstraints.html#bpy.types.ObjectConstraints.remove) 
- [`Panel.custom_data`](bpy.types.Panel.html#bpy.types.Panel.custom_data)   
- [`PoseBone.constraints`](bpy.types.PoseBone.html#bpy.types.PoseBone.constraints) 
- [`PoseBoneConstraints.active`](bpy.types.PoseBoneConstraints.html#bpy.types.PoseBoneConstraints.active) 
- [`PoseBoneConstraints.copy`](bpy.types.PoseBoneConstraints.html#bpy.types.PoseBoneConstraints.copy) 
- [`PoseBoneConstraints.copy`](bpy.types.PoseBoneConstraints.html#bpy.types.PoseBoneConstraints.copy) 
- [`PoseBoneConstraints.new`](bpy.types.PoseBoneConstraints.html#bpy.types.PoseBoneConstraints.new) 
- [`PoseBoneConstraints.remove`](bpy.types.PoseBoneConstraints.html#bpy.types.PoseBoneConstraints.remove) 
- [`UILayout.template_constraint_header`](bpy.types.UILayout.html#bpy.types.UILayout.template_constraint_header)
