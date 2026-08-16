# bpy.types.DriverTarget

# DriverTarget(bpy_struct)

 

base class — [`bpy_struct`](bpy.types.bpy_struct.html#bpy.types.bpy_struct)

   class bpy.types.DriverTarget(bpy_struct) 

Source of input values for driver variables

   bone_target 

Name of PoseBone to use as target (default “”, never None)

  Type: 

str

      context_property 

Type of a context-dependent data-block to access property from (default `'ACTIVE_SCENE'`)

  
- `ACTIVE_SCENE` Active Scene – Currently evaluating scene. 
- `ACTIVE_VIEW_LAYER` Active View Layer – Currently evaluating view layer.   Type: 

Literal[‘ACTIVE_SCENE’, ‘ACTIVE_VIEW_LAYER’]

      data_path 

RNA Path (from ID-block) to property used (default “”, never None)

  Type: 

str

      fallback_value 

The value to use if the data path cannot be resolved (in [-inf, inf], default 0.0)

  Type: 

float

      id 

ID-block that the specific property used can be found from (id_type property must be set first)

  Type: 

[`ID`](bpy.types.ID.html#bpy.types.ID) | None

      id_type 

Type of ID-block that can be used (default `'OBJECT'`)

  Type: 

Literal[[Id Type Items](bpy_types_enum_items/id_type_items.html#rna-enum-id-type-items)]

      is_fallback_used 

Indicates that the most recent variable evaluation used the fallback value (default False, readonly)

  Type: 

bool

      rotation_mode 

Mode for calculating rotation channel values (default `'AUTO'`)

  Type: 

Literal[[Driver Target Rotation Mode Items](bpy_types_enum_items/driver_target_rotation_mode_items.html#rna-enum-driver-target-rotation-mode-items)]

      transform_space 

Space in which transforms are used (default `'WORLD_SPACE'`)

  
- `WORLD_SPACE` World Space – Transforms include effects of parenting/restpose and constraints. 
- `TRANSFORM_SPACE` Transform Space – Transforms don’t include parenting/restpose or constraints. 
- `LOCAL_SPACE` Local Space – Transforms include effects of constraints but not parenting/restpose.   Type: 

Literal[‘WORLD_SPACE’, ‘TRANSFORM_SPACE’, ‘LOCAL_SPACE’]

      transform_type 

Driver variable type (default `'LOC_X'`)

  Type: 

Literal[‘LOC_X’, ‘LOC_Y’, ‘LOC_Z’, ‘ROT_X’, ‘ROT_Y’, ‘ROT_Z’, ‘ROT_W’, ‘SCALE_X’, ‘SCALE_Y’, ‘SCALE_Z’, ‘SCALE_AVG’]

      use_fallback_value 

Use the fallback value if the data path cannot be resolved, instead of failing to evaluate the driver (default False)

  Type: 

bool

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

  
- [`DriverVariable.targets`](bpy.types.DriverVariable.html#bpy.types.DriverVariable.targets)
