# bpy.types.Context

# Context(bpy_struct)

 

base class — [`bpy_struct`](bpy.types.bpy_struct.html#bpy.types.bpy_struct)

   class bpy.types.Context(bpy_struct) 

Current windowmanager and data context

   area 

(readonly)

  Type: 

[`Area`](bpy.types.Area.html#bpy.types.Area) | None

      asset 

(readonly)

  Type: 

[`AssetRepresentation`](bpy.types.AssetRepresentation.html#bpy.types.AssetRepresentation) | None

      blend_data 

(readonly)

  Type: 

[`BlendData`](bpy.types.BlendData.html#bpy.types.BlendData) | None

      collection 

(readonly)

  Type: 

[`Collection`](bpy.types.Collection.html#bpy.types.Collection) | None

      engine 

(default “”, readonly, never None)

  Type: 

str

      gizmo_group 

(readonly)

  Type: 

[`GizmoGroup`](bpy.types.GizmoGroup.html#bpy.types.GizmoGroup) | None

      layer_collection 

(readonly)

  Type: 

[`LayerCollection`](bpy.types.LayerCollection.html#bpy.types.LayerCollection) | None

      mode 

(default `'EDIT_MESH'`, readonly)

  Type: 

Literal[[Context Mode Items](bpy_types_enum_items/context_mode_items.html#rna-enum-context-mode-items)]

      preferences 

(readonly)

  Type: 

[`Preferences`](bpy.types.Preferences.html#bpy.types.Preferences) | None

      region 

(readonly)

  Type: 

[`Region`](bpy.types.Region.html#bpy.types.Region) | None

      region_data 

(readonly)

  Type: 

[`RegionView3D`](bpy.types.RegionView3D.html#bpy.types.RegionView3D) | None

      region_popup 

The temporary region for pop-ups (including menus and pop-overs) (readonly)

  Type: 

[`Region`](bpy.types.Region.html#bpy.types.Region) | None

      scene 

(readonly)

  Type: 

[`Scene`](bpy.types.Scene.html#bpy.types.Scene) | None

      screen 

(readonly)

  Type: 

[`Screen`](bpy.types.Screen.html#bpy.types.Screen) | None

      space_data 

The current space, may be None in background-mode, when the cursor is outside the window or when using menu-search (readonly)

  Type: 

[`Space`](bpy.types.Space.html#bpy.types.Space) | None

      tool_settings 

(readonly)

  Type: 

[`ToolSettings`](bpy.types.ToolSettings.html#bpy.types.ToolSettings) | None

      view_layer 

(readonly)

  Type: 

[`ViewLayer`](bpy.types.ViewLayer.html#bpy.types.ViewLayer) | None

      window 

(readonly)

  Type: 

[`Window`](bpy.types.Window.html#bpy.types.Window) | None

      window_manager 

(readonly)

  Type: 

[`WindowManager`](bpy.types.WindowManager.html#bpy.types.WindowManager) | None

      workspace 

(readonly)

  Type: 

[`WorkSpace`](bpy.types.WorkSpace.html#bpy.types.WorkSpace) | None

    

Buttons Context

   texture_slot  Type: 

[`TextureSlot`](bpy.types.TextureSlot.html#bpy.types.TextureSlot)

      scene  Type: 

[`Scene`](bpy.types.Scene.html#bpy.types.Scene)

      world  Type: 

[`World`](bpy.types.World.html#bpy.types.World)

      object  Type: 

[`Object`](bpy.types.Object.html#bpy.types.Object)

      mesh  Type: 

[`Mesh`](bpy.types.Mesh.html#bpy.types.Mesh)

      armature  Type: 

[`Armature`](bpy.types.Armature.html#bpy.types.Armature)

      lattice  Type: 

[`Lattice`](bpy.types.Lattice.html#bpy.types.Lattice)

      curve  Type: 

[`Curve`](bpy.types.Curve.html#bpy.types.Curve)

      meta_ball  Type: 

[`MetaBall`](bpy.types.MetaBall.html#bpy.types.MetaBall)

      light  Type: 

[`Light`](bpy.types.Light.html#bpy.types.Light)

      speaker  Type: 

[`Speaker`](bpy.types.Speaker.html#bpy.types.Speaker)

      lightprobe  Type: 

[`LightProbe`](bpy.types.LightProbe.html#bpy.types.LightProbe)

      camera  Type: 

[`Camera`](bpy.types.Camera.html#bpy.types.Camera)

      material  Type: 

[`Material`](bpy.types.Material.html#bpy.types.Material)

      material_slot  Type: 

[`MaterialSlot`](bpy.types.MaterialSlot.html#bpy.types.MaterialSlot)

      texture  Type: 

[`Texture`](bpy.types.Texture.html#bpy.types.Texture)

      texture_user  Type: 

[`ID`](bpy.types.ID.html#bpy.types.ID)

      texture_user_property  Type: 

[`Property`](bpy.types.Property.html#bpy.types.Property)

      texture_node  Type: 

[`Node`](bpy.types.Node.html#bpy.types.Node)

      bone  Type: 

[`Bone`](bpy.types.Bone.html#bpy.types.Bone)

      edit_bone  Type: 

[`EditBone`](bpy.types.EditBone.html#bpy.types.EditBone)

      pose_bone  Type: 

[`PoseBone`](bpy.types.PoseBone.html#bpy.types.PoseBone)

      particle_system  Type: 

[`ParticleSystem`](bpy.types.ParticleSystem.html#bpy.types.ParticleSystem)

      particle_system_editable  Type: 

[`ParticleSystem`](bpy.types.ParticleSystem.html#bpy.types.ParticleSystem)

      particle_settings  Type: 

[`ParticleSettings`](bpy.types.ParticleSettings.html#bpy.types.ParticleSettings)

      cloth  Type: 

[`ClothModifier`](bpy.types.ClothModifier.html#bpy.types.ClothModifier)

      soft_body  Type: 

[`SoftBodyModifier`](bpy.types.SoftBodyModifier.html#bpy.types.SoftBodyModifier)

      fluid  Type: 

[`FluidModifier`](bpy.types.FluidModifier.html#bpy.types.FluidModifier)

      collision  Type: 

[`CollisionModifier`](bpy.types.CollisionModifier.html#bpy.types.CollisionModifier)

      brush  Type: 

[`Brush`](bpy.types.Brush.html#bpy.types.Brush)

      dynamic_paint  Type: 

[`DynamicPaintModifier`](bpy.types.DynamicPaintModifier.html#bpy.types.DynamicPaintModifier)

      line_style  Type: 

[`FreestyleLineStyle`](bpy.types.FreestyleLineStyle.html#bpy.types.FreestyleLineStyle)

      collection  Type: 

[`LayerCollection`](bpy.types.LayerCollection.html#bpy.types.LayerCollection)

      gpencil  Type: 

[`GreasePencil`](bpy.types.GreasePencil.html#bpy.types.GreasePencil)

      grease_pencil  Type: 

[`GreasePencil`](bpy.types.GreasePencil.html#bpy.types.GreasePencil)

      curves  Type: 

[`Curves`](bpy.types.Curves.html#bpy.types.Curves)

      pointcloud  Type: 

[`PointCloud`](bpy.types.PointCloud.html#bpy.types.PointCloud)

      volume  Type: 

[`Volume`](bpy.types.Volume.html#bpy.types.Volume)

      strip  Type: 

[`Strip`](bpy.types.Strip.html#bpy.types.Strip)

      strip_modifier  Type: 

[`StripModifier`](bpy.types.StripModifier.html#bpy.types.StripModifier)

    

Clip Context

   edit_movieclip  Type: 

[`MovieClip`](bpy.types.MovieClip.html#bpy.types.MovieClip)

      edit_mask  Type: 

[`Mask`](bpy.types.Mask.html#bpy.types.Mask)

    

File Context

   active_file  Type: 

[`FileSelectEntry`](bpy.types.FileSelectEntry.html#bpy.types.FileSelectEntry)

      selected_files  Type: 

Sequence[[`FileSelectEntry`](bpy.types.FileSelectEntry.html#bpy.types.FileSelectEntry)]

      asset_library_reference  Type: 

[`AssetLibraryReference`](bpy.types.AssetLibraryReference.html#bpy.types.AssetLibraryReference)

      asset  Type: 

[`AssetRepresentation`](bpy.types.AssetRepresentation.html#bpy.types.AssetRepresentation)

      selected_assets  Type: 

Sequence[[`AssetRepresentation`](bpy.types.AssetRepresentation.html#bpy.types.AssetRepresentation)]

      id  Type: 

[`ID`](bpy.types.ID.html#bpy.types.ID)

      selected_ids  Type: 

Sequence[[`ID`](bpy.types.ID.html#bpy.types.ID)]

    

Image Context

   edit_image  Type: 

[`Image`](bpy.types.Image.html#bpy.types.Image)

      edit_mask  Type: 

[`Mask`](bpy.types.Mask.html#bpy.types.Mask)

    

Node Context

   selected_nodes  Type: 

Sequence[[`Node`](bpy.types.Node.html#bpy.types.Node)]

      active_node  Type: 

[`Node`](bpy.types.Node.html#bpy.types.Node)

      light  Type: 

[`Light`](bpy.types.Light.html#bpy.types.Light)

      material  Type: 

[`Material`](bpy.types.Material.html#bpy.types.Material)

      world  Type: 

[`World`](bpy.types.World.html#bpy.types.World)

    

Screen Context

   scene  Type: 

[`Scene`](bpy.types.Scene.html#bpy.types.Scene)

      view_layer  Type: 

[`ViewLayer`](bpy.types.ViewLayer.html#bpy.types.ViewLayer)

      visible_objects  Type: 

Sequence[[`Object`](bpy.types.Object.html#bpy.types.Object)]

      selectable_objects  Type: 

Sequence[[`Object`](bpy.types.Object.html#bpy.types.Object)]

      selected_objects  Type: 

Sequence[[`Object`](bpy.types.Object.html#bpy.types.Object)]

      editable_objects  Type: 

Sequence[[`Object`](bpy.types.Object.html#bpy.types.Object)]

      selected_editable_objects  Type: 

Sequence[[`Object`](bpy.types.Object.html#bpy.types.Object)]

      objects_in_mode  Type: 

Sequence[[`Object`](bpy.types.Object.html#bpy.types.Object)]

      objects_in_mode_unique_data  Type: 

Sequence[[`Object`](bpy.types.Object.html#bpy.types.Object)]

      visible_bones  Type: 

Sequence[[`EditBone`](bpy.types.EditBone.html#bpy.types.EditBone)]

      editable_bones  Type: 

Sequence[[`EditBone`](bpy.types.EditBone.html#bpy.types.EditBone)]

      selected_bones  Type: 

Sequence[[`EditBone`](bpy.types.EditBone.html#bpy.types.EditBone)]

      selected_editable_bones  Type: 

Sequence[[`EditBone`](bpy.types.EditBone.html#bpy.types.EditBone)]

      visible_pose_bones  Type: 

Sequence[[`PoseBone`](bpy.types.PoseBone.html#bpy.types.PoseBone)]

      selected_pose_bones  Type: 

Sequence[[`PoseBone`](bpy.types.PoseBone.html#bpy.types.PoseBone)]

      selected_pose_bones_from_active_object  Type: 

Sequence[[`PoseBone`](bpy.types.PoseBone.html#bpy.types.PoseBone)]

      active_bone  Type: 

[`EditBone`](bpy.types.EditBone.html#bpy.types.EditBone) | [`Bone`](bpy.types.Bone.html#bpy.types.Bone)

      active_pose_bone  Type: 

[`PoseBone`](bpy.types.PoseBone.html#bpy.types.PoseBone)

      active_object  Type: 

[`Object`](bpy.types.Object.html#bpy.types.Object)

      object  Type: 

[`Object`](bpy.types.Object.html#bpy.types.Object)

      edit_object  Type: 

[`Object`](bpy.types.Object.html#bpy.types.Object)

      sculpt_object  Type: 

[`Object`](bpy.types.Object.html#bpy.types.Object)

      vertex_paint_object  Type: 

[`Object`](bpy.types.Object.html#bpy.types.Object)

      weight_paint_object  Type: 

[`Object`](bpy.types.Object.html#bpy.types.Object)

      image_paint_object  Type: 

[`Object`](bpy.types.Object.html#bpy.types.Object)

      particle_edit_object  Type: 

[`Object`](bpy.types.Object.html#bpy.types.Object)

      pose_object  Type: 

[`Object`](bpy.types.Object.html#bpy.types.Object)

      active_nla_track  Type: 

[`NlaTrack`](bpy.types.NlaTrack.html#bpy.types.NlaTrack)

      active_nla_strip  Type: 

[`NlaStrip`](bpy.types.NlaStrip.html#bpy.types.NlaStrip)

      selected_nla_strips  Type: 

Sequence[[`NlaStrip`](bpy.types.NlaStrip.html#bpy.types.NlaStrip)]

      selected_movieclip_tracks  Type: 

Sequence[[`MovieTrackingTrack`](bpy.types.MovieTrackingTrack.html#bpy.types.MovieTrackingTrack)]

      annotation_data  Type: 

[`GreasePencil`](bpy.types.GreasePencil.html#bpy.types.GreasePencil)

      annotation_data_owner  Type: 

[`ID`](bpy.types.ID.html#bpy.types.ID)

      active_annotation_layer  Type: 

[`AnnotationLayer`](bpy.types.AnnotationLayer.html#bpy.types.AnnotationLayer)

      grease_pencil  Type: 

[`GreasePencil`](bpy.types.GreasePencil.html#bpy.types.GreasePencil)

      active_operator  Type: 

[`Operator`](bpy.types.Operator.html#bpy.types.Operator)

      active_action  Type: 

[`Action`](bpy.types.Action.html#bpy.types.Action)

      selected_visible_actions  Type: 

Sequence[[`Action`](bpy.types.Action.html#bpy.types.Action)]

      selected_editable_actions  Type: 

Sequence[[`Action`](bpy.types.Action.html#bpy.types.Action)]

      visible_fcurves  Type: 

Sequence[[`FCurve`](bpy.types.FCurve.html#bpy.types.FCurve)]

      editable_fcurves  Type: 

Sequence[[`FCurve`](bpy.types.FCurve.html#bpy.types.FCurve)]

      selected_visible_fcurves  Type: 

Sequence[[`FCurve`](bpy.types.FCurve.html#bpy.types.FCurve)]

      selected_editable_fcurves  Type: 

Sequence[[`FCurve`](bpy.types.FCurve.html#bpy.types.FCurve)]

      active_editable_fcurve  Type: 

[`FCurve`](bpy.types.FCurve.html#bpy.types.FCurve)

      selected_editable_keyframes  Type: 

Sequence[[`Keyframe`](bpy.types.Keyframe.html#bpy.types.Keyframe)]

      ui_list  Type: 

[`UIList`](bpy.types.UIList.html#bpy.types.UIList)

      property  Type: 

[`AnyType`](bpy.types.AnyType.html#bpy.types.AnyType) | `str` | `int`

   

Get the property associated with a hovered button. Returns a tuple of the data-block, data path to the property, and array index.

  

Note

 

When the property doesn’t have an associated [`bpy.types.ID`](bpy.types.ID.html#bpy.types.ID) non-ID data may be returned. This may occur when accessing windowing data, for example, operator properties.

  

```python
import bpy

# Example inserting keyframe for the hovered property.
active_property = bpy.context.property
if active_property:
    datablock, data_path, index = active_property
    datablock.keyframe_insert(data_path=data_path, index=index, frame=1)
```

     asset_library_reference  Type: 

[`AssetLibraryReference`](bpy.types.AssetLibraryReference.html#bpy.types.AssetLibraryReference)

      active_strip  Type: 

[`Strip`](bpy.types.Strip.html#bpy.types.Strip)

      strips  Type: 

Sequence[[`Strip`](bpy.types.Strip.html#bpy.types.Strip)]

      selected_strips  Type: 

Sequence[[`Strip`](bpy.types.Strip.html#bpy.types.Strip)]

      selected_editable_strips  Type: 

Sequence[[`Strip`](bpy.types.Strip.html#bpy.types.Strip)]

      sequencer_scene  Type: 

[`Scene`](bpy.types.Scene.html#bpy.types.Scene)

    

Sequencer Context

   edit_mask  Type: 

[`Mask`](bpy.types.Mask.html#bpy.types.Mask)

      tool_settings  Type: 

[`ToolSettings`](bpy.types.ToolSettings.html#bpy.types.ToolSettings)

    

Text Context

   edit_text  Type: 

[`Text`](bpy.types.Text.html#bpy.types.Text)

    

View3D Context

   active_object  Type: 

[`Object`](bpy.types.Object.html#bpy.types.Object)

      selected_ids  Type: 

Sequence[[`ID`](bpy.types.ID.html#bpy.types.ID)]

    

Methods

   evaluated_depsgraph_get() 

Get the dependency graph for the current scene and view layer, to access to data-blocks with animation and modifiers applied. If any data-blocks have been edited, the dependency graph will be updated. This invalidates all references to evaluated data-blocks from the dependency graph.

  Returns: 

Evaluated dependency graph

  Return type: 

[`Depsgraph`](bpy.types.Depsgraph.html#bpy.types.Depsgraph)

      copy() 

Get context members as a dictionary.

  Return type: 

dict[str, Any]

      path_resolve(path, coerce=True) 

Returns the property from the path, raise an exception when not found.

  Parameters:  
- path (str) – patch which this property resolves. 
- coerce (bool) – optional argument, when True, the property will be converted into its Python representation.   Returns: 

Property value or property object.

  Return type: 

Any | [`bpy_prop`](bpy.types.bpy_prop.html#bpy.types.bpy_prop)

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

      temp_override(*, window=None, screen=None, area=None, region=None, **keywords) 

Context manager to temporarily override members in the context.

  Parameters:  
- window ([`bpy.types.Window`](bpy.types.Window.html#bpy.types.Window) | None) – Window override or None. 
- screen ([`bpy.types.Screen`](bpy.types.Screen.html#bpy.types.Screen) | None) – 

Screen override or None.

  

Note

 

Switching to or away from full-screen areas & temporary screens isn’t supported. Passing in these screens will raise an exception, actions that leave the context such screens won’t restore the prior screen.

   

Note

 

Changing the screen has wider implications than other arguments as it will also change the works-space and potentially the scene (when pinned). 
- area ([`bpy.types.Area`](bpy.types.Area.html#bpy.types.Area) | None) – Area override or None. 
- region ([`bpy.types.Region`](bpy.types.Region.html#bpy.types.Region) | None) – Region override or None. 
- keywords – Additional keywords override context members.   Returns: 

The context manager.

  Return type: 

[`bpy.types.ContextTempOverride`](bpy.types.ContextTempOverride.html#bpy.types.ContextTempOverride)

   

Overriding the context can be used to temporarily activate another `window` / `area` & `region`, as well as other members such as the `active_object` or `bone`.

 

Notes:

  
- When overriding window, area and regions: the arguments must be consistent, so any region argument that’s passed in must be contained by the current area or the area passed in. The same goes for the area needing to be contained in the current window. 
- Temporary context overrides may be nested, when this is done, members will be added to the existing overrides. 
- Context members are restored outside the scope of the context-manager. The only exception to this is when the data is no longer available.

 

In the event windowing data was removed (for example), the state of the context is left as-is. While this isn’t likely to happen, explicit window operation such as closing windows or loading a new file remove the windowing data that was set before the temporary context was created.  

Overriding the context can be useful to set the context after loading files (which would otherwise be None). For example:

 

```python
import bpy
from bpy import context

# Reload the current file and select all.
bpy.ops.wm.open_mainfile(filepath=bpy.data.filepath)
window = context.window_manager.windows[0]
with context.temp_override(window=window):
    bpy.ops.mesh.primitive_uv_sphere_add()
    # The context override is needed so it's possible to set edit-mode.
    bpy.ops.object.mode_set(mode='EDIT')
```

  

This example shows how it’s possible to add an object to the scene in another window.

 

```python
import bpy
from bpy import context

win_active = context.window
win_other = None
for win_iter in context.window_manager.windows:
    if win_iter != win_active:
        win_other = win_iter
        break

# Add cube in the other window.
with context.temp_override(window=win_other):
    bpy.ops.mesh.primitive_cube_add()
```

  

Logging Context Member Access

 

Context members can be logged by calling `logging_set(True)` on the “with” target of a temporary override. This will log the members that are being accessed during the operation and may assist in debugging when it is unclear which members need to be overridden.

 

In the event an operator fails to execute because of a missing context member, logging may help identify which member is required.

 

This example shows how to log which context members are being accessed. Log statements are printed to your system’s console.

  

Important

 

Not all operators rely on Context Members and therefore will not be affected by `bpy.types.Context.temp_override`, use logging to what members if any are accessed.

  

```python
import bpy
from bpy import context

my_objects = [context.scene.camera]

with context.temp_override(selected_objects=my_objects) as override:
    override.logging_set(
        True,  # Enable logging.
        hide_missing=True,  # Don't show failed attempts.
    )
    bpy.ops.object.delete()
```

     

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

  
- [`AssetShelf.draw_context_menu`](bpy.types.AssetShelf.html#bpy.types.AssetShelf.draw_context_menu) 
- [`AssetShelf.poll`](bpy.types.AssetShelf.html#bpy.types.AssetShelf.poll) 
- [`FileHandler.poll_drop`](bpy.types.FileHandler.html#bpy.types.FileHandler.poll_drop) 
- [`Gizmo.draw`](bpy.types.Gizmo.html#bpy.types.Gizmo.draw) 
- [`Gizmo.draw_select`](bpy.types.Gizmo.html#bpy.types.Gizmo.draw_select) 
- [`Gizmo.exit`](bpy.types.Gizmo.html#bpy.types.Gizmo.exit) 
- [`Gizmo.invoke`](bpy.types.Gizmo.html#bpy.types.Gizmo.invoke) 
- [`Gizmo.modal`](bpy.types.Gizmo.html#bpy.types.Gizmo.modal) 
- [`Gizmo.test_select`](bpy.types.Gizmo.html#bpy.types.Gizmo.test_select) 
- [`GizmoGroup.draw_prepare`](bpy.types.GizmoGroup.html#bpy.types.GizmoGroup.draw_prepare) 
- [`GizmoGroup.invoke_prepare`](bpy.types.GizmoGroup.html#bpy.types.GizmoGroup.invoke_prepare) 
- [`GizmoGroup.poll`](bpy.types.GizmoGroup.html#bpy.types.GizmoGroup.poll) 
- [`GizmoGroup.refresh`](bpy.types.GizmoGroup.html#bpy.types.GizmoGroup.refresh) 
- [`GizmoGroup.setup`](bpy.types.GizmoGroup.html#bpy.types.GizmoGroup.setup) 
- [`Header.draw`](bpy.types.Header.html#bpy.types.Header.draw) 
- [`KeyingSetInfo.generate`](bpy.types.KeyingSetInfo.html#bpy.types.KeyingSetInfo.generate) 
- [`KeyingSetInfo.iterator`](bpy.types.KeyingSetInfo.html#bpy.types.KeyingSetInfo.iterator) 
- [`KeyingSetInfo.poll`](bpy.types.KeyingSetInfo.html#bpy.types.KeyingSetInfo.poll) 
- [`Macro.draw`](bpy.types.Macro.html#bpy.types.Macro.draw) 
- [`Macro.poll`](bpy.types.Macro.html#bpy.types.Macro.poll) 
- [`Menu.draw`](bpy.types.Menu.html#bpy.types.Menu.draw) 
- [`Menu.poll`](bpy.types.Menu.html#bpy.types.Menu.poll) 
- [`Node.draw_buttons`](bpy.types.Node.html#bpy.types.Node.draw_buttons) 
- [`Node.draw_buttons_ext`](bpy.types.Node.html#bpy.types.Node.draw_buttons_ext) 
- [`Node.init`](bpy.types.Node.html#bpy.types.Node.init) 
- [`Node.socket_value_update`](bpy.types.Node.html#bpy.types.Node.socket_value_update) 
- [`NodeInternal.draw_buttons`](bpy.types.NodeInternal.html#bpy.types.NodeInternal.draw_buttons) 
- [`NodeInternal.draw_buttons_ext`](bpy.types.NodeInternal.html#bpy.types.NodeInternal.draw_buttons_ext) 
- [`NodeSocket.draw`](bpy.types.NodeSocket.html#bpy.types.NodeSocket.draw) 
- [`NodeSocket.draw_color`](bpy.types.NodeSocket.html#bpy.types.NodeSocket.draw_color) 
- [`NodeSocketStandard.draw`](bpy.types.NodeSocketStandard.html#bpy.types.NodeSocketStandard.draw) 
- [`NodeSocketStandard.draw_color`](bpy.types.NodeSocketStandard.html#bpy.types.NodeSocketStandard.draw_color) 
- [`NodeTree.get_from_context`](bpy.types.NodeTree.html#bpy.types.NodeTree.get_from_context) 
- [`NodeTree.interface_update`](bpy.types.NodeTree.html#bpy.types.NodeTree.interface_update) 
- [`NodeTree.poll`](bpy.types.NodeTree.html#bpy.types.NodeTree.poll) 
- [`NodeTreeInterfaceSocket.draw`](bpy.types.NodeTreeInterfaceSocket.html#bpy.types.NodeTreeInterfaceSocket.draw) 
- [`NodeTreeInterfaceSocketBool.draw`](bpy.types.NodeTreeInterfaceSocketBool.html#bpy.types.NodeTreeInterfaceSocketBool.draw) 
- [`NodeTreeInterfaceSocketBundle.draw`](bpy.types.NodeTreeInterfaceSocketBundle.html#bpy.types.NodeTreeInterfaceSocketBundle.draw) 
- [`NodeTreeInterfaceSocketClosure.draw`](bpy.types.NodeTreeInterfaceSocketClosure.html#bpy.types.NodeTreeInterfaceSocketClosure.draw) 
- [`NodeTreeInterfaceSocketCollection.draw`](bpy.types.NodeTreeInterfaceSocketCollection.html#bpy.types.NodeTreeInterfaceSocketCollection.draw) 
- [`NodeTreeInterfaceSocketColor.draw`](bpy.types.NodeTreeInterfaceSocketColor.html#bpy.types.NodeTreeInterfaceSocketColor.draw) 
- [`NodeTreeInterfaceSocketFloat.draw`](bpy.types.NodeTreeInterfaceSocketFloat.html#bpy.types.NodeTreeInterfaceSocketFloat.draw) 
- [`NodeTreeInterfaceSocketFloatAngle.draw`](bpy.types.NodeTreeInterfaceSocketFloatAngle.html#bpy.types.NodeTreeInterfaceSocketFloatAngle.draw) 
- [`NodeTreeInterfaceSocketFloatColorTemperature.draw`](bpy.types.NodeTreeInterfaceSocketFloatColorTemperature.html#bpy.types.NodeTreeInterfaceSocketFloatColorTemperature.draw) 
- [`NodeTreeInterfaceSocketFloatDistance.draw`](bpy.types.NodeTreeInterfaceSocketFloatDistance.html#bpy.types.NodeTreeInterfaceSocketFloatDistance.draw) 
- [`NodeTreeInterfaceSocketFloatFactor.draw`](bpy.types.NodeTreeInterfaceSocketFloatFactor.html#bpy.types.NodeTreeInterfaceSocketFloatFactor.draw) 
- [`NodeTreeInterfaceSocketFloatFrequency.draw`](bpy.types.NodeTreeInterfaceSocketFloatFrequency.html#bpy.types.NodeTreeInterfaceSocketFloatFrequency.draw) 
- [`NodeTreeInterfaceSocketFloatMass.draw`](bpy.types.NodeTreeInterfaceSocketFloatMass.html#bpy.types.NodeTreeInterfaceSocketFloatMass.draw) 
- [`NodeTreeInterfaceSocketFloatPercentage.draw`](bpy.types.NodeTreeInterfaceSocketFloatPercentage.html#bpy.types.NodeTreeInterfaceSocketFloatPercentage.draw) 
- [`NodeTreeInterfaceSocketFloatPixel.draw`](bpy.types.NodeTreeInterfaceSocketFloatPixel.html#bpy.types.NodeTreeInterfaceSocketFloatPixel.draw) 
- [`NodeTreeInterfaceSocketFloatTime.draw`](bpy.types.NodeTreeInterfaceSocketFloatTime.html#bpy.types.NodeTreeInterfaceSocketFloatTime.draw) 
- [`NodeTreeInterfaceSocketFloatTimeAbsolute.draw`](bpy.types.NodeTreeInterfaceSocketFloatTimeAbsolute.html#bpy.types.NodeTreeInterfaceSocketFloatTimeAbsolute.draw) 
- [`NodeTreeInterfaceSocketFloatUnsigned.draw`](bpy.types.NodeTreeInterfaceSocketFloatUnsigned.html#bpy.types.NodeTreeInterfaceSocketFloatUnsigned.draw) 
- [`NodeTreeInterfaceSocketFloatWavelength.draw`](bpy.types.NodeTreeInterfaceSocketFloatWavelength.html#bpy.types.NodeTreeInterfaceSocketFloatWavelength.draw) 
- [`NodeTreeInterfaceSocketGeometry.draw`](bpy.types.NodeTreeInterfaceSocketGeometry.html#bpy.types.NodeTreeInterfaceSocketGeometry.draw) 
- [`NodeTreeInterfaceSocketImage.draw`](bpy.types.NodeTreeInterfaceSocketImage.html#bpy.types.NodeTreeInterfaceSocketImage.draw) 
- [`NodeTreeInterfaceSocketInt.draw`](bpy.types.NodeTreeInterfaceSocketInt.html#bpy.types.NodeTreeInterfaceSocketInt.draw) 
- [`NodeTreeInterfaceSocketIntFactor.draw`](bpy.types.NodeTreeInterfaceSocketIntFactor.html#bpy.types.NodeTreeInterfaceSocketIntFactor.draw) 
- [`NodeTreeInterfaceSocketIntPercentage.draw`](bpy.types.NodeTreeInterfaceSocketIntPercentage.html#bpy.types.NodeTreeInterfaceSocketIntPercentage.draw) 
- [`NodeTreeInterfaceSocketIntPixel.draw`](bpy.types.NodeTreeInterfaceSocketIntPixel.html#bpy.types.NodeTreeInterfaceSocketIntPixel.draw) 
- [`NodeTreeInterfaceSocketIntUnsigned.draw`](bpy.types.NodeTreeInterfaceSocketIntUnsigned.html#bpy.types.NodeTreeInterfaceSocketIntUnsigned.draw) 
- [`NodeTreeInterfaceSocketIntVector2D.draw`](bpy.types.NodeTreeInterfaceSocketIntVector2D.html#bpy.types.NodeTreeInterfaceSocketIntVector2D.draw) 
- [`NodeTreeInterfaceSocketIntVector3D.draw`](bpy.types.NodeTreeInterfaceSocketIntVector3D.html#bpy.types.NodeTreeInterfaceSocketIntVector3D.draw) 
- [`NodeTreeInterfaceSocketIntVectorFactor2D.draw`](bpy.types.NodeTreeInterfaceSocketIntVectorFactor2D.html#bpy.types.NodeTreeInterfaceSocketIntVectorFactor2D.draw) 
- [`NodeTreeInterfaceSocketIntVectorFactor3D.draw`](bpy.types.NodeTreeInterfaceSocketIntVectorFactor3D.html#bpy.types.NodeTreeInterfaceSocketIntVectorFactor3D.draw) 
- [`NodeTreeInterfaceSocketIntVectorPercentage2D.draw`](bpy.types.NodeTreeInterfaceSocketIntVectorPercentage2D.html#bpy.types.NodeTreeInterfaceSocketIntVectorPercentage2D.draw) 
- [`NodeTreeInterfaceSocketIntVectorPercentage3D.draw`](bpy.types.NodeTreeInterfaceSocketIntVectorPercentage3D.html#bpy.types.NodeTreeInterfaceSocketIntVectorPercentage3D.draw) 
- [`NodeTreeInterfaceSocketIntVectorPixel2D.draw`](bpy.types.NodeTreeInterfaceSocketIntVectorPixel2D.html#bpy.types.NodeTreeInterfaceSocketIntVectorPixel2D.draw) 
- [`NodeTreeInterfaceSocketIntVectorPixel3D.draw`](bpy.types.NodeTreeInterfaceSocketIntVectorPixel3D.html#bpy.types.NodeTreeInterfaceSocketIntVectorPixel3D.draw) 
- [`NodeTreeInterfaceSocketIntVectorUnsigned2D.draw`](bpy.types.NodeTreeInterfaceSocketIntVectorUnsigned2D.html#bpy.types.NodeTreeInterfaceSocketIntVectorUnsigned2D.draw) 
- [`NodeTreeInterfaceSocketIntVectorUnsigned3D.draw`](bpy.types.NodeTreeInterfaceSocketIntVectorUnsigned3D.html#bpy.types.NodeTreeInterfaceSocketIntVectorUnsigned3D.draw)   
- [`NodeTreeInterfaceSocketMaterial.draw`](bpy.types.NodeTreeInterfaceSocketMaterial.html#bpy.types.NodeTreeInterfaceSocketMaterial.draw) 
- [`NodeTreeInterfaceSocketMatrix.draw`](bpy.types.NodeTreeInterfaceSocketMatrix.html#bpy.types.NodeTreeInterfaceSocketMatrix.draw) 
- [`NodeTreeInterfaceSocketMenu.draw`](bpy.types.NodeTreeInterfaceSocketMenu.html#bpy.types.NodeTreeInterfaceSocketMenu.draw) 
- [`NodeTreeInterfaceSocketObject.draw`](bpy.types.NodeTreeInterfaceSocketObject.html#bpy.types.NodeTreeInterfaceSocketObject.draw) 
- [`NodeTreeInterfaceSocketRotation.draw`](bpy.types.NodeTreeInterfaceSocketRotation.html#bpy.types.NodeTreeInterfaceSocketRotation.draw) 
- [`NodeTreeInterfaceSocketShader.draw`](bpy.types.NodeTreeInterfaceSocketShader.html#bpy.types.NodeTreeInterfaceSocketShader.draw) 
- [`NodeTreeInterfaceSocketString.draw`](bpy.types.NodeTreeInterfaceSocketString.html#bpy.types.NodeTreeInterfaceSocketString.draw) 
- [`NodeTreeInterfaceSocketStringFilePath.draw`](bpy.types.NodeTreeInterfaceSocketStringFilePath.html#bpy.types.NodeTreeInterfaceSocketStringFilePath.draw) 
- [`NodeTreeInterfaceSocketTexture.draw`](bpy.types.NodeTreeInterfaceSocketTexture.html#bpy.types.NodeTreeInterfaceSocketTexture.draw) 
- [`NodeTreeInterfaceSocketVector.draw`](bpy.types.NodeTreeInterfaceSocketVector.html#bpy.types.NodeTreeInterfaceSocketVector.draw) 
- [`NodeTreeInterfaceSocketVector2D.draw`](bpy.types.NodeTreeInterfaceSocketVector2D.html#bpy.types.NodeTreeInterfaceSocketVector2D.draw) 
- [`NodeTreeInterfaceSocketVector4D.draw`](bpy.types.NodeTreeInterfaceSocketVector4D.html#bpy.types.NodeTreeInterfaceSocketVector4D.draw) 
- [`NodeTreeInterfaceSocketVectorAcceleration.draw`](bpy.types.NodeTreeInterfaceSocketVectorAcceleration.html#bpy.types.NodeTreeInterfaceSocketVectorAcceleration.draw) 
- [`NodeTreeInterfaceSocketVectorAcceleration2D.draw`](bpy.types.NodeTreeInterfaceSocketVectorAcceleration2D.html#bpy.types.NodeTreeInterfaceSocketVectorAcceleration2D.draw) 
- [`NodeTreeInterfaceSocketVectorAcceleration4D.draw`](bpy.types.NodeTreeInterfaceSocketVectorAcceleration4D.html#bpy.types.NodeTreeInterfaceSocketVectorAcceleration4D.draw) 
- [`NodeTreeInterfaceSocketVectorDirection.draw`](bpy.types.NodeTreeInterfaceSocketVectorDirection.html#bpy.types.NodeTreeInterfaceSocketVectorDirection.draw) 
- [`NodeTreeInterfaceSocketVectorDirection2D.draw`](bpy.types.NodeTreeInterfaceSocketVectorDirection2D.html#bpy.types.NodeTreeInterfaceSocketVectorDirection2D.draw) 
- [`NodeTreeInterfaceSocketVectorDirection4D.draw`](bpy.types.NodeTreeInterfaceSocketVectorDirection4D.html#bpy.types.NodeTreeInterfaceSocketVectorDirection4D.draw) 
- [`NodeTreeInterfaceSocketVectorEuler.draw`](bpy.types.NodeTreeInterfaceSocketVectorEuler.html#bpy.types.NodeTreeInterfaceSocketVectorEuler.draw) 
- [`NodeTreeInterfaceSocketVectorEuler2D.draw`](bpy.types.NodeTreeInterfaceSocketVectorEuler2D.html#bpy.types.NodeTreeInterfaceSocketVectorEuler2D.draw) 
- [`NodeTreeInterfaceSocketVectorEuler4D.draw`](bpy.types.NodeTreeInterfaceSocketVectorEuler4D.html#bpy.types.NodeTreeInterfaceSocketVectorEuler4D.draw) 
- [`NodeTreeInterfaceSocketVectorFactor.draw`](bpy.types.NodeTreeInterfaceSocketVectorFactor.html#bpy.types.NodeTreeInterfaceSocketVectorFactor.draw) 
- [`NodeTreeInterfaceSocketVectorFactor2D.draw`](bpy.types.NodeTreeInterfaceSocketVectorFactor2D.html#bpy.types.NodeTreeInterfaceSocketVectorFactor2D.draw) 
- [`NodeTreeInterfaceSocketVectorFactor4D.draw`](bpy.types.NodeTreeInterfaceSocketVectorFactor4D.html#bpy.types.NodeTreeInterfaceSocketVectorFactor4D.draw) 
- [`NodeTreeInterfaceSocketVectorPercentage.draw`](bpy.types.NodeTreeInterfaceSocketVectorPercentage.html#bpy.types.NodeTreeInterfaceSocketVectorPercentage.draw) 
- [`NodeTreeInterfaceSocketVectorPercentage2D.draw`](bpy.types.NodeTreeInterfaceSocketVectorPercentage2D.html#bpy.types.NodeTreeInterfaceSocketVectorPercentage2D.draw) 
- [`NodeTreeInterfaceSocketVectorPercentage4D.draw`](bpy.types.NodeTreeInterfaceSocketVectorPercentage4D.html#bpy.types.NodeTreeInterfaceSocketVectorPercentage4D.draw) 
- [`NodeTreeInterfaceSocketVectorPixel.draw`](bpy.types.NodeTreeInterfaceSocketVectorPixel.html#bpy.types.NodeTreeInterfaceSocketVectorPixel.draw) 
- [`NodeTreeInterfaceSocketVectorPixel2D.draw`](bpy.types.NodeTreeInterfaceSocketVectorPixel2D.html#bpy.types.NodeTreeInterfaceSocketVectorPixel2D.draw) 
- [`NodeTreeInterfaceSocketVectorPixel4D.draw`](bpy.types.NodeTreeInterfaceSocketVectorPixel4D.html#bpy.types.NodeTreeInterfaceSocketVectorPixel4D.draw) 
- [`NodeTreeInterfaceSocketVectorTranslation.draw`](bpy.types.NodeTreeInterfaceSocketVectorTranslation.html#bpy.types.NodeTreeInterfaceSocketVectorTranslation.draw) 
- [`NodeTreeInterfaceSocketVectorTranslation2D.draw`](bpy.types.NodeTreeInterfaceSocketVectorTranslation2D.html#bpy.types.NodeTreeInterfaceSocketVectorTranslation2D.draw) 
- [`NodeTreeInterfaceSocketVectorTranslation4D.draw`](bpy.types.NodeTreeInterfaceSocketVectorTranslation4D.html#bpy.types.NodeTreeInterfaceSocketVectorTranslation4D.draw) 
- [`NodeTreeInterfaceSocketVectorVelocity.draw`](bpy.types.NodeTreeInterfaceSocketVectorVelocity.html#bpy.types.NodeTreeInterfaceSocketVectorVelocity.draw) 
- [`NodeTreeInterfaceSocketVectorVelocity2D.draw`](bpy.types.NodeTreeInterfaceSocketVectorVelocity2D.html#bpy.types.NodeTreeInterfaceSocketVectorVelocity2D.draw) 
- [`NodeTreeInterfaceSocketVectorVelocity4D.draw`](bpy.types.NodeTreeInterfaceSocketVectorVelocity4D.html#bpy.types.NodeTreeInterfaceSocketVectorVelocity4D.draw) 
- [`NodeTreeInterfaceSocketVectorXYZ.draw`](bpy.types.NodeTreeInterfaceSocketVectorXYZ.html#bpy.types.NodeTreeInterfaceSocketVectorXYZ.draw) 
- [`NodeTreeInterfaceSocketVectorXYZ2D.draw`](bpy.types.NodeTreeInterfaceSocketVectorXYZ2D.html#bpy.types.NodeTreeInterfaceSocketVectorXYZ2D.draw) 
- [`NodeTreeInterfaceSocketVectorXYZ4D.draw`](bpy.types.NodeTreeInterfaceSocketVectorXYZ4D.html#bpy.types.NodeTreeInterfaceSocketVectorXYZ4D.draw) 
- [`Operator.cancel`](bpy.types.Operator.html#bpy.types.Operator.cancel) 
- [`Operator.check`](bpy.types.Operator.html#bpy.types.Operator.check) 
- [`Operator.description`](bpy.types.Operator.html#bpy.types.Operator.description) 
- [`Operator.draw`](bpy.types.Operator.html#bpy.types.Operator.draw) 
- [`Operator.execute`](bpy.types.Operator.html#bpy.types.Operator.execute) 
- [`Operator.invoke`](bpy.types.Operator.html#bpy.types.Operator.invoke) 
- [`Operator.modal`](bpy.types.Operator.html#bpy.types.Operator.modal) 
- [`Operator.poll`](bpy.types.Operator.html#bpy.types.Operator.poll) 
- [`Panel.draw`](bpy.types.Panel.html#bpy.types.Panel.draw) 
- [`Panel.draw_header`](bpy.types.Panel.html#bpy.types.Panel.draw_header) 
- [`Panel.draw_header_preset`](bpy.types.Panel.html#bpy.types.Panel.draw_header_preset) 
- [`Panel.poll`](bpy.types.Panel.html#bpy.types.Panel.poll) 
- [`RenderEngine.draw`](bpy.types.RenderEngine.html#bpy.types.RenderEngine.draw) 
- [`RenderEngine.view_draw`](bpy.types.RenderEngine.html#bpy.types.RenderEngine.view_draw) 
- [`RenderEngine.view_update`](bpy.types.RenderEngine.html#bpy.types.RenderEngine.view_update) 
- [`UIList.draw_filter`](bpy.types.UIList.html#bpy.types.UIList.draw_filter) 
- [`UIList.draw_item`](bpy.types.UIList.html#bpy.types.UIList.draw_item) 
- [`UIList.filter_items`](bpy.types.UIList.html#bpy.types.UIList.filter_items) 
- [`XrSessionState.action_binding_create`](bpy.types.XrSessionState.html#bpy.types.XrSessionState.action_binding_create) 
- [`XrSessionState.action_create`](bpy.types.XrSessionState.html#bpy.types.XrSessionState.action_create) 
- [`XrSessionState.action_set_create`](bpy.types.XrSessionState.html#bpy.types.XrSessionState.action_set_create) 
- [`XrSessionState.action_state_get`](bpy.types.XrSessionState.html#bpy.types.XrSessionState.action_state_get) 
- [`XrSessionState.active_action_set_set`](bpy.types.XrSessionState.html#bpy.types.XrSessionState.active_action_set_set) 
- [`XrSessionState.controller_aim_location_get`](bpy.types.XrSessionState.html#bpy.types.XrSessionState.controller_aim_location_get) 
- [`XrSessionState.controller_aim_rotation_get`](bpy.types.XrSessionState.html#bpy.types.XrSessionState.controller_aim_rotation_get) 
- [`XrSessionState.controller_grip_location_get`](bpy.types.XrSessionState.html#bpy.types.XrSessionState.controller_grip_location_get) 
- [`XrSessionState.controller_grip_rotation_get`](bpy.types.XrSessionState.html#bpy.types.XrSessionState.controller_grip_rotation_get) 
- [`XrSessionState.controller_pose_actions_set`](bpy.types.XrSessionState.html#bpy.types.XrSessionState.controller_pose_actions_set) 
- [`XrSessionState.haptic_action_apply`](bpy.types.XrSessionState.html#bpy.types.XrSessionState.haptic_action_apply) 
- [`XrSessionState.haptic_action_stop`](bpy.types.XrSessionState.html#bpy.types.XrSessionState.haptic_action_stop) 
- [`XrSessionState.is_running`](bpy.types.XrSessionState.html#bpy.types.XrSessionState.is_running) 
- [`XrSessionState.reset_to_base_pose`](bpy.types.XrSessionState.html#bpy.types.XrSessionState.reset_to_base_pose)
