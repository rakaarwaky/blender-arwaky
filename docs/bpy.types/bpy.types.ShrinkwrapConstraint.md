# bpy.types.ShrinkwrapConstraint

# ShrinkwrapConstraint(Constraint)

 

base classes — [`bpy_struct`](bpy.types.bpy_struct.html#bpy.types.bpy_struct), [`Constraint`](bpy.types.Constraint.html#bpy.types.Constraint)

   class bpy.types.ShrinkwrapConstraint(Constraint) 

Create constraint-based shrinkwrap relationship

   cull_face 

Stop vertices from projecting to a face on the target when facing towards/away (default `'OFF'`)

  
- `OFF` Off – No culling. 
- `FRONT` Front – No projection when in front of the face. 
- `BACK` Back – No projection when behind the face.   Type: 

Literal[‘OFF’, ‘FRONT’, ‘BACK’]

      distance 

Distance to Target (in [0, inf], default 0.0)

  Type: 

float

      project_axis 

Axis constrain to (default `'POS_X'`)

  Type: 

Literal[[Object Axis Items](bpy_types_enum_items/object_axis_items.html#rna-enum-object-axis-items)]

      project_axis_space 

Space for the projection axis (default `'WORLD'`)

  
- `WORLD` World Space – The constraint is applied relative to the world coordinate system. 
- `CUSTOM` Custom Space – The constraint is applied in local space of a custom object/bone/vertex group. 
- `POSE` Pose Space – The constraint is applied in Pose Space, the object transformation is ignored. 
- `LOCAL_WITH_PARENT` Local With Parent – The constraint is applied relative to the rest pose local coordinate system of the bone, thus including the parent-induced transformation. 
- `LOCAL` Local Space – The constraint is applied relative to the local coordinate system of the object.   Type: 

Literal[‘WORLD’, ‘CUSTOM’, ‘POSE’, ‘LOCAL_WITH_PARENT’, ‘LOCAL’]

      project_limit 

Limit the distance used for projection (zero disables) (in [0, inf], default 0.0)

  Type: 

float

      shrinkwrap_type 

Select type of shrinkwrap algorithm for target position (default `'NEAREST_SURFACE'`)

  
- `NEAREST_SURFACE` Nearest Surface Point – Shrink the location to the nearest target surface. 
- `PROJECT` Project – Shrink the location to the nearest target surface along a given axis. 
- `NEAREST_VERTEX` Nearest Vertex – Shrink the location to the nearest target vertex. 
- `TARGET_PROJECT` Target Normal Project – Shrink the location to the nearest target surface along the interpolated vertex normals of the target.   Type: 

Literal[‘NEAREST_SURFACE’, ‘PROJECT’, ‘NEAREST_VERTEX’, ‘TARGET_PROJECT’]

      target 

Target Mesh object

  Type: 

[`Object`](bpy.types.Object.html#bpy.types.Object) | None

      track_axis 

Axis that is aligned to the normal (default `'TRACK_X'`)

  Type: 

Literal[‘TRACK_X’, ‘TRACK_Y’, ‘TRACK_Z’, ‘TRACK_NEGATIVE_X’, ‘TRACK_NEGATIVE_Y’, ‘TRACK_NEGATIVE_Z’]

      use_invert_cull 

When projecting in the opposite direction invert the face cull mode (default False)

  Type: 

bool

      use_project_opposite 

Project in both specified and opposite directions (default False)

  Type: 

bool

      use_track_normal 

Align the specified axis to the surface normal (default False)

  Type: 

bool

      wrap_mode 

Select how to constrain the object to the target surface (default `'ON_SURFACE'`)

  Type: 

Literal[[Modifier Shrinkwrap Mode Items](bpy_types_enum_items/modifier_shrinkwrap_mode_items.html#rna-enum-modifier-shrinkwrap-mode-items)]

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
- [`Constraint.name`](bpy.types.Constraint.html#bpy.types.Constraint.name) 
- [`Constraint.type`](bpy.types.Constraint.html#bpy.types.Constraint.type) 
- [`Constraint.is_override_data`](bpy.types.Constraint.html#bpy.types.Constraint.is_override_data) 
- [`Constraint.owner_space`](bpy.types.Constraint.html#bpy.types.Constraint.owner_space) 
- [`Constraint.target_space`](bpy.types.Constraint.html#bpy.types.Constraint.target_space) 
- [`Constraint.space_object`](bpy.types.Constraint.html#bpy.types.Constraint.space_object) 
- [`Constraint.space_subtarget`](bpy.types.Constraint.html#bpy.types.Constraint.space_subtarget)   
- [`Constraint.mute`](bpy.types.Constraint.html#bpy.types.Constraint.mute) 
- [`Constraint.enabled`](bpy.types.Constraint.html#bpy.types.Constraint.enabled) 
- [`Constraint.show_expanded`](bpy.types.Constraint.html#bpy.types.Constraint.show_expanded) 
- [`Constraint.is_valid`](bpy.types.Constraint.html#bpy.types.Constraint.is_valid) 
- [`Constraint.active`](bpy.types.Constraint.html#bpy.types.Constraint.active) 
- [`Constraint.influence`](bpy.types.Constraint.html#bpy.types.Constraint.influence) 
- [`Constraint.error_location`](bpy.types.Constraint.html#bpy.types.Constraint.error_location) 
- [`Constraint.error_rotation`](bpy.types.Constraint.html#bpy.types.Constraint.error_rotation)     

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
- [`Constraint.bl_rna_get_subclass`](bpy.types.Constraint.html#bpy.types.Constraint.bl_rna_get_subclass) 
- [`Constraint.bl_rna_get_subclass_py`](bpy.types.Constraint.html#bpy.types.Constraint.bl_rna_get_subclass_py)
