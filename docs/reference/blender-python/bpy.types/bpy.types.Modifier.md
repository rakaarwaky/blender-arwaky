# bpy.types.Modifier

# Modifier(bpy_struct)

 

base class — [`bpy_struct`](bpy.types.bpy_struct.html#bpy.types.bpy_struct)

  

Subclasses

  
- [ArmatureModifier(Modifier)](bpy.types.ArmatureModifier.html) 
- [ArrayModifier(Modifier)](bpy.types.ArrayModifier.html) 
- [BevelModifier(Modifier)](bpy.types.BevelModifier.html) 
- [BooleanModifier(Modifier)](bpy.types.BooleanModifier.html) 
- [BuildModifier(Modifier)](bpy.types.BuildModifier.html) 
- [CastModifier(Modifier)](bpy.types.CastModifier.html) 
- [ClothModifier(Modifier)](bpy.types.ClothModifier.html) 
- [CollisionModifier(Modifier)](bpy.types.CollisionModifier.html) 
- [CorrectiveSmoothModifier(Modifier)](bpy.types.CorrectiveSmoothModifier.html) 
- [CurveModifier(Modifier)](bpy.types.CurveModifier.html) 
- [DataTransferModifier(Modifier)](bpy.types.DataTransferModifier.html) 
- [DecimateModifier(Modifier)](bpy.types.DecimateModifier.html) 
- [DisplaceModifier(Modifier)](bpy.types.DisplaceModifier.html) 
- [DynamicPaintModifier(Modifier)](bpy.types.DynamicPaintModifier.html) 
- [EdgeSplitModifier(Modifier)](bpy.types.EdgeSplitModifier.html) 
- [ExplodeModifier(Modifier)](bpy.types.ExplodeModifier.html) 
- [FluidModifier(Modifier)](bpy.types.FluidModifier.html) 
- [GreasePencilArmatureModifier(Modifier)](bpy.types.GreasePencilArmatureModifier.html) 
- [GreasePencilArrayModifier(Modifier)](bpy.types.GreasePencilArrayModifier.html) 
- [GreasePencilBuildModifier(Modifier)](bpy.types.GreasePencilBuildModifier.html) 
- [GreasePencilColorModifier(Modifier)](bpy.types.GreasePencilColorModifier.html) 
- [GreasePencilDashModifierData(Modifier)](bpy.types.GreasePencilDashModifierData.html) 
- [GreasePencilEnvelopeModifier(Modifier)](bpy.types.GreasePencilEnvelopeModifier.html) 
- [GreasePencilHookModifier(Modifier)](bpy.types.GreasePencilHookModifier.html) 
- [GreasePencilLatticeModifier(Modifier)](bpy.types.GreasePencilLatticeModifier.html) 
- [GreasePencilLengthModifier(Modifier)](bpy.types.GreasePencilLengthModifier.html) 
- [GreasePencilLineartModifier(Modifier)](bpy.types.GreasePencilLineartModifier.html) 
- [GreasePencilMirrorModifier(Modifier)](bpy.types.GreasePencilMirrorModifier.html) 
- [GreasePencilMultiplyModifier(Modifier)](bpy.types.GreasePencilMultiplyModifier.html) 
- [GreasePencilNoiseModifier(Modifier)](bpy.types.GreasePencilNoiseModifier.html) 
- [GreasePencilOffsetModifier(Modifier)](bpy.types.GreasePencilOffsetModifier.html) 
- [GreasePencilOpacityModifier(Modifier)](bpy.types.GreasePencilOpacityModifier.html) 
- [GreasePencilOutlineModifier(Modifier)](bpy.types.GreasePencilOutlineModifier.html) 
- [GreasePencilShrinkwrapModifier(Modifier)](bpy.types.GreasePencilShrinkwrapModifier.html) 
- [GreasePencilSimplifyModifier(Modifier)](bpy.types.GreasePencilSimplifyModifier.html) 
- [GreasePencilSmoothModifier(Modifier)](bpy.types.GreasePencilSmoothModifier.html) 
- [GreasePencilSubdivModifier(Modifier)](bpy.types.GreasePencilSubdivModifier.html) 
- [GreasePencilTextureModifier(Modifier)](bpy.types.GreasePencilTextureModifier.html) 
- [GreasePencilThickModifierData(Modifier)](bpy.types.GreasePencilThickModifierData.html) 
- [GreasePencilTimeModifier(Modifier)](bpy.types.GreasePencilTimeModifier.html) 
- [GreasePencilTintModifier(Modifier)](bpy.types.GreasePencilTintModifier.html) 
- [GreasePencilWeightAngleModifier(Modifier)](bpy.types.GreasePencilWeightAngleModifier.html) 
- [GreasePencilWeightProximityModifier(Modifier)](bpy.types.GreasePencilWeightProximityModifier.html) 
- [HookModifier(Modifier)](bpy.types.HookModifier.html) 
- [LaplacianDeformModifier(Modifier)](bpy.types.LaplacianDeformModifier.html) 
- [LaplacianSmoothModifier(Modifier)](bpy.types.LaplacianSmoothModifier.html) 
- [LatticeModifier(Modifier)](bpy.types.LatticeModifier.html) 
- [MaskModifier(Modifier)](bpy.types.MaskModifier.html) 
- [MeshCacheModifier(Modifier)](bpy.types.MeshCacheModifier.html) 
- [MeshDeformModifier(Modifier)](bpy.types.MeshDeformModifier.html) 
- [MeshSequenceCacheModifier(Modifier)](bpy.types.MeshSequenceCacheModifier.html) 
- [MeshToVolumeModifier(Modifier)](bpy.types.MeshToVolumeModifier.html) 
- [MirrorModifier(Modifier)](bpy.types.MirrorModifier.html) 
- [MultiresModifier(Modifier)](bpy.types.MultiresModifier.html) 
- [NodesModifier(Modifier)](bpy.types.NodesModifier.html) 
- [NormalEditModifier(Modifier)](bpy.types.NormalEditModifier.html) 
- [OceanModifier(Modifier)](bpy.types.OceanModifier.html) 
- [ParticleInstanceModifier(Modifier)](bpy.types.ParticleInstanceModifier.html) 
- [ParticleSystemModifier(Modifier)](bpy.types.ParticleSystemModifier.html) 
- [RemeshModifier(Modifier)](bpy.types.RemeshModifier.html) 
- [ScrewModifier(Modifier)](bpy.types.ScrewModifier.html) 
- [ShrinkwrapModifier(Modifier)](bpy.types.ShrinkwrapModifier.html) 
- [SimpleDeformModifier(Modifier)](bpy.types.SimpleDeformModifier.html) 
- [SkinModifier(Modifier)](bpy.types.SkinModifier.html) 
- [SmoothModifier(Modifier)](bpy.types.SmoothModifier.html) 
- [SoftBodyModifier(Modifier)](bpy.types.SoftBodyModifier.html) 
- [SolidifyModifier(Modifier)](bpy.types.SolidifyModifier.html) 
- [SubsurfModifier(Modifier)](bpy.types.SubsurfModifier.html) 
- [SurfaceDeformModifier(Modifier)](bpy.types.SurfaceDeformModifier.html) 
- [SurfaceModifier(Modifier)](bpy.types.SurfaceModifier.html) 
- [TriangulateModifier(Modifier)](bpy.types.TriangulateModifier.html) 
- [UVProjectModifier(Modifier)](bpy.types.UVProjectModifier.html) 
- [UVWarpModifier(Modifier)](bpy.types.UVWarpModifier.html) 
- [VertexWeightEditModifier(Modifier)](bpy.types.VertexWeightEditModifier.html) 
- [VertexWeightMixModifier(Modifier)](bpy.types.VertexWeightMixModifier.html) 
- [VertexWeightProximityModifier(Modifier)](bpy.types.VertexWeightProximityModifier.html) 
- [VolumeDisplaceModifier(Modifier)](bpy.types.VolumeDisplaceModifier.html) 
- [VolumeToMeshModifier(Modifier)](bpy.types.VolumeToMeshModifier.html) 
- [WarpModifier(Modifier)](bpy.types.WarpModifier.html) 
- [WaveModifier(Modifier)](bpy.types.WaveModifier.html) 
- [WeightedNormalModifier(Modifier)](bpy.types.WeightedNormalModifier.html) 
- [WeldModifier(Modifier)](bpy.types.WeldModifier.html) 
- [WireframeModifier(Modifier)](bpy.types.WireframeModifier.html)     class bpy.types.Modifier(bpy_struct) 

Modifier affecting the geometry data of an object

   execution_time 

Time in seconds that the modifier took to evaluate. This is only set on evaluated objects. If multiple modifiers run in parallel, execution time is not a reliable metric. (in [-inf, inf], default 0.0, readonly)

  Type: 

float

      is_active 

The active modifier in the list (default False)

  Type: 

bool

      is_override_data 

In a local override object, whether this modifier comes from the linked reference object, or is local to the override (default True, readonly)

  Type: 

bool

      name 

Modifier name (default “”, never None)

  Type: 

str

      persistent_uid 

Uniquely identifies the modifier within the modifier stack that it is part of (in [-inf, inf], default 0, readonly)

  Type: 

int

      show_expanded 

Set modifier expanded in the user interface (default False)

  Type: 

bool

      show_in_editmode 

Display modifier in Edit mode (default False)

  Type: 

bool

      show_on_cage 

Adjust edit cage to modifier result (default False)

  Type: 

bool

      show_render 

Use modifier during render (default False)

  Type: 

bool

      show_viewport 

Display modifier in viewport (default False)

  Type: 

bool

      type 

(default `'GREASE_PENCIL_VERTEX_WEIGHT_PROXIMITY'`, readonly)

  Type: 

Literal[[Object Modifier Type Items](bpy_types_enum_items/object_modifier_type_items.html#rna-enum-object-modifier-type-items)]

      use_apply_on_spline 

Apply this and all preceding deformation modifiers on splines’ points rather than on filled curve/surface (default False)

  Type: 

bool

      use_pin_to_last 

Keep the modifier at the end of the list (default False)

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

  
- [`Object.modifiers`](bpy.types.Object.html#bpy.types.Object.modifiers) 
- [`ObjectModifiers.active`](bpy.types.ObjectModifiers.html#bpy.types.ObjectModifiers.active)   
- [`ObjectModifiers.new`](bpy.types.ObjectModifiers.html#bpy.types.ObjectModifiers.new) 
- [`ObjectModifiers.remove`](bpy.types.ObjectModifiers.html#bpy.types.ObjectModifiers.remove)
