# bpy.types.PropertyGroup

# PropertyGroup(bpy_struct)

  

## Custom Properties

 

PropertyGroups are the base class for dynamically defined sets of properties.

 

They can be used to extend existing Blender data with your own types which can be animated, accessed from the user interface and from Python.

  

Note

 

The values assigned to Blender data are saved to disk but the class definitions are not, this means whenever you load Blender the class needs to be registered too.

 

This is best done by creating an add-on which loads on startup and registers your properties.

   

Note

 

PropertyGroups must be registered before assigning them to Blender data.

   

See also

 

Property types used in class declarations are all in [`bpy.props`](bpy.props.html#module-bpy.props)

  

```python
import bpy

class MyPropertyGroup(bpy.types.PropertyGroup):
    custom_1: bpy.props.FloatProperty(name="My Float")
    custom_2: bpy.props.IntProperty(name="My Int")

bpy.utils.register_class(MyPropertyGroup)

bpy.types.Object.my_prop_grp = bpy.props.PointerProperty(type=MyPropertyGroup)

# Test this worked.
bpy.data.objects[0].my_prop_grp.custom_1 = 22.0
```

  

base class — [`bpy_struct`](bpy.types.bpy_struct.html#bpy.types.bpy_struct)

  

Subclasses

  
- [OperatorFileListElement(PropertyGroup)](bpy.types.OperatorFileListElement.html) 
- [OperatorMousePath(PropertyGroup)](bpy.types.OperatorMousePath.html) 
- [OperatorStrokeElement(PropertyGroup)](bpy.types.OperatorStrokeElement.html) 
- [SelectedUvElement(PropertyGroup)](bpy.types.SelectedUvElement.html)     class bpy.types.PropertyGroup(bpy_struct) 

Group of ID properties

   name 

Unique name used in the code and scripting, can be re-defined in Python sub-classes if needed (default “”, never None)

  Type: 

str

      bl_system_properties_get(*, do_create=False) 

DEBUG ONLY. Internal access to runtime-defined RNA data storage, intended solely for testing and debugging purposes. Do not access it in regular scripting work, and in particular, do not assume that it contains writable data

  Parameters: 

do_create (bool) – Ensure that system properties are created if they do not exist yet (optional)

  Returns: 

The system properties root container, or None if there are no system properties stored in this data yet, and its creation was not requested

  Return type: 

`PropertyGroup`

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

      

### Inherited Properties

  
- [`bpy_struct.id_data`](bpy.types.bpy_struct.html#bpy.types.bpy_struct.id_data)       

### Inherited Functions

  
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

### References

  
- [`AddonPreferences.bl_system_properties_get`](bpy.types.AddonPreferences.html#bpy.types.AddonPreferences.bl_system_properties_get) 
- [`Bone.bl_system_properties_get`](bpy.types.Bone.html#bpy.types.Bone.bl_system_properties_get) 
- [`BoneCollection.bl_system_properties_get`](bpy.types.BoneCollection.html#bpy.types.BoneCollection.bl_system_properties_get) 
- [`CollectionExport.export_properties`](bpy.types.CollectionExport.html#bpy.types.CollectionExport.export_properties) 
- [`CollectionImport.import_properties`](bpy.types.CollectionImport.html#bpy.types.CollectionImport.import_properties) 
- [`EditBone.bl_system_properties_get`](bpy.types.EditBone.html#bpy.types.EditBone.bl_system_properties_get) 
- [`GizmoGroupProperties.bl_system_properties_get`](bpy.types.GizmoGroupProperties.html#bpy.types.GizmoGroupProperties.bl_system_properties_get) 
- [`GizmoProperties.bl_system_properties_get`](bpy.types.GizmoProperties.html#bpy.types.GizmoProperties.bl_system_properties_get) 
- [`ID.bl_system_properties_get`](bpy.types.ID.html#bpy.types.ID.bl_system_properties_get) 
- [`IDPropertyWrapPtr.bl_system_properties_get`](bpy.types.IDPropertyWrapPtr.html#bpy.types.IDPropertyWrapPtr.bl_system_properties_get) 
- [`KeyConfigPreferences.bl_system_properties_get`](bpy.types.KeyConfigPreferences.html#bpy.types.KeyConfigPreferences.bl_system_properties_get) 
- [`Node.bl_system_properties_get`](bpy.types.Node.html#bpy.types.Node.bl_system_properties_get) 
- [`NodeSocket.bl_system_properties_get`](bpy.types.NodeSocket.html#bpy.types.NodeSocket.bl_system_properties_get) 
- [`NodeTreeInterfaceSocket.bl_system_properties_get`](bpy.types.NodeTreeInterfaceSocket.html#bpy.types.NodeTreeInterfaceSocket.bl_system_properties_get) 
- [`NodesModifierProperties.bl_system_properties_get`](bpy.types.NodesModifierProperties.html#bpy.types.NodesModifierProperties.bl_system_properties_get)   
- [`NodesModifierPropertiesEmpty.bl_system_properties_get`](bpy.types.NodesModifierPropertiesEmpty.html#bpy.types.NodesModifierPropertiesEmpty.bl_system_properties_get) 
- [`OperatorProperties.bl_system_properties_get`](bpy.types.OperatorProperties.html#bpy.types.OperatorProperties.bl_system_properties_get) 
- [`PoseBone.bl_system_properties_get`](bpy.types.PoseBone.html#bpy.types.PoseBone.bl_system_properties_get) 
- `PropertyGroup.bl_system_properties_get` 
- [`PropertyGroupItem.collection`](bpy.types.PropertyGroupItem.html#bpy.types.PropertyGroupItem.collection) 
- [`PropertyGroupItem.group`](bpy.types.PropertyGroupItem.html#bpy.types.PropertyGroupItem.group) 
- [`PropertyGroupItem.idp_array`](bpy.types.PropertyGroupItem.html#bpy.types.PropertyGroupItem.idp_array) 
- [`SequencerCompositorModifierProperties.bl_system_properties_get`](bpy.types.SequencerCompositorModifierProperties.html#bpy.types.SequencerCompositorModifierProperties.bl_system_properties_get) 
- [`SequencerCompositorModifierPropertiesEmpty.bl_system_properties_get`](bpy.types.SequencerCompositorModifierPropertiesEmpty.html#bpy.types.SequencerCompositorModifierPropertiesEmpty.bl_system_properties_get) 
- [`Strip.bl_system_properties_get`](bpy.types.Strip.html#bpy.types.Strip.bl_system_properties_get) 
- [`TimelineMarker.bl_system_properties_get`](bpy.types.TimelineMarker.html#bpy.types.TimelineMarker.bl_system_properties_get) 
- [`UIList.bl_system_properties_get`](bpy.types.UIList.html#bpy.types.UIList.bl_system_properties_get) 
- [`View3DShading.bl_system_properties_get`](bpy.types.View3DShading.html#bpy.types.View3DShading.bl_system_properties_get) 
- [`ViewLayer.bl_system_properties_get`](bpy.types.ViewLayer.html#bpy.types.ViewLayer.bl_system_properties_get)
