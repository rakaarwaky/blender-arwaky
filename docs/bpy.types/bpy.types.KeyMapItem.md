# bpy.types.KeyMapItem

# KeyMapItem(bpy_struct)

 

base class — [`bpy_struct`](bpy.types.bpy_struct.html#bpy.types.bpy_struct)

   class bpy.types.KeyMapItem(bpy_struct) 

Item in a Key Map

   active 

Activate or deactivate item (default False)

  Type: 

bool

      alt 

Alt key pressed, -1 for any state (in [-1, 1], default 0)

  Type: 

int

      alt_ui 

Alt key pressed (default False)

  Type: 

bool

      any 

Any modifier keys pressed (default False)

  Type: 

bool

      ctrl 

Control key pressed, -1 for any state (in [-1, 1], default 0)

  Type: 

int

      ctrl_ui 

Control key pressed (default False)

  Type: 

bool

      direction 

The direction (only applies to drag events) (default `'ANY'`)

  Type: 

Literal[[Event Direction Items](bpy_types_enum_items/event_direction_items.html#rna-enum-event-direction-items)]

      hyper 

Hyper key pressed, -1 for any state (in [-1, 1], default 0)

  Type: 

int

      hyper_ui 

Hyper key pressed. An additional modifier which can be configured on Linux, typically replacing CapsLock (default False)

  Type: 

bool

      id 

ID of the item (in [-32768, 32767], default 0, readonly)

  Type: 

int

      idname 

Identifier of operator to call on input event (default “”, never None)

  Type: 

str

      is_user_defined 

Is this keymap item user defined (does not just replace a builtin item) (default False, readonly)

  Type: 

bool

      is_user_modified 

Is this keymap item modified by the user (default False, readonly)

  Type: 

bool

      key_modifier 

Regular key pressed as a modifier (default `'NONE'`)

  Type: 

Literal[[Event Type Items](bpy_types_enum_items/event_type_items.html#rna-enum-event-type-items)]

      map_type 

Type of event mapping (default `'KEYBOARD'`)

  Type: 

Literal[‘KEYBOARD’, ‘MOUSE’, ‘NDOF’, ‘TEXTINPUT’, ‘TIMER’]

      name 

Name of operator (translated) to call on input event (default “”, readonly, never None)

  Type: 

str

      oskey 

Operating system key pressed, -1 for any state (in [-1, 1], default 0)

  Type: 

int

      oskey_ui 

Operating system key pressed (default False)

  Type: 

bool

      properties 

Properties to set when the operator is called (readonly)

  Type: 

[`OperatorProperties`](bpy.types.OperatorProperties.html#bpy.types.OperatorProperties) | None

      propvalue 

The value this event translates to in a modal keymap (default `'NONE'`)

  Type: 

Literal[[Keymap Propvalue Items](bpy_types_enum_items/keymap_propvalue_items.html#rna-enum-keymap-propvalue-items)]

      repeat 

Active on key-repeat events (when a key is held) (default False)

  Type: 

bool

      shift 

Shift key pressed, -1 for any state (in [-1, 1], default 0)

  Type: 

int

      shift_ui 

Shift key pressed (default False)

  Type: 

bool

      show_expanded 

Show key map event and property details in the user interface (default False)

  Type: 

bool

      type 

Type of event (default `'NONE'`)

  Type: 

Literal[[Event Type Items](bpy_types_enum_items/event_type_items.html#rna-enum-event-type-items)]

      value 

(default `'NOTHING'`)

  Type: 

Literal[[Event Value Items](bpy_types_enum_items/event_value_items.html#rna-enum-event-value-items)]

      compare(item) 

compare

  Parameters: 

item (`KeyMapItem` | None) – Item

  Returns: 

Comparison result

  Return type: 

bool

      to_string(*, compact=False) 

to_string

  Parameters: 

compact (bool) – Compact, (optional)

  Returns: 

result, (never None)

  Return type: 

str

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

  
- [`KeyConfigurations.find_item_from_operator`](bpy.types.KeyConfigurations.html#bpy.types.KeyConfigurations.find_item_from_operator) 
- [`KeyMap.keymap_items`](bpy.types.KeyMap.html#bpy.types.KeyMap.keymap_items) 
- [`KeyMap.restore_item_to_default`](bpy.types.KeyMap.html#bpy.types.KeyMap.restore_item_to_default) 
- `KeyMapItem.compare` 
- [`KeyMapItems.find_from_operator`](bpy.types.KeyMapItems.html#bpy.types.KeyMapItems.find_from_operator) 
- [`KeyMapItems.find_match`](bpy.types.KeyMapItems.html#bpy.types.KeyMapItems.find_match) 
- [`KeyMapItems.find_match`](bpy.types.KeyMapItems.html#bpy.types.KeyMapItems.find_match) 
- [`KeyMapItems.from_id`](bpy.types.KeyMapItems.html#bpy.types.KeyMapItems.from_id)   
- [`KeyMapItems.match_event`](bpy.types.KeyMapItems.html#bpy.types.KeyMapItems.match_event) 
- [`KeyMapItems.new`](bpy.types.KeyMapItems.html#bpy.types.KeyMapItems.new) 
- [`KeyMapItems.new_from_item`](bpy.types.KeyMapItems.html#bpy.types.KeyMapItems.new_from_item) 
- [`KeyMapItems.new_from_item`](bpy.types.KeyMapItems.html#bpy.types.KeyMapItems.new_from_item) 
- [`KeyMapItems.new_modal`](bpy.types.KeyMapItems.html#bpy.types.KeyMapItems.new_modal) 
- [`KeyMapItems.remove`](bpy.types.KeyMapItems.html#bpy.types.KeyMapItems.remove) 
- [`UILayout.template_event_from_keymap_item`](bpy.types.UILayout.html#bpy.types.UILayout.template_event_from_keymap_item) 
- [`UILayout.template_keymap_item_properties`](bpy.types.UILayout.html#bpy.types.UILayout.template_keymap_item_properties)
