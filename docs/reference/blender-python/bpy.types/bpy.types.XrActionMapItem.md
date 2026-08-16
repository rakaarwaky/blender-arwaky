# bpy.types.XrActionMapItem

# XrActionMapItem(bpy_struct)

 

base class — [`bpy_struct`](bpy.types.bpy_struct.html#bpy.types.bpy_struct)

   class bpy.types.XrActionMapItem(bpy_struct)   bimanual 

The action depends on the states/poses of both user paths (default False)

  Type: 

bool

      bindings 

Bindings for the action map item, mapping the action to an XR input (default None, readonly)

  Type: 

[`XrActionMapBindings`](bpy.types.XrActionMapBindings.html#bpy.types.XrActionMapBindings)[[`XrActionMapBinding`](bpy.types.XrActionMapBinding.html#bpy.types.XrActionMapBinding)]

      haptic_amplitude 

Intensity of the haptic vibration, ranging from 0.0 to 1.0 (in [0, 1], default 0.0)

  Type: 

float

      haptic_duration 

Haptic duration in seconds. 0.0 is the minimum supported duration. (in [0, inf], default 0.0)

  Type: 

float

      haptic_frequency 

Frequency of the haptic vibration in hertz. 0.0 specifies the OpenXR runtime’s default frequency. (in [0, inf], default 0.0)

  Type: 

float

      haptic_match_user_paths 

Apply haptics to the same user paths for the haptic action and this action (default False)

  Type: 

bool

      haptic_mode 

Haptic application mode (default `'PRESS'`)

  
- `PRESS` Press – Apply haptics on button press. 
- `RELEASE` Release – Apply haptics on button release. 
- `PRESS_RELEASE` Press Release – Apply haptics on button press and release. 
- `REPEAT` Repeat – Apply haptics repeatedly for the duration of the button press.   Type: 

Literal[‘PRESS’, ‘RELEASE’, ‘PRESS_RELEASE’, ‘REPEAT’]

      haptic_name 

Name of the haptic action to apply when executing this action (default “”, never None)

  Type: 

str

      name 

Name of the action map item (default “”, never None)

  Type: 

str

      op 

Identifier of operator to call on action event (default “”, never None)

  Type: 

str

      op_mode 

Operator execution mode (default `'PRESS'`)

  
- `PRESS` Press – Execute operator on button press (non-modal operators only). 
- `RELEASE` Release – Execute operator on button release (non-modal operators only). 
- `MODAL` Modal – Use modal execution (modal operators only).   Type: 

Literal[‘PRESS’, ‘RELEASE’, ‘MODAL’]

      op_name 

Name of operator (translated) to call on action event (default “”, readonly, never None)

  Type: 

str

      op_properties 

Properties to set when the operator is called (readonly)

  Type: 

[`OperatorProperties`](bpy.types.OperatorProperties.html#bpy.types.OperatorProperties) | None

      pose_is_controller_aim 

The action poses will be used for the VR controller aims (default False)

  Type: 

bool

      pose_is_controller_grip 

The action poses will be used for the VR controller grips (default False)

  Type: 

bool

      selected_binding 

Currently selected binding (in [-32768, 32767], default 0)

  Type: 

int

      type 

Action type (default `'FLOAT'`)

  
- `FLOAT` Float – Float action, representing either a digital or analog button. 
- `VECTOR2D` Vector2D – 2D float vector action, representing a thumbstick or trackpad. 
- `POSE` Pose – 3D pose action, representing a controller’s location and rotation. 
- `VIBRATION` Vibration – Haptic vibration output action, to be applied with a duration, frequency, and amplitude.   Type: 

Literal[‘FLOAT’, ‘VECTOR2D’, ‘POSE’, ‘VIBRATION’]

      user_paths 

OpenXR user paths (default None, readonly)

  Type: 

[`XrUserPaths`](bpy.types.XrUserPaths.html#bpy.types.XrUserPaths)[[`XrUserPath`](bpy.types.XrUserPath.html#bpy.types.XrUserPath)]

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

  
- [`XrActionMap.actionmap_items`](bpy.types.XrActionMap.html#bpy.types.XrActionMap.actionmap_items) 
- [`XrActionMapItems.find`](bpy.types.XrActionMapItems.html#bpy.types.XrActionMapItems.find) 
- [`XrActionMapItems.new`](bpy.types.XrActionMapItems.html#bpy.types.XrActionMapItems.new) 
- [`XrActionMapItems.new_from_item`](bpy.types.XrActionMapItems.html#bpy.types.XrActionMapItems.new_from_item)   
- [`XrActionMapItems.new_from_item`](bpy.types.XrActionMapItems.html#bpy.types.XrActionMapItems.new_from_item) 
- [`XrActionMapItems.remove`](bpy.types.XrActionMapItems.html#bpy.types.XrActionMapItems.remove) 
- [`XrSessionState.action_binding_create`](bpy.types.XrSessionState.html#bpy.types.XrSessionState.action_binding_create) 
- [`XrSessionState.action_create`](bpy.types.XrSessionState.html#bpy.types.XrSessionState.action_create)
