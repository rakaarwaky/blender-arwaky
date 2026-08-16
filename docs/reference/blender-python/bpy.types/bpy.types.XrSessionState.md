# bpy.types.XrSessionState

# XrSessionState(bpy_struct)

 

base class — [`bpy_struct`](bpy.types.bpy_struct.html#bpy.types.bpy_struct)

   class bpy.types.XrSessionState(bpy_struct) 

Runtime state information about the VR session

   actionmaps 

(default None, readonly)

  Type: 

[`XrActionMaps`](bpy.types.XrActionMaps.html#bpy.types.XrActionMaps)[[`XrActionMap`](bpy.types.XrActionMap.html#bpy.types.XrActionMap)]

      active_actionmap 

(in [-inf, inf], default 0)

  Type: 

int

      navigation_location 

Location offset to apply to base pose when determining viewer location (array of 3 items, in [-inf, inf], default (0.0, 0.0, 0.0))

  Type: 

[`mathutils.Vector`](mathutils.html#mathutils.Vector)

      navigation_rotation 

Rotation offset to apply to base pose when determining viewer rotation (array of 4 items, in [-inf, inf], default (0.0, 0.0, 0.0, 0.0))

  Type: 

[`mathutils.Quaternion`](mathutils.html#mathutils.Quaternion)

      navigation_scale 

Navigation scale multiplier applied when determining viewer scale (in [-inf, inf], default 0.0)

  Type: 

float

      selected_actionmap 

(in [-inf, inf], default 0)

  Type: 

int

      viewer_pose_location 

Last known location of the viewer pose (center between the eyes) in world space (array of 3 items, in [-inf, inf], default (0.0, 0.0, 0.0), readonly)

  Type: 

[`mathutils.Vector`](mathutils.html#mathutils.Vector)

      viewer_pose_rotation 

Last known rotation of the viewer pose (center between the eyes) in world space (array of 4 items, in [-inf, inf], default (0.0, 0.0, 0.0, 0.0), readonly)

  Type: 

[`mathutils.Quaternion`](mathutils.html#mathutils.Quaternion)

      viewer_scale 

Viewer XR scale factor, computed from the navigation scale, view scale session setting, and active scene unit scale (in [-inf, inf], default 0.0, readonly)

  Type: 

float

      viewfinder 

Viewfinder State (readonly)

  Type: 

[`XrViewfinderState`](bpy.types.XrViewfinderState.html#bpy.types.XrViewfinderState) | None

      classmethod is_running(context) 

Query if the VR session is currently running

  Parameters: 

context ([`Context`](bpy.types.Context.html#bpy.types.Context) | None) – (never None)

  Returns: 

Result

  Return type: 

bool

      classmethod reset_to_base_pose(context) 

Force resetting of position and rotation deltas

  Parameters: 

context ([`Context`](bpy.types.Context.html#bpy.types.Context) | None) – (never None)

      classmethod action_set_create(context, actionmap) 

Create a VR action set

  Parameters:  
- context ([`Context`](bpy.types.Context.html#bpy.types.Context) | None) – (never None) 
- actionmap ([`XrActionMap`](bpy.types.XrActionMap.html#bpy.types.XrActionMap) | None) – (never None)   Returns: 

Result

  Return type: 

bool

      classmethod action_create(context, actionmap, actionmap_item) 

Create a VR action

  Parameters:  
- context ([`Context`](bpy.types.Context.html#bpy.types.Context) | None) – (never None) 
- actionmap ([`XrActionMap`](bpy.types.XrActionMap.html#bpy.types.XrActionMap) | None) – (never None) 
- actionmap_item ([`XrActionMapItem`](bpy.types.XrActionMapItem.html#bpy.types.XrActionMapItem) | None) – (never None)   Returns: 

Result

  Return type: 

bool

      classmethod action_binding_create(context, actionmap, actionmap_item, actionmap_binding) 

Create a VR action binding

  Parameters:  
- context ([`Context`](bpy.types.Context.html#bpy.types.Context) | None) – (never None) 
- actionmap ([`XrActionMap`](bpy.types.XrActionMap.html#bpy.types.XrActionMap) | None) – (never None) 
- actionmap_item ([`XrActionMapItem`](bpy.types.XrActionMapItem.html#bpy.types.XrActionMapItem) | None) – (never None) 
- actionmap_binding ([`XrActionMapBinding`](bpy.types.XrActionMapBinding.html#bpy.types.XrActionMapBinding) | None) – (never None)   Returns: 

Result

  Return type: 

bool

      classmethod active_action_set_set(context, action_set) 

Set the active VR action set

  Parameters:  
- context ([`Context`](bpy.types.Context.html#bpy.types.Context) | None) – (never None) 
- action_set (str) – Action Set, Action set name (never None)   Returns: 

Result

  Return type: 

bool

      classmethod controller_pose_actions_set(context, action_set, grip_action, aim_action) 

Set the actions that determine the VR controller poses

  Parameters:  
- context ([`Context`](bpy.types.Context.html#bpy.types.Context) | None) – (never None) 
- action_set (str) – Action Set, Action set name (never None) 
- grip_action (str) – Grip Action, Name of the action representing the controller grips (never None) 
- aim_action (str) – Aim Action, Name of the action representing the controller aims (never None)   Returns: 

Result

  Return type: 

bool

      classmethod action_state_get(context, action_set_name, action_name, user_path) 

Get the current state of a VR action

  Parameters:  
- context ([`Context`](bpy.types.Context.html#bpy.types.Context) | None) – (never None) 
- action_set_name (str) – Action Set, Action set name (never None) 
- action_name (str) – Action, Action name (never None) 
- user_path (str) – User Path, OpenXR user path (never None)   Returns: 

Action State, Current state of the VR action. Second float value is only set for 2D vector type actions. (array of 2 items, in [-inf, inf], never None)

  Return type: 

[`bpy_prop_array`](bpy.types.bpy_prop_array.html#bpy.types.bpy_prop_array)[float]

      classmethod haptic_action_apply(context, action_set_name, action_name, user_path, duration, frequency, amplitude) 

Apply a VR haptic action

  Parameters:  
- context ([`Context`](bpy.types.Context.html#bpy.types.Context) | None) – (never None) 
- action_set_name (str) – Action Set, Action set name (never None) 
- action_name (str) – Action, Action name (never None) 
- user_path (str) – User Path, Optional OpenXR user path. If not set, the action will be applied to all paths. (never None) 
- duration (float) – Duration, Haptic duration in seconds. 0.0 is the minimum supported duration. (in [0, inf]) 
- frequency (float) – Frequency, Frequency of the haptic vibration in hertz. 0.0 specifies the OpenXR runtime’s default frequency. (in [0, inf]) 
- amplitude (float) – Amplitude, Haptic amplitude, ranging from 0.0 to 1.0 (in [0, 1])   Returns: 

Result

  Return type: 

bool

      classmethod haptic_action_stop(context, action_set_name, action_name, user_path) 

Stop a VR haptic action

  Parameters:  
- context ([`Context`](bpy.types.Context.html#bpy.types.Context) | None) – (never None) 
- action_set_name (str) – Action Set, Action set name (never None) 
- action_name (str) – Action, Action name (never None) 
- user_path (str) – User Path, Optional OpenXR user path. If not set, the action will be stopped for all paths. (never None)       classmethod controller_grip_location_get(context, index) 

Get the last known controller grip location in world space

  Parameters:  
- context ([`Context`](bpy.types.Context.html#bpy.types.Context) | None) – (never None) 
- index (int) – Index, Controller index (in [0, 255])   Returns: 

Location, Controller grip location (array of 3 items, in [-inf, inf], never None)

  Return type: 

[`mathutils.Vector`](mathutils.html#mathutils.Vector)

      classmethod controller_grip_rotation_get(context, index) 

Get the last known controller grip rotation (quaternion) in world space

  Parameters:  
- context ([`Context`](bpy.types.Context.html#bpy.types.Context) | None) – (never None) 
- index (int) – Index, Controller index (in [0, 255])   Returns: 

Rotation, Controller grip quaternion rotation (array of 4 items, in [-inf, inf], never None)

  Return type: 

[`mathutils.Quaternion`](mathutils.html#mathutils.Quaternion)

      classmethod controller_aim_location_get(context, index) 

Get the last known controller aim location in world space

  Parameters:  
- context ([`Context`](bpy.types.Context.html#bpy.types.Context) | None) – (never None) 
- index (int) – Index, Controller index (in [0, 255])   Returns: 

Location, Controller aim location (array of 3 items, in [-inf, inf], never None)

  Return type: 

[`mathutils.Vector`](mathutils.html#mathutils.Vector)

      classmethod controller_aim_rotation_get(context, index) 

Get the last known controller aim rotation (quaternion) in world space

  Parameters:  
- context ([`Context`](bpy.types.Context.html#bpy.types.Context) | None) – (never None) 
- index (int) – Index, Controller index (in [0, 255])   Returns: 

Rotation, Controller aim quaternion rotation (array of 4 items, in [-inf, inf], never None)

  Return type: 

[`mathutils.Quaternion`](mathutils.html#mathutils.Quaternion)

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

  
- [`WindowManager.xr_session_state`](bpy.types.WindowManager.html#bpy.types.WindowManager.xr_session_state) 
- [`XrActionMaps.find`](bpy.types.XrActionMaps.html#bpy.types.XrActionMaps.find) 
- [`XrActionMaps.new`](bpy.types.XrActionMaps.html#bpy.types.XrActionMaps.new)   
- [`XrActionMaps.new_from_actionmap`](bpy.types.XrActionMaps.html#bpy.types.XrActionMaps.new_from_actionmap) 
- [`XrActionMaps.remove`](bpy.types.XrActionMaps.html#bpy.types.XrActionMaps.remove)
