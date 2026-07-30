# bpy.types.Texture

# Texture(ID)

 

base classes — [`bpy_struct`](bpy.types.bpy_struct.html#bpy.types.bpy_struct), [`ID`](bpy.types.ID.html#bpy.types.ID)

  

Subclasses

  
- [BlendTexture(Texture)](bpy.types.BlendTexture.html) 
- [CloudsTexture(Texture)](bpy.types.CloudsTexture.html) 
- [DistortedNoiseTexture(Texture)](bpy.types.DistortedNoiseTexture.html) 
- [ImageTexture(Texture)](bpy.types.ImageTexture.html) 
- [MagicTexture(Texture)](bpy.types.MagicTexture.html) 
- [MarbleTexture(Texture)](bpy.types.MarbleTexture.html) 
- [MusgraveTexture(Texture)](bpy.types.MusgraveTexture.html) 
- [NoiseTexture(Texture)](bpy.types.NoiseTexture.html) 
- [StucciTexture(Texture)](bpy.types.StucciTexture.html) 
- [VoronoiTexture(Texture)](bpy.types.VoronoiTexture.html) 
- [WoodTexture(Texture)](bpy.types.WoodTexture.html)     class bpy.types.Texture(ID) 

Texture data-block used by materials, lights, worlds and brushes

   animation_data 

Animation data for this data-block (readonly)

  Type: 

[`AnimData`](bpy.types.AnimData.html#bpy.types.AnimData) | None

      color_ramp 

(readonly)

  Type: 

[`ColorRamp`](bpy.types.ColorRamp.html#bpy.types.ColorRamp) | None

      contrast 

Adjust the contrast of the texture (in [0, 5], default 1.0)

  Type: 

float

      factor_blue 

(in [0, 2], default 1.0)

  Type: 

float

      factor_green 

(in [0, 2], default 1.0)

  Type: 

float

      factor_red 

(in [0, 2], default 1.0)

  Type: 

float

      intensity 

Adjust the brightness of the texture (in [0, 2], default 1.0)

  Type: 

float

      node_tree 

Node tree for node-based textures (readonly)

  Type: 

[`NodeTree`](bpy.types.NodeTree.html#bpy.types.NodeTree) | None

      saturation 

Adjust the saturation of colors in the texture (in [0, 2], default 1.0)

  Type: 

float

      type 

(default `'IMAGE'`)

  Type: 

Literal[[Texture Type Items](bpy_types_enum_items/texture_type_items.html#rna-enum-texture-type-items)]

      use_clamp 

Set negative texture RGB and intensity values to zero, for some uses like displacement this option can be disabled to get the full range (default False)

  Type: 

bool

      use_color_ramp 

Map the texture intensity to the color ramp. Note that the alpha value is used for image textures, enable “Calculate Alpha” for images without an alpha channel. (default False)

  Type: 

bool

      use_nodes 

Make this a node-based texture (default False)

  Type: 

bool

      use_preview_alpha 

Show Alpha in Preview Render (default False)

  Type: 

bool

      users_material 

Materials that use this texture

  Type: 

tuple[[`Material`](bpy.types.Material.html#bpy.types.Material), …]

    

Note

 

Takes `O(len(bpy.data.materials) * len(material.texture_slots))` time.

  

(readonly)

    users_object_modifier 

Object modifiers that use this texture

  Type: 

tuple[[`Object`](bpy.types.Object.html#bpy.types.Object), …]

    

Note

 

Takes `O(len(bpy.data.objects) * len(obj.modifiers))` time.

  

(readonly)

    evaluate(value) 

Evaluate the texture at the given coordinate and returns the result

  Parameters: 

value ([`mathutils.Vector`](mathutils.html#mathutils.Vector) | Sequence[float]) – The coordinates (x,y,z) of the texture, in case of a 3D texture, the z value is the slice of the texture that is evaluated. For 2D textures such as images, the z value is ignored., (array of 3 items, in [-inf, inf])

  Returns: 

The result of the texture where (x,y,z,w) are (red, green, blue, intensity). For grayscale textures, often intensity only will be used., (array of 4 items, in [-inf, inf])

  Return type: 

[`mathutils.Vector`](mathutils.html#mathutils.Vector)

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
- [`ID.name`](bpy.types.ID.html#bpy.types.ID.name) 
- [`ID.name_full`](bpy.types.ID.html#bpy.types.ID.name_full) 
- [`ID.id_type`](bpy.types.ID.html#bpy.types.ID.id_type) 
- [`ID.session_uid`](bpy.types.ID.html#bpy.types.ID.session_uid) 
- [`ID.is_evaluated`](bpy.types.ID.html#bpy.types.ID.is_evaluated) 
- [`ID.original`](bpy.types.ID.html#bpy.types.ID.original) 
- [`ID.users`](bpy.types.ID.html#bpy.types.ID.users) 
- [`ID.use_fake_user`](bpy.types.ID.html#bpy.types.ID.use_fake_user) 
- [`ID.use_extra_user`](bpy.types.ID.html#bpy.types.ID.use_extra_user) 
- [`ID.is_embedded_data`](bpy.types.ID.html#bpy.types.ID.is_embedded_data)   
- [`ID.is_linked_packed`](bpy.types.ID.html#bpy.types.ID.is_linked_packed) 
- [`ID.is_missing`](bpy.types.ID.html#bpy.types.ID.is_missing) 
- [`ID.is_runtime_data`](bpy.types.ID.html#bpy.types.ID.is_runtime_data) 
- [`ID.is_editable`](bpy.types.ID.html#bpy.types.ID.is_editable) 
- [`ID.tag`](bpy.types.ID.html#bpy.types.ID.tag) 
- [`ID.is_library_indirect`](bpy.types.ID.html#bpy.types.ID.is_library_indirect) 
- [`ID.library`](bpy.types.ID.html#bpy.types.ID.library) 
- [`ID.library_weak_reference`](bpy.types.ID.html#bpy.types.ID.library_weak_reference) 
- [`ID.asset_data`](bpy.types.ID.html#bpy.types.ID.asset_data) 
- [`ID.override_library`](bpy.types.ID.html#bpy.types.ID.override_library) 
- [`ID.preview`](bpy.types.ID.html#bpy.types.ID.preview)     

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
- [`ID.bl_system_properties_get`](bpy.types.ID.html#bpy.types.ID.bl_system_properties_get) 
- [`ID.rename`](bpy.types.ID.html#bpy.types.ID.rename) 
- [`ID.evaluated_get`](bpy.types.ID.html#bpy.types.ID.evaluated_get) 
- [`ID.copy`](bpy.types.ID.html#bpy.types.ID.copy) 
- [`ID.asset_mark`](bpy.types.ID.html#bpy.types.ID.asset_mark) 
- [`ID.asset_clear`](bpy.types.ID.html#bpy.types.ID.asset_clear) 
- [`ID.asset_generate_preview`](bpy.types.ID.html#bpy.types.ID.asset_generate_preview) 
- [`ID.override_create`](bpy.types.ID.html#bpy.types.ID.override_create) 
- [`ID.override_hierarchy_create`](bpy.types.ID.html#bpy.types.ID.override_hierarchy_create) 
- [`ID.user_clear`](bpy.types.ID.html#bpy.types.ID.user_clear) 
- [`ID.user_remap`](bpy.types.ID.html#bpy.types.ID.user_remap) 
- [`ID.make_local`](bpy.types.ID.html#bpy.types.ID.make_local) 
- [`ID.user_of_id`](bpy.types.ID.html#bpy.types.ID.user_of_id) 
- [`ID.animation_data_create`](bpy.types.ID.html#bpy.types.ID.animation_data_create) 
- [`ID.animation_data_clear`](bpy.types.ID.html#bpy.types.ID.animation_data_clear) 
- [`ID.update_tag`](bpy.types.ID.html#bpy.types.ID.update_tag) 
- [`ID.preview_ensure`](bpy.types.ID.html#bpy.types.ID.preview_ensure) 
- [`ID.bl_rna_get_subclass`](bpy.types.ID.html#bpy.types.ID.bl_rna_get_subclass) 
- [`ID.bl_rna_get_subclass_py`](bpy.types.ID.html#bpy.types.ID.bl_rna_get_subclass_py)     

## References

  
- `bpy.context.texture` 
- [`BlendData.textures`](bpy.types.BlendData.html#bpy.types.BlendData.textures) 
- [`BlendDataTextures.new`](bpy.types.BlendDataTextures.html#bpy.types.BlendDataTextures.new) 
- [`BlendDataTextures.remove`](bpy.types.BlendDataTextures.html#bpy.types.BlendDataTextures.remove) 
- [`Brush.mask_texture`](bpy.types.Brush.html#bpy.types.Brush.mask_texture) 
- [`Brush.texture`](bpy.types.Brush.html#bpy.types.Brush.texture) 
- [`DisplaceModifier.texture`](bpy.types.DisplaceModifier.html#bpy.types.DisplaceModifier.texture) 
- [`DynamicPaintSurface.init_texture`](bpy.types.DynamicPaintSurface.html#bpy.types.DynamicPaintSurface.init_texture) 
- [`FieldSettings.texture`](bpy.types.FieldSettings.html#bpy.types.FieldSettings.texture) 
- [`FluidFlowSettings.noise_texture`](bpy.types.FluidFlowSettings.html#bpy.types.FluidFlowSettings.noise_texture) 
- [`FreestyleLineStyle.active_texture`](bpy.types.FreestyleLineStyle.html#bpy.types.FreestyleLineStyle.active_texture)   
- [`NodeSocketTexture.default_value`](bpy.types.NodeSocketTexture.html#bpy.types.NodeSocketTexture.default_value) 
- [`NodeTreeInterfaceSocketTexture.default_value`](bpy.types.NodeTreeInterfaceSocketTexture.html#bpy.types.NodeTreeInterfaceSocketTexture.default_value) 
- [`ParticleSettings.active_texture`](bpy.types.ParticleSettings.html#bpy.types.ParticleSettings.active_texture) 
- [`TextureNodeTexture.texture`](bpy.types.TextureNodeTexture.html#bpy.types.TextureNodeTexture.texture) 
- [`TextureSlot.texture`](bpy.types.TextureSlot.html#bpy.types.TextureSlot.texture) 
- [`VertexWeightEditModifier.mask_texture`](bpy.types.VertexWeightEditModifier.html#bpy.types.VertexWeightEditModifier.mask_texture) 
- [`VertexWeightMixModifier.mask_texture`](bpy.types.VertexWeightMixModifier.html#bpy.types.VertexWeightMixModifier.mask_texture) 
- [`VertexWeightProximityModifier.mask_texture`](bpy.types.VertexWeightProximityModifier.html#bpy.types.VertexWeightProximityModifier.mask_texture) 
- [`VolumeDisplaceModifier.texture`](bpy.types.VolumeDisplaceModifier.html#bpy.types.VolumeDisplaceModifier.texture) 
- [`WarpModifier.texture`](bpy.types.WarpModifier.html#bpy.types.WarpModifier.texture) 
- [`WaveModifier.texture`](bpy.types.WaveModifier.html#bpy.types.WaveModifier.texture)
