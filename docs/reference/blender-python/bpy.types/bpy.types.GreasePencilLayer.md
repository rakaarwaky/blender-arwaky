# bpy.types.GreasePencilLayer

# GreasePencilLayer(GreasePencilTreeNode)

 

base classes — [`bpy_struct`](bpy.types.bpy_struct.html#bpy.types.bpy_struct), [`GreasePencilTreeNode`](bpy.types.GreasePencilTreeNode.html#bpy.types.GreasePencilTreeNode)

   class bpy.types.GreasePencilLayer(GreasePencilTreeNode) 

Collection of related drawings

   blend_mode 

Blend mode (default `'REGULAR'`)

  Type: 

Literal[‘REGULAR’, ‘HARDLIGHT’, ‘ADD’, ‘SUBTRACT’, ‘MULTIPLY’, ‘DIVIDE’]

      frames 

Grease Pencil frames (default None, readonly)

  Type: 

[`GreasePencilFrames`](bpy.types.GreasePencilFrames.html#bpy.types.GreasePencilFrames)[[`GreasePencilFrame`](bpy.types.GreasePencilFrame.html#bpy.types.GreasePencilFrame)]

      ignore_locked_materials 

Allow editing strokes even if they use locked materials (default False)

  Type: 

bool

      lock_frame 

Lock current frame displayed by layer (default False)

  Type: 

bool

      mask_layers 

List of Masking Layers (default None, readonly)

  Type: 

[`GreasePencilLayerMasks`](bpy.types.GreasePencilLayerMasks.html#bpy.types.GreasePencilLayerMasks)[[`GreasePencilLayerMask`](bpy.types.GreasePencilLayerMask.html#bpy.types.GreasePencilLayerMask)]

      matrix_local 

Local transformation matrix of the layer (multi-dimensional array of 4 * 4 items, in [-inf, inf], default ((0.0, 0.0, 0.0, 0.0), (0.0, 0.0, 0.0, 0.0), (0.0, 0.0, 0.0, 0.0), (0.0, 0.0, 0.0, 0.0)), readonly)

  Type: 

[`mathutils.Matrix`](mathutils.html#mathutils.Matrix)

      matrix_parent_inverse 

Inverse of layer’s parent transformation matrix (multi-dimensional array of 4 * 4 items, in [-inf, inf], default ((0.0, 0.0, 0.0, 0.0), (0.0, 0.0, 0.0, 0.0), (0.0, 0.0, 0.0, 0.0), (0.0, 0.0, 0.0, 0.0)), readonly)

  Type: 

[`mathutils.Matrix`](mathutils.html#mathutils.Matrix)

      opacity 

Layer Opacity (in [0, 1], default 0.0)

  Type: 

float

      parent 

Parent object

  Type: 

[`Object`](bpy.types.Object.html#bpy.types.Object) | None

      parent_bone 

Name of parent bone. Only used when the parent object is an armature. (default “”, never None)

  Type: 

str

      pass_index 

Index number for the “Layer Index” pass (in [0, inf], default 0)

  Type: 

int

      radius_offset 

Radius change to apply to current strokes (in [-inf, inf], default 0.0)

  Type: 

float

      rotation 

Euler rotation of the layer (array of 3 items, in [-inf, inf], default (0.0, 0.0, 0.0))

  Type: 

[`mathutils.Euler`](mathutils.html#mathutils.Euler)

      scale 

Scale of the layer (array of 3 items, in [-inf, inf], default (1.0, 1.0, 1.0))

  Type: 

[`mathutils.Vector`](mathutils.html#mathutils.Vector)

      tint_color 

Color for tinting stroke colors (array of 3 items, in [0, 1], default (0.0, 0.0, 0.0))

  Type: 

[`mathutils.Color`](mathutils.html#mathutils.Color)

      tint_factor 

Factor of tinting color (in [0, 1], default 0.0)

  Type: 

float

      translation 

Translation of the layer (array of 3 items, in [-inf, inf], default (0.0, 0.0, 0.0))

  Type: 

[`mathutils.Vector`](mathutils.html#mathutils.Vector)

      use_lights 

Enable the use of lights on stroke and fill materials (default False)

  Type: 

bool

      use_viewlayer_masks 

Include the mask layers when rendering the view-layer (default True)

  Type: 

bool

      viewlayer_render 

Only include Layer in this View Layer render output (leave blank to include always) (default “”, never None)

  Type: 

str

      get_frame_at(frame_number) 

Get the frame at given frame number

  Parameters: 

frame_number (int) – Frame Number, (in [-1048574, 1048574])

  Returns: 

Frame

  Return type: 

[`GreasePencilFrame`](bpy.types.GreasePencilFrame.html#bpy.types.GreasePencilFrame)

      current_frame() 

The Grease Pencil frame at the current scene time on this layer

  Return type: 

[`GreasePencilFrame`](bpy.types.GreasePencilFrame.html#bpy.types.GreasePencilFrame)

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
- [`GreasePencilTreeNode.name`](bpy.types.GreasePencilTreeNode.html#bpy.types.GreasePencilTreeNode.name) 
- [`GreasePencilTreeNode.hide`](bpy.types.GreasePencilTreeNode.html#bpy.types.GreasePencilTreeNode.hide) 
- [`GreasePencilTreeNode.lock`](bpy.types.GreasePencilTreeNode.html#bpy.types.GreasePencilTreeNode.lock) 
- [`GreasePencilTreeNode.select`](bpy.types.GreasePencilTreeNode.html#bpy.types.GreasePencilTreeNode.select) 
- [`GreasePencilTreeNode.use_onion_skinning`](bpy.types.GreasePencilTreeNode.html#bpy.types.GreasePencilTreeNode.use_onion_skinning)   
- [`GreasePencilTreeNode.use_masks`](bpy.types.GreasePencilTreeNode.html#bpy.types.GreasePencilTreeNode.use_masks) 
- [`GreasePencilTreeNode.channel_color`](bpy.types.GreasePencilTreeNode.html#bpy.types.GreasePencilTreeNode.channel_color) 
- [`GreasePencilTreeNode.next_node`](bpy.types.GreasePencilTreeNode.html#bpy.types.GreasePencilTreeNode.next_node) 
- [`GreasePencilTreeNode.prev_node`](bpy.types.GreasePencilTreeNode.html#bpy.types.GreasePencilTreeNode.prev_node) 
- [`GreasePencilTreeNode.parent_group`](bpy.types.GreasePencilTreeNode.html#bpy.types.GreasePencilTreeNode.parent_group)     

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
- [`GreasePencilTreeNode.bl_rna_get_subclass`](bpy.types.GreasePencilTreeNode.html#bpy.types.GreasePencilTreeNode.bl_rna_get_subclass) 
- [`GreasePencilTreeNode.bl_rna_get_subclass_py`](bpy.types.GreasePencilTreeNode.html#bpy.types.GreasePencilTreeNode.bl_rna_get_subclass_py)     

## References

  
- [`GreasePencil.layers`](bpy.types.GreasePencil.html#bpy.types.GreasePencil.layers) 
- [`GreasePencilLayerMasks.add`](bpy.types.GreasePencilLayerMasks.html#bpy.types.GreasePencilLayerMasks.add) 
- [`GreasePencilv3Layers.active`](bpy.types.GreasePencilv3Layers.html#bpy.types.GreasePencilv3Layers.active) 
- [`GreasePencilv3Layers.move`](bpy.types.GreasePencilv3Layers.html#bpy.types.GreasePencilv3Layers.move) 
- [`GreasePencilv3Layers.move_bottom`](bpy.types.GreasePencilv3Layers.html#bpy.types.GreasePencilv3Layers.move_bottom)   
- [`GreasePencilv3Layers.move_to_layer_group`](bpy.types.GreasePencilv3Layers.html#bpy.types.GreasePencilv3Layers.move_to_layer_group) 
- [`GreasePencilv3Layers.move_top`](bpy.types.GreasePencilv3Layers.html#bpy.types.GreasePencilv3Layers.move_top) 
- [`GreasePencilv3Layers.new`](bpy.types.GreasePencilv3Layers.html#bpy.types.GreasePencilv3Layers.new) 
- [`GreasePencilv3Layers.remove`](bpy.types.GreasePencilv3Layers.html#bpy.types.GreasePencilv3Layers.remove)
