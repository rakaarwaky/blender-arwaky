# bpy.types.AnimData

# AnimData(bpy_struct)

 

base class — [`bpy_struct`](bpy.types.bpy_struct.html#bpy.types.bpy_struct)

   class bpy.types.AnimData(bpy_struct) 

Animation data for data-block

   action 

Active Action for this data-block

  Type: 

[`Action`](bpy.types.Action.html#bpy.types.Action) | None

      action_blend_type 

Method used for combining Active Action’s result with result of NLA stack (default `'REPLACE'`)

  
- `REPLACE` Replace – The strip values replace the accumulated results by amount specified by influence. 
- `COMBINE` Combine – The strip values are combined with accumulated results by appropriately using addition, multiplication, or quaternion math, based on channel type. 
- `ADD` Add – Weighted result of strip is added to the accumulated results. 
- `SUBTRACT` Subtract – Weighted result of strip is removed from the accumulated results. 
- `MULTIPLY` Multiply – Weighted result of strip is multiplied with the accumulated results.   Type: 

Literal[‘REPLACE’, ‘COMBINE’, ‘ADD’, ‘SUBTRACT’, ‘MULTIPLY’]

      action_extrapolation 

Action to take for gaps past the Active Action’s range (when evaluating with NLA) (default `'HOLD'`)

  
- `NOTHING` Nothing – Strip has no influence past its extents. 
- `HOLD` Hold – Hold the first frame if no previous strips in track, and always hold last frame. 
- `HOLD_FORWARD` Hold Forward – Only hold last frame.   Type: 

Literal[‘NOTHING’, ‘HOLD’, ‘HOLD_FORWARD’]

      action_influence 

Amount the Active Action contributes to the result of the NLA stack (in [0, 1], default 1.0)

  Type: 

float

      action_slot 

The slot identifies which sub-set of the Action is considered to be for this data-block, and its name is used to find the right slot when assigning an Action

  Type: 

[`ActionSlot`](bpy.types.ActionSlot.html#bpy.types.ActionSlot) | None

      action_slot_handle 

A number that identifies which sub-set of the Action is considered to be for this data-block (in [-inf, inf], default 0)

  Type: 

int

      action_slot_handle_tweak_storage 

Storage to temporarily hold the main action slot while in tweak mode (in [-inf, inf], default 0)

  Type: 

int

      action_suitable_slots 

The list of slots in this animation data-block (default None, readonly)

  Type: 

[`bpy_prop_collection`](bpy.types.bpy_prop_collection.html#bpy.types.bpy_prop_collection)[[`ActionSlot`](bpy.types.ActionSlot.html#bpy.types.ActionSlot)]

      action_tweak_storage 

Storage to temporarily hold the main action while in tweak mode

  Type: 

[`Action`](bpy.types.Action.html#bpy.types.Action) | None

      drivers 

The Drivers/Expressions for this data-block (default None, readonly)

  Type: 

[`AnimDataDrivers`](bpy.types.AnimDataDrivers.html#bpy.types.AnimDataDrivers)[[`FCurve`](bpy.types.FCurve.html#bpy.types.FCurve)]

      last_slot_identifier 

The identifier of the most recently assigned action slot. The slot identifies which sub-set of the Action is considered to be for this data-block, and its identifier is used to find the right slot when assigning an Action. (default “”, never None)

  Type: 

str

      nla_tracks 

NLA Tracks (i.e. Animation Layers) (default None, readonly)

  Type: 

[`NlaTracks`](bpy.types.NlaTracks.html#bpy.types.NlaTracks)[[`NlaTrack`](bpy.types.NlaTrack.html#bpy.types.NlaTrack)]

      use_nla 

NLA stack is evaluated when evaluating this block (default True)

  Type: 

bool

      use_pin 

(default False)

  Type: 

bool

      use_tweak_mode 

Whether to enable or disable tweak mode in NLA (default False)

  Type: 

bool

      nla_tweak_strip_time_to_scene(frame, *, invert=False) 

Convert a time value from the local time of the tweaked strip to scene time, exactly as done by built-in key editing tools. Returns the input time unchanged if not tweaking.

  Parameters:  
- frame (float) – Input time (in [-1.04857e+06, 1.04857e+06]) 
- invert (bool) – Invert, Convert scene time to action time (optional)   Returns: 

Converted time (in [-1.04857e+06, 1.04857e+06])

  Return type: 

float

      fix_paths_rename_all(*, prefix='', old_name='', new_name='') 

Rename the property paths in the animation system, since properties are animated via string paths, it’s needed to keep them valid after properties has been renamed

  Parameters:  
- prefix (str) – Prefix, Name prefix (optional, never None) 
- old_name (str) – Old Name, Old name (optional, never None) 
- new_name (str) – New Name, New name (optional, never None)       classmethod bl_rna_get_subclass(id, default=None, /)  Parameters:  
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

  
- [`Annotation.animation_data`](bpy.types.Annotation.html#bpy.types.Annotation.animation_data) 
- [`Armature.animation_data`](bpy.types.Armature.html#bpy.types.Armature.animation_data) 
- [`CacheFile.animation_data`](bpy.types.CacheFile.html#bpy.types.CacheFile.animation_data) 
- [`Camera.animation_data`](bpy.types.Camera.html#bpy.types.Camera.animation_data) 
- [`Curve.animation_data`](bpy.types.Curve.html#bpy.types.Curve.animation_data) 
- [`Curves.animation_data`](bpy.types.Curves.html#bpy.types.Curves.animation_data) 
- [`FreestyleLineStyle.animation_data`](bpy.types.FreestyleLineStyle.html#bpy.types.FreestyleLineStyle.animation_data) 
- [`GreasePencil.animation_data`](bpy.types.GreasePencil.html#bpy.types.GreasePencil.animation_data) 
- [`ID.animation_data_create`](bpy.types.ID.html#bpy.types.ID.animation_data_create) 
- [`Key.animation_data`](bpy.types.Key.html#bpy.types.Key.animation_data) 
- [`Lattice.animation_data`](bpy.types.Lattice.html#bpy.types.Lattice.animation_data) 
- [`Light.animation_data`](bpy.types.Light.html#bpy.types.Light.animation_data) 
- [`LightProbe.animation_data`](bpy.types.LightProbe.html#bpy.types.LightProbe.animation_data) 
- [`Mask.animation_data`](bpy.types.Mask.html#bpy.types.Mask.animation_data)   
- [`Material.animation_data`](bpy.types.Material.html#bpy.types.Material.animation_data) 
- [`Mesh.animation_data`](bpy.types.Mesh.html#bpy.types.Mesh.animation_data) 
- [`MetaBall.animation_data`](bpy.types.MetaBall.html#bpy.types.MetaBall.animation_data) 
- [`MovieClip.animation_data`](bpy.types.MovieClip.html#bpy.types.MovieClip.animation_data) 
- [`NodeTree.animation_data`](bpy.types.NodeTree.html#bpy.types.NodeTree.animation_data) 
- [`Object.animation_data`](bpy.types.Object.html#bpy.types.Object.animation_data) 
- [`ParticleSettings.animation_data`](bpy.types.ParticleSettings.html#bpy.types.ParticleSettings.animation_data) 
- [`PointCloud.animation_data`](bpy.types.PointCloud.html#bpy.types.PointCloud.animation_data) 
- [`Scene.animation_data`](bpy.types.Scene.html#bpy.types.Scene.animation_data) 
- [`Speaker.animation_data`](bpy.types.Speaker.html#bpy.types.Speaker.animation_data) 
- [`Texture.animation_data`](bpy.types.Texture.html#bpy.types.Texture.animation_data) 
- [`Volume.animation_data`](bpy.types.Volume.html#bpy.types.Volume.animation_data) 
- [`World.animation_data`](bpy.types.World.html#bpy.types.World.animation_data)
