# bpy.types.MovieTrackingObject

# MovieTrackingObject(bpy_struct)

 

base class — [`bpy_struct`](bpy.types.bpy_struct.html#bpy.types.bpy_struct)

   class bpy.types.MovieTrackingObject(bpy_struct) 

Match-moving object tracking and reconstruction data

   is_camera 

Object is used for camera tracking (default False, readonly)

  Type: 

bool

      keyframe_a 

First keyframe used for reconstruction initialization (in [-inf, inf], default 0)

  Type: 

int

      keyframe_b 

Second keyframe used for reconstruction initialization (in [-inf, inf], default 0)

  Type: 

int

      name 

Unique name of object (default “”, never None)

  Type: 

str

      plane_tracks 

Collection of plane tracks in this tracking data object (default None, readonly)

  Type: 

[`MovieTrackingObjectPlaneTracks`](bpy.types.MovieTrackingObjectPlaneTracks.html#bpy.types.MovieTrackingObjectPlaneTracks)[[`MovieTrackingPlaneTrack`](bpy.types.MovieTrackingPlaneTrack.html#bpy.types.MovieTrackingPlaneTrack)]

      reconstruction 

(readonly)

  Type: 

[`MovieTrackingReconstruction`](bpy.types.MovieTrackingReconstruction.html#bpy.types.MovieTrackingReconstruction) | None

      scale 

Scale of object solution in camera space (in [0.0001, 10000], default 1.0)

  Type: 

float

      tracks 

Collection of tracks in this tracking data object (default None, readonly)

  Type: 

[`MovieTrackingObjectTracks`](bpy.types.MovieTrackingObjectTracks.html#bpy.types.MovieTrackingObjectTracks)[[`MovieTrackingTrack`](bpy.types.MovieTrackingTrack.html#bpy.types.MovieTrackingTrack)]

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

  
- [`MovieTracking.objects`](bpy.types.MovieTracking.html#bpy.types.MovieTracking.objects) 
- [`MovieTrackingObjects.active`](bpy.types.MovieTrackingObjects.html#bpy.types.MovieTrackingObjects.active)   
- [`MovieTrackingObjects.new`](bpy.types.MovieTrackingObjects.html#bpy.types.MovieTrackingObjects.new) 
- [`MovieTrackingObjects.remove`](bpy.types.MovieTrackingObjects.html#bpy.types.MovieTrackingObjects.remove)
