# bpy.types.ShaderNode

# ShaderNode(NodeInternal)

 

base classes — [`bpy_struct`](bpy.types.bpy_struct.html#bpy.types.bpy_struct), [`Node`](bpy.types.Node.html#bpy.types.Node), [`NodeInternal`](bpy.types.NodeInternal.html#bpy.types.NodeInternal)

  

Subclasses

  
- [ShaderNodeAddShader(ShaderNode)](bpy.types.ShaderNodeAddShader.html) 
- [ShaderNodeAmbientOcclusion(ShaderNode)](bpy.types.ShaderNodeAmbientOcclusion.html) 
- [ShaderNodeAttribute(ShaderNode)](bpy.types.ShaderNodeAttribute.html) 
- [ShaderNodeBackground(ShaderNode)](bpy.types.ShaderNodeBackground.html) 
- [ShaderNodeBevel(ShaderNode)](bpy.types.ShaderNodeBevel.html) 
- [ShaderNodeBlackbody(ShaderNode)](bpy.types.ShaderNodeBlackbody.html) 
- [ShaderNodeBrightContrast(ShaderNode)](bpy.types.ShaderNodeBrightContrast.html) 
- [ShaderNodeBsdfAnisotropic(ShaderNode)](bpy.types.ShaderNodeBsdfAnisotropic.html) 
- [ShaderNodeBsdfDiffuse(ShaderNode)](bpy.types.ShaderNodeBsdfDiffuse.html) 
- [ShaderNodeBsdfGlass(ShaderNode)](bpy.types.ShaderNodeBsdfGlass.html) 
- [ShaderNodeBsdfHair(ShaderNode)](bpy.types.ShaderNodeBsdfHair.html) 
- [ShaderNodeBsdfHairPrincipled(ShaderNode)](bpy.types.ShaderNodeBsdfHairPrincipled.html) 
- [ShaderNodeBsdfMetallic(ShaderNode)](bpy.types.ShaderNodeBsdfMetallic.html) 
- [ShaderNodeBsdfPrincipled(ShaderNode)](bpy.types.ShaderNodeBsdfPrincipled.html) 
- [ShaderNodeBsdfRayPortal(ShaderNode)](bpy.types.ShaderNodeBsdfRayPortal.html) 
- [ShaderNodeBsdfRefraction(ShaderNode)](bpy.types.ShaderNodeBsdfRefraction.html) 
- [ShaderNodeBsdfSheen(ShaderNode)](bpy.types.ShaderNodeBsdfSheen.html) 
- [ShaderNodeBsdfToon(ShaderNode)](bpy.types.ShaderNodeBsdfToon.html) 
- [ShaderNodeBsdfTranslucent(ShaderNode)](bpy.types.ShaderNodeBsdfTranslucent.html) 
- [ShaderNodeBsdfTransparent(ShaderNode)](bpy.types.ShaderNodeBsdfTransparent.html) 
- [ShaderNodeBump(ShaderNode)](bpy.types.ShaderNodeBump.html) 
- [ShaderNodeCameraData(ShaderNode)](bpy.types.ShaderNodeCameraData.html) 
- [ShaderNodeClamp(ShaderNode)](bpy.types.ShaderNodeClamp.html) 
- [ShaderNodeCombineColor(ShaderNode)](bpy.types.ShaderNodeCombineColor.html) 
- [ShaderNodeCombineXYZ(ShaderNode)](bpy.types.ShaderNodeCombineXYZ.html) 
- [ShaderNodeCustomGroup(ShaderNode)](bpy.types.ShaderNodeCustomGroup.html) 
- [ShaderNodeDisplacement(ShaderNode)](bpy.types.ShaderNodeDisplacement.html) 
- [ShaderNodeEeveeSpecular(ShaderNode)](bpy.types.ShaderNodeEeveeSpecular.html) 
- [ShaderNodeEmission(ShaderNode)](bpy.types.ShaderNodeEmission.html) 
- [ShaderNodeFloatCurve(ShaderNode)](bpy.types.ShaderNodeFloatCurve.html) 
- [ShaderNodeFresnel(ShaderNode)](bpy.types.ShaderNodeFresnel.html) 
- [ShaderNodeGamma(ShaderNode)](bpy.types.ShaderNodeGamma.html) 
- [ShaderNodeGroup(ShaderNode)](bpy.types.ShaderNodeGroup.html) 
- [ShaderNodeHairInfo(ShaderNode)](bpy.types.ShaderNodeHairInfo.html) 
- [ShaderNodeHoldout(ShaderNode)](bpy.types.ShaderNodeHoldout.html) 
- [ShaderNodeHueSaturation(ShaderNode)](bpy.types.ShaderNodeHueSaturation.html) 
- [ShaderNodeInvert(ShaderNode)](bpy.types.ShaderNodeInvert.html) 
- [ShaderNodeLayerWeight(ShaderNode)](bpy.types.ShaderNodeLayerWeight.html) 
- [ShaderNodeLightFalloff(ShaderNode)](bpy.types.ShaderNodeLightFalloff.html) 
- [ShaderNodeLightPath(ShaderNode)](bpy.types.ShaderNodeLightPath.html) 
- [ShaderNodeMapRange(ShaderNode)](bpy.types.ShaderNodeMapRange.html) 
- [ShaderNodeMapping(ShaderNode)](bpy.types.ShaderNodeMapping.html) 
- [ShaderNodeMath(ShaderNode)](bpy.types.ShaderNodeMath.html) 
- [ShaderNodeMix(ShaderNode)](bpy.types.ShaderNodeMix.html) 
- [ShaderNodeMixRGB(ShaderNode)](bpy.types.ShaderNodeMixRGB.html) 
- [ShaderNodeMixShader(ShaderNode)](bpy.types.ShaderNodeMixShader.html) 
- [ShaderNodeNewGeometry(ShaderNode)](bpy.types.ShaderNodeNewGeometry.html) 
- [ShaderNodeNormal(ShaderNode)](bpy.types.ShaderNodeNormal.html) 
- [ShaderNodeNormalMap(ShaderNode)](bpy.types.ShaderNodeNormalMap.html) 
- [ShaderNodeObjectInfo(ShaderNode)](bpy.types.ShaderNodeObjectInfo.html) 
- [ShaderNodeOutputAOV(ShaderNode)](bpy.types.ShaderNodeOutputAOV.html) 
- [ShaderNodeOutputLight(ShaderNode)](bpy.types.ShaderNodeOutputLight.html) 
- [ShaderNodeOutputLineStyle(ShaderNode)](bpy.types.ShaderNodeOutputLineStyle.html) 
- [ShaderNodeOutputMaterial(ShaderNode)](bpy.types.ShaderNodeOutputMaterial.html) 
- [ShaderNodeOutputWorld(ShaderNode)](bpy.types.ShaderNodeOutputWorld.html) 
- [ShaderNodeParticleInfo(ShaderNode)](bpy.types.ShaderNodeParticleInfo.html) 
- [ShaderNodePointInfo(ShaderNode)](bpy.types.ShaderNodePointInfo.html) 
- [ShaderNodeRGB(ShaderNode)](bpy.types.ShaderNodeRGB.html) 
- [ShaderNodeRGBCurve(ShaderNode)](bpy.types.ShaderNodeRGBCurve.html) 
- [ShaderNodeRGBToBW(ShaderNode)](bpy.types.ShaderNodeRGBToBW.html) 
- [ShaderNodeRadialTiling(ShaderNode)](bpy.types.ShaderNodeRadialTiling.html) 
- [ShaderNodeRaycast(ShaderNode)](bpy.types.ShaderNodeRaycast.html) 
- [ShaderNodeScript(ShaderNode)](bpy.types.ShaderNodeScript.html) 
- [ShaderNodeSeparateColor(ShaderNode)](bpy.types.ShaderNodeSeparateColor.html) 
- [ShaderNodeSeparateXYZ(ShaderNode)](bpy.types.ShaderNodeSeparateXYZ.html) 
- [ShaderNodeShaderToRGB(ShaderNode)](bpy.types.ShaderNodeShaderToRGB.html) 
- [ShaderNodeSqueeze(ShaderNode)](bpy.types.ShaderNodeSqueeze.html) 
- [ShaderNodeSubsurfaceScattering(ShaderNode)](bpy.types.ShaderNodeSubsurfaceScattering.html) 
- [ShaderNodeTangent(ShaderNode)](bpy.types.ShaderNodeTangent.html) 
- [ShaderNodeTexBrick(ShaderNode)](bpy.types.ShaderNodeTexBrick.html) 
- [ShaderNodeTexChecker(ShaderNode)](bpy.types.ShaderNodeTexChecker.html) 
- [ShaderNodeTexCoord(ShaderNode)](bpy.types.ShaderNodeTexCoord.html) 
- [ShaderNodeTexEnvironment(ShaderNode)](bpy.types.ShaderNodeTexEnvironment.html) 
- [ShaderNodeTexGabor(ShaderNode)](bpy.types.ShaderNodeTexGabor.html) 
- [ShaderNodeTexGradient(ShaderNode)](bpy.types.ShaderNodeTexGradient.html) 
- [ShaderNodeTexIES(ShaderNode)](bpy.types.ShaderNodeTexIES.html) 
- [ShaderNodeTexImage(ShaderNode)](bpy.types.ShaderNodeTexImage.html) 
- [ShaderNodeTexMagic(ShaderNode)](bpy.types.ShaderNodeTexMagic.html) 
- [ShaderNodeTexNoise(ShaderNode)](bpy.types.ShaderNodeTexNoise.html) 
- [ShaderNodeTexSky(ShaderNode)](bpy.types.ShaderNodeTexSky.html) 
- [ShaderNodeTexVoronoi(ShaderNode)](bpy.types.ShaderNodeTexVoronoi.html) 
- [ShaderNodeTexWave(ShaderNode)](bpy.types.ShaderNodeTexWave.html) 
- [ShaderNodeTexWhiteNoise(ShaderNode)](bpy.types.ShaderNodeTexWhiteNoise.html) 
- [ShaderNodeUVAlongStroke(ShaderNode)](bpy.types.ShaderNodeUVAlongStroke.html) 
- [ShaderNodeUVMap(ShaderNode)](bpy.types.ShaderNodeUVMap.html) 
- [ShaderNodeValToRGB(ShaderNode)](bpy.types.ShaderNodeValToRGB.html) 
- [ShaderNodeValue(ShaderNode)](bpy.types.ShaderNodeValue.html) 
- [ShaderNodeVectorCurve(ShaderNode)](bpy.types.ShaderNodeVectorCurve.html) 
- [ShaderNodeVectorDisplacement(ShaderNode)](bpy.types.ShaderNodeVectorDisplacement.html) 
- [ShaderNodeVectorMath(ShaderNode)](bpy.types.ShaderNodeVectorMath.html) 
- [ShaderNodeVectorRotate(ShaderNode)](bpy.types.ShaderNodeVectorRotate.html) 
- [ShaderNodeVectorTransform(ShaderNode)](bpy.types.ShaderNodeVectorTransform.html) 
- [ShaderNodeVertexColor(ShaderNode)](bpy.types.ShaderNodeVertexColor.html) 
- [ShaderNodeVolumeAbsorption(ShaderNode)](bpy.types.ShaderNodeVolumeAbsorption.html) 
- [ShaderNodeVolumeCoefficients(ShaderNode)](bpy.types.ShaderNodeVolumeCoefficients.html) 
- [ShaderNodeVolumeInfo(ShaderNode)](bpy.types.ShaderNodeVolumeInfo.html) 
- [ShaderNodeVolumePrincipled(ShaderNode)](bpy.types.ShaderNodeVolumePrincipled.html) 
- [ShaderNodeVolumeScatter(ShaderNode)](bpy.types.ShaderNodeVolumeScatter.html) 
- [ShaderNodeWavelength(ShaderNode)](bpy.types.ShaderNodeWavelength.html) 
- [ShaderNodeWireframe(ShaderNode)](bpy.types.ShaderNodeWireframe.html)     class bpy.types.ShaderNode(NodeInternal) 

Material shader node

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
- [`Node.type`](bpy.types.Node.html#bpy.types.Node.type) 
- [`Node.location`](bpy.types.Node.html#bpy.types.Node.location) 
- [`Node.location_absolute`](bpy.types.Node.html#bpy.types.Node.location_absolute) 
- [`Node.width`](bpy.types.Node.html#bpy.types.Node.width) 
- [`Node.height`](bpy.types.Node.html#bpy.types.Node.height) 
- [`Node.dimensions`](bpy.types.Node.html#bpy.types.Node.dimensions) 
- [`Node.name`](bpy.types.Node.html#bpy.types.Node.name) 
- [`Node.label`](bpy.types.Node.html#bpy.types.Node.label) 
- [`Node.inputs`](bpy.types.Node.html#bpy.types.Node.inputs) 
- [`Node.outputs`](bpy.types.Node.html#bpy.types.Node.outputs) 
- [`Node.panel_states`](bpy.types.Node.html#bpy.types.Node.panel_states) 
- [`Node.internal_links`](bpy.types.Node.html#bpy.types.Node.internal_links) 
- [`Node.parent`](bpy.types.Node.html#bpy.types.Node.parent) 
- [`Node.warning_propagation`](bpy.types.Node.html#bpy.types.Node.warning_propagation) 
- [`Node.use_custom_color`](bpy.types.Node.html#bpy.types.Node.use_custom_color) 
- [`Node.color`](bpy.types.Node.html#bpy.types.Node.color) 
- [`Node.color_tag`](bpy.types.Node.html#bpy.types.Node.color_tag)   
- [`Node.select`](bpy.types.Node.html#bpy.types.Node.select) 
- [`Node.show_options`](bpy.types.Node.html#bpy.types.Node.show_options) 
- [`Node.show_preview`](bpy.types.Node.html#bpy.types.Node.show_preview) 
- [`Node.hide`](bpy.types.Node.html#bpy.types.Node.hide) 
- [`Node.mute`](bpy.types.Node.html#bpy.types.Node.mute) 
- [`Node.show_texture`](bpy.types.Node.html#bpy.types.Node.show_texture) 
- [`Node.bl_idname`](bpy.types.Node.html#bpy.types.Node.bl_idname) 
- [`Node.bl_label`](bpy.types.Node.html#bpy.types.Node.bl_label) 
- [`Node.bl_description`](bpy.types.Node.html#bpy.types.Node.bl_description) 
- [`Node.bl_icon`](bpy.types.Node.html#bpy.types.Node.bl_icon) 
- [`Node.bl_static_type`](bpy.types.Node.html#bpy.types.Node.bl_static_type) 
- [`Node.bl_width_default`](bpy.types.Node.html#bpy.types.Node.bl_width_default) 
- [`Node.bl_width_min`](bpy.types.Node.html#bpy.types.Node.bl_width_min) 
- [`Node.bl_width_max`](bpy.types.Node.html#bpy.types.Node.bl_width_max) 
- [`Node.bl_height_default`](bpy.types.Node.html#bpy.types.Node.bl_height_default) 
- [`Node.bl_height_min`](bpy.types.Node.html#bpy.types.Node.bl_height_min) 
- [`Node.bl_height_max`](bpy.types.Node.html#bpy.types.Node.bl_height_max)     

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
- [`Node.bl_system_properties_get`](bpy.types.Node.html#bpy.types.Node.bl_system_properties_get)   
- [`Node.socket_value_update`](bpy.types.Node.html#bpy.types.Node.socket_value_update) 
- [`Node.is_registered_node_type`](bpy.types.Node.html#bpy.types.Node.is_registered_node_type) 
- [`Node.poll`](bpy.types.Node.html#bpy.types.Node.poll) 
- [`Node.poll_instance`](bpy.types.Node.html#bpy.types.Node.poll_instance) 
- [`Node.update`](bpy.types.Node.html#bpy.types.Node.update) 
- [`Node.insert_link`](bpy.types.Node.html#bpy.types.Node.insert_link) 
- [`Node.init`](bpy.types.Node.html#bpy.types.Node.init) 
- [`Node.copy`](bpy.types.Node.html#bpy.types.Node.copy) 
- [`Node.free`](bpy.types.Node.html#bpy.types.Node.free) 
- [`Node.draw_buttons`](bpy.types.Node.html#bpy.types.Node.draw_buttons) 
- [`Node.draw_buttons_ext`](bpy.types.Node.html#bpy.types.Node.draw_buttons_ext) 
- [`Node.draw_label`](bpy.types.Node.html#bpy.types.Node.draw_label) 
- [`Node.debug_zone_body_lazy_function_graph`](bpy.types.Node.html#bpy.types.Node.debug_zone_body_lazy_function_graph) 
- [`Node.debug_zone_lazy_function_graph`](bpy.types.Node.html#bpy.types.Node.debug_zone_lazy_function_graph) 
- [`Node.poll`](bpy.types.Node.html#bpy.types.Node.poll) 
- [`Node.bl_rna_get_subclass`](bpy.types.Node.html#bpy.types.Node.bl_rna_get_subclass) 
- [`Node.bl_rna_get_subclass_py`](bpy.types.Node.html#bpy.types.Node.bl_rna_get_subclass_py) 
- [`NodeInternal.poll`](bpy.types.NodeInternal.html#bpy.types.NodeInternal.poll) 
- [`NodeInternal.poll_instance`](bpy.types.NodeInternal.html#bpy.types.NodeInternal.poll_instance) 
- [`NodeInternal.update`](bpy.types.NodeInternal.html#bpy.types.NodeInternal.update) 
- [`NodeInternal.draw_buttons`](bpy.types.NodeInternal.html#bpy.types.NodeInternal.draw_buttons) 
- [`NodeInternal.draw_buttons_ext`](bpy.types.NodeInternal.html#bpy.types.NodeInternal.draw_buttons_ext) 
- [`NodeInternal.bl_rna_get_subclass`](bpy.types.NodeInternal.html#bpy.types.NodeInternal.bl_rna_get_subclass) 
- [`NodeInternal.bl_rna_get_subclass_py`](bpy.types.NodeInternal.html#bpy.types.NodeInternal.bl_rna_get_subclass_py)     

## References

  
- [`ShaderNodeTree.get_output_node`](bpy.types.ShaderNodeTree.html#bpy.types.ShaderNodeTree.get_output_node)
