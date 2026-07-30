# bpy.types.FCurveKeyframePoints

# FCurveKeyframePoints(bpy_prop_collection)

 

base class — [`bpy_prop_collection`](bpy.types.bpy_prop_collection.html#bpy.types.bpy_prop_collection)

   class bpy.types.FCurveKeyframePoints(bpy_prop_collection) 

Collection of keyframe points

   insert(frame, value, *, options=set(), keyframe_type='KEYFRAME') 

Add a keyframe point to a F-Curve

  Parameters:  
- frame (float) – X Value of this keyframe point (in [-inf, inf]) 
- value (float) – Y Value of this keyframe point (in [-inf, inf]) 
- options (set[Literal['REPLACE', 'NEEDED', 'FAST']]) – 

Keyframe options (optional)

  
- `REPLACE` Replace – Don’t add any new keyframes, but just replace existing ones. 
- `NEEDED` Needed – Only adds keyframes that are needed. 
- `FAST` Fast – Fast keyframe insertion to avoid recalculating the curve each time. 
- keyframe_type (Literal[[Beztriple Keyframe Type Items](bpy_types_enum_items/beztriple_keyframe_type_items.html#rna-enum-beztriple-keyframe-type-items)]) – Type of keyframe to insert (optional)   Returns: 

Newly created keyframe

  Return type: 

[`Keyframe`](bpy.types.Keyframe.html#bpy.types.Keyframe)

      add(count) 

Add a keyframe point to a F-Curve

  Parameters: 

count (int) – Number, Number of points to add to the spline (in [0, inf])

      remove(keyframe, *, fast=False) 

Remove keyframe from an F-Curve

  Parameters:  
- keyframe ([`Keyframe`](bpy.types.Keyframe.html#bpy.types.Keyframe) | None) – Keyframe to remove (never None) 
- fast (bool) – Fast, Fast keyframe removal to avoid recalculating the curve each time (optional)       clear() 

Remove all keyframes from an F-Curve

    sort() 

Ensure all keyframe points are chronologically sorted

    deduplicate() 

Ensure there are no duplicate keys. Assumes that the points have already been sorted

    handles_recalc() 

Update handles after modifications to the keyframe points, to update things like auto-clamping

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

  
- [`FCurve.keyframe_points`](bpy.types.FCurve.html#bpy.types.FCurve.keyframe_points)
