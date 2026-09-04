# bpy.types.Material

# Material(ID)

 

base classes — [`bpy_struct`](bpy.types.bpy_struct.html#bpy.types.bpy_struct), [`ID`](bpy.types.ID.html#bpy.types.ID)

   class bpy.types.Material(ID) 

Material data-block to define the appearance of geometric objects for rendering

   alpha_threshold 

A pixel is rendered only if its alpha value is above this threshold (in [0, 1], default 0.5)

  Type: 

float

      animation_data 

Animation data for this data-block (readonly)

  Type: 

[`AnimData`](bpy.types.AnimData.html#bpy.types.AnimData) | None

      blend_method 

Blend Mode for Transparent Faces (Deprecated: use ‘surface_render_method’) (default `'OPAQUE'`)

  
- `OPAQUE` Opaque – Render surface without transparency. 
- `CLIP` Alpha Clip – Use the alpha threshold to clip the visibility (binary visibility). 
- `HASHED` Alpha Hashed – Use noise to dither the binary visibility (works well with multi-samples). 
- `BLEND` Alpha Blend – Render polygon transparent, depending on alpha channel of the texture.   Type: 

Literal[‘OPAQUE’, ‘CLIP’, ‘HASHED’, ‘BLEND’]

      cycles 

Cycles material settings (readonly)

  Type: 

`CyclesMaterialSettings` | None

      diffuse_color 

Diffuse color of the material (array of 4 items, in [0, inf], default (0.8, 0.8, 0.8, 1.0))

  Type: 

[`bpy_prop_array`](bpy.types.bpy_prop_array.html#bpy.types.bpy_prop_array)[float]

      displacement_method 

Method to use for the displacement (default `'BUMP'`)

  
- `BUMP` Bump Only – Bump mapping to simulate the appearance of displacement. 
- `DISPLACEMENT` Displacement Only – Use true displacement of surface only, requires fine subdivision. 
- `BOTH` Displacement and Bump – Combination of true displacement and bump mapping for finer detail.   Type: 

Literal[‘BUMP’, ‘DISPLACEMENT’, ‘BOTH’]

      grease_pencil 

Grease Pencil color settings for material (readonly)

  Type: 

[`MaterialGPencilStyle`](bpy.types.MaterialGPencilStyle.html#bpy.types.MaterialGPencilStyle) | None

      is_grease_pencil 

True if this material has Grease Pencil data (default False, readonly)

  Type: 

bool

      line_color 

Line color used for Freestyle line rendering (array of 4 items, in [0, inf], default (0.0, 0.0, 0.0, 0.0))

  Type: 

[`bpy_prop_array`](bpy.types.bpy_prop_array.html#bpy.types.bpy_prop_array)[float]

      line_priority 

The line color of a higher priority is used at material boundaries (in [0, 32767], default 0)

  Type: 

int

      lineart 

Line Art settings for material (readonly)

  Type: 

[`MaterialLineArt`](bpy.types.MaterialLineArt.html#bpy.types.MaterialLineArt) | None

      max_vertex_displacement 

The max distance a vertex can be displaced. Displacements over this threshold may cause visibility issues. (in [0, inf], default 0.0)

  Type: 

float

      metallic 

Amount of mirror reflection for raytrace (in [0, 1], default 0.0)

  Type: 

float

      node_tree 

Node tree for node based materials (readonly)

  Type: 

[`NodeTree`](bpy.types.NodeTree.html#bpy.types.NodeTree) | None

      paint_active_slot 

Index of active texture paint slot (in [0, 32767], default 0)

  Type: 

int

      paint_clone_slot 

Index of clone texture paint slot (in [0, 32767], default 0)

  Type: 

int

      pass_index 

Index number for the “Material Index” render pass (in [0, 32767], default 0)

  Type: 

int

      preview_render_type 

Type of preview render (default `'SPHERE'`)

  
- `FLAT` Flat – Flat XY plane. 
- `SPHERE` Sphere – Sphere. 
- `CUBE` Cube – Cube. 
- `HAIR` Hair – Hair strands. 
- `SHADERBALL` Shader Ball – Shader ball. 
- `CLOTH` Cloth – Cloth. 
- `FLUID` Fluid – Fluid.   Type: 

Literal[‘FLAT’, ‘SPHERE’, ‘CUBE’, ‘HAIR’, ‘SHADERBALL’, ‘CLOTH’, ‘FLUID’]

      refraction_depth 

Approximate the thickness of the object to compute two refraction events (0 is disabled) (Deprecated) (in [0, inf], default 0.0)

  Type: 

float

      roughness 

Roughness of the material (in [0, 1], default 0.4)

  Type: 

float

      show_transparent_back 

Render multiple transparent layers (may introduce transparency sorting problems) (Deprecated: use ‘use_tranparency_overlap’) (default True)

  Type: 

bool

      specular_color 

Specular color of the material (array of 3 items, in [0, inf], default (1.0, 1.0, 1.0))

  Type: 

[`mathutils.Color`](mathutils.html#mathutils.Color)

      specular_intensity 

How intense (bright) the specular reflection is (in [0, 1], default 0.5)

  Type: 

float

      surface_render_method 

Controls the blending and the compatibility with certain features (default `'DITHERED'`)

  
- `DITHERED` Dithered – Allows for grayscale hashed transparency, and compatible with render passes and raytracing. Also known as deferred rendering.. 
- `BLENDED` Blended – Allows for colored transparency, but incompatible with render passes and raytracing. Also known as forward rendering..   Type: 

Literal[‘DITHERED’, ‘BLENDED’]

      texture_paint_images 

Texture images used for texture painting (default None, readonly)

  Type: 

[`bpy_prop_collection`](bpy.types.bpy_prop_collection.html#bpy.types.bpy_prop_collection)[[`Image`](bpy.types.Image.html#bpy.types.Image)]

      texture_paint_slots 

Texture slots defining the mapping and influence of textures (default None, readonly)

  Type: 

[`bpy_prop_collection`](bpy.types.bpy_prop_collection.html#bpy.types.bpy_prop_collection)[[`TexPaintSlot`](bpy.types.TexPaintSlot.html#bpy.types.TexPaintSlot)]

      thickness_mode 

Approximation used to model the light interactions inside the object (default `'SPHERE'`)

  
- `SPHERE` Sphere – Approximate the object as a sphere whose diameter is equal to the thickness defined by the node tree. 
- `SLAB` Slab – Approximate the object as an infinite slab of thickness defined by the node tree.   Type: 

Literal[‘SPHERE’, ‘SLAB’]

      use_backface_culling 

Use back face culling to hide the back side of faces (default False)

  Type: 

bool

      use_backface_culling_lightprobe_volume 

Consider material single sided for light probe volume capture. Additionally helps rejecting probes inside the object to avoid light leaks. (default True)

  Type: 

bool

      use_backface_culling_shadow 

Use back face culling when casting shadows (default False)

  Type: 

bool

      use_nodes 

Use shader nodes to render the material (default False)

  

Deprecated since version 5.0: removal planned in version 6.0

 

Unused but kept for compatibility reasons. Setting the property has no effect, and getting it always returns True.

   Type: 

bool

      use_preview_world 

Use the current world background to light the preview render (default False)

  Type: 

bool

      use_raytrace_refraction 

Use raytracing to determine transmitted color instead of using only light probes. This prevents the surface from contributing to the lighting of surfaces not using this setting. (default False)

  Type: 

bool

      use_screen_refraction 

Use raytracing to determine transmitted color instead of using only light probes. This prevents the surface from contributing to the lighting of surfaces not using this setting. Deprecated: use ‘use_raytrace_refraction’. (default False)

  Type: 

bool

      use_sss_translucency 

Add translucency effect to subsurface (Deprecated) (default False)

  Type: 

bool

      use_thickness_from_shadow 

Use the shadow maps from shadow casting lights to refine the thickness defined by the material node tree (default False)

  Type: 

bool

      use_transparency_overlap 

Render multiple transparent layers (may introduce transparency sorting problems) (default True)

  Type: 

bool

      use_transparent_shadow 

Use transparent shadows for this material if it contains a Transparent BSDF, disabling will render faster but not give accurate shadows (default True)

  Type: 

bool

      volume_intersection_method 

Determines which inner part of the mesh will produce volumetric effect (default `'FAST'`)

  
- `FAST` Fast – Each face is considered as a medium interface. Gives correct results for manifold geometry that contains no inner parts.. 
- `ACCURATE` Accurate – Faces are considered as medium interface only when they have different consecutive facing. Gives correct results as long as the max ray depth is not exceeded. Have significant memory overhead compared to the fast method..   Type: 

Literal[‘FAST’, ‘ACCURATE’]

      inline_shader_nodes() 

Get the inlined shader nodes of this material. This preprocesses the node tree to remove nested groups, repeat zones and more.

  Returns: 

The inlined shader nodes.

  Return type: 

[`InlineShaderNodes`](bpy.types.InlineShaderNodes.html#bpy.types.InlineShaderNodes)

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

  
- `bpy.context.material` 
- [`BlendData.materials`](bpy.types.BlendData.html#bpy.types.BlendData.materials) 
- [`BlendDataMaterials.create_gpencil_data`](bpy.types.BlendDataMaterials.html#bpy.types.BlendDataMaterials.create_gpencil_data) 
- [`BlendDataMaterials.new`](bpy.types.BlendDataMaterials.html#bpy.types.BlendDataMaterials.new) 
- [`BlendDataMaterials.remove`](bpy.types.BlendDataMaterials.html#bpy.types.BlendDataMaterials.remove) 
- [`BlendDataMaterials.remove_gpencil_data`](bpy.types.BlendDataMaterials.html#bpy.types.BlendDataMaterials.remove_gpencil_data) 
- [`BrushGpencilSettings.material`](bpy.types.BrushGpencilSettings.html#bpy.types.BrushGpencilSettings.material) 
- [`BrushGpencilSettings.material_alt`](bpy.types.BrushGpencilSettings.html#bpy.types.BrushGpencilSettings.material_alt) 
- [`Curve.materials`](bpy.types.Curve.html#bpy.types.Curve.materials) 
- [`Curves.materials`](bpy.types.Curves.html#bpy.types.Curves.materials) 
- [`GeometryNodeInputMaterial.material`](bpy.types.GeometryNodeInputMaterial.html#bpy.types.GeometryNodeInputMaterial.material) 
- [`GreasePencil.materials`](bpy.types.GreasePencil.html#bpy.types.GreasePencil.materials) 
- [`GreasePencilArrayModifier.material_filter`](bpy.types.GreasePencilArrayModifier.html#bpy.types.GreasePencilArrayModifier.material_filter) 
- [`GreasePencilBuildModifier.material_filter`](bpy.types.GreasePencilBuildModifier.html#bpy.types.GreasePencilBuildModifier.material_filter) 
- [`GreasePencilColorModifier.material_filter`](bpy.types.GreasePencilColorModifier.html#bpy.types.GreasePencilColorModifier.material_filter) 
- [`GreasePencilDashModifierData.material_filter`](bpy.types.GreasePencilDashModifierData.html#bpy.types.GreasePencilDashModifierData.material_filter) 
- [`GreasePencilEnvelopeModifier.material_filter`](bpy.types.GreasePencilEnvelopeModifier.html#bpy.types.GreasePencilEnvelopeModifier.material_filter) 
- [`GreasePencilHookModifier.material_filter`](bpy.types.GreasePencilHookModifier.html#bpy.types.GreasePencilHookModifier.material_filter) 
- [`GreasePencilLatticeModifier.material_filter`](bpy.types.GreasePencilLatticeModifier.html#bpy.types.GreasePencilLatticeModifier.material_filter) 
- [`GreasePencilLengthModifier.material_filter`](bpy.types.GreasePencilLengthModifier.html#bpy.types.GreasePencilLengthModifier.material_filter) 
- [`GreasePencilLineartModifier.target_material`](bpy.types.GreasePencilLineartModifier.html#bpy.types.GreasePencilLineartModifier.target_material) 
- [`GreasePencilMirrorModifier.material_filter`](bpy.types.GreasePencilMirrorModifier.html#bpy.types.GreasePencilMirrorModifier.material_filter) 
- [`GreasePencilMultiplyModifier.material_filter`](bpy.types.GreasePencilMultiplyModifier.html#bpy.types.GreasePencilMultiplyModifier.material_filter) 
- [`GreasePencilNoiseModifier.material_filter`](bpy.types.GreasePencilNoiseModifier.html#bpy.types.GreasePencilNoiseModifier.material_filter)   
- [`GreasePencilOffsetModifier.material_filter`](bpy.types.GreasePencilOffsetModifier.html#bpy.types.GreasePencilOffsetModifier.material_filter) 
- [`GreasePencilOpacityModifier.material_filter`](bpy.types.GreasePencilOpacityModifier.html#bpy.types.GreasePencilOpacityModifier.material_filter) 
- [`GreasePencilOutlineModifier.material_filter`](bpy.types.GreasePencilOutlineModifier.html#bpy.types.GreasePencilOutlineModifier.material_filter) 
- [`GreasePencilOutlineModifier.outline_material`](bpy.types.GreasePencilOutlineModifier.html#bpy.types.GreasePencilOutlineModifier.outline_material) 
- [`GreasePencilShrinkwrapModifier.material_filter`](bpy.types.GreasePencilShrinkwrapModifier.html#bpy.types.GreasePencilShrinkwrapModifier.material_filter) 
- [`GreasePencilSimplifyModifier.material_filter`](bpy.types.GreasePencilSimplifyModifier.html#bpy.types.GreasePencilSimplifyModifier.material_filter) 
- [`GreasePencilSmoothModifier.material_filter`](bpy.types.GreasePencilSmoothModifier.html#bpy.types.GreasePencilSmoothModifier.material_filter) 
- [`GreasePencilSubdivModifier.material_filter`](bpy.types.GreasePencilSubdivModifier.html#bpy.types.GreasePencilSubdivModifier.material_filter) 
- [`GreasePencilTextureModifier.material_filter`](bpy.types.GreasePencilTextureModifier.html#bpy.types.GreasePencilTextureModifier.material_filter) 
- [`GreasePencilThickModifierData.material_filter`](bpy.types.GreasePencilThickModifierData.html#bpy.types.GreasePencilThickModifierData.material_filter) 
- [`GreasePencilTintModifier.material_filter`](bpy.types.GreasePencilTintModifier.html#bpy.types.GreasePencilTintModifier.material_filter) 
- [`GreasePencilWeightAngleModifier.material_filter`](bpy.types.GreasePencilWeightAngleModifier.html#bpy.types.GreasePencilWeightAngleModifier.material_filter) 
- [`GreasePencilWeightProximityModifier.material_filter`](bpy.types.GreasePencilWeightProximityModifier.html#bpy.types.GreasePencilWeightProximityModifier.material_filter) 
- [`IDMaterials.append`](bpy.types.IDMaterials.html#bpy.types.IDMaterials.append) 
- [`IDMaterials.pop`](bpy.types.IDMaterials.html#bpy.types.IDMaterials.pop) 
- [`MaterialSlot.material`](bpy.types.MaterialSlot.html#bpy.types.MaterialSlot.material) 
- [`Mesh.materials`](bpy.types.Mesh.html#bpy.types.Mesh.materials) 
- [`MetaBall.materials`](bpy.types.MetaBall.html#bpy.types.MetaBall.materials) 
- [`NodeSocketMaterial.default_value`](bpy.types.NodeSocketMaterial.html#bpy.types.NodeSocketMaterial.default_value) 
- [`NodeTreeInterfaceSocketMaterial.default_value`](bpy.types.NodeTreeInterfaceSocketMaterial.html#bpy.types.NodeTreeInterfaceSocketMaterial.default_value) 
- [`Object.active_material`](bpy.types.Object.html#bpy.types.Object.active_material) 
- [`PointCloud.materials`](bpy.types.PointCloud.html#bpy.types.PointCloud.materials) 
- [`ViewLayer.material_override`](bpy.types.ViewLayer.html#bpy.types.ViewLayer.material_override) 
- [`Volume.materials`](bpy.types.Volume.html#bpy.types.Volume.materials)
