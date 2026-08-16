# bpy.types.Theme

# Theme(bpy_struct)

 

base class — [`bpy_struct`](bpy.types.bpy_struct.html#bpy.types.bpy_struct)

   class bpy.types.Theme(bpy_struct) 

User interface styling and color settings

   bone_color_sets 

(default None, readonly, never None)

  Type: 

[`bpy_prop_collection`](bpy.types.bpy_prop_collection.html#bpy.types.bpy_prop_collection)[[`ThemeBoneColorSet`](bpy.types.ThemeBoneColorSet.html#bpy.types.ThemeBoneColorSet)]

      clip_editor 

(readonly, never None)

  Type: 

[`ThemeClipEditor`](bpy.types.ThemeClipEditor.html#bpy.types.ThemeClipEditor)

      collection_color 

(default None, readonly, never None)

  Type: 

[`bpy_prop_collection`](bpy.types.bpy_prop_collection.html#bpy.types.bpy_prop_collection)[[`ThemeCollectionColor`](bpy.types.ThemeCollectionColor.html#bpy.types.ThemeCollectionColor)]

      common 

Theme properties shared by different editors (readonly, never None)

  Type: 

[`ThemeCommon`](bpy.types.ThemeCommon.html#bpy.types.ThemeCommon)

      console 

(readonly, never None)

  Type: 

[`ThemeConsole`](bpy.types.ThemeConsole.html#bpy.types.ThemeConsole)

      dopesheet_editor 

(readonly, never None)

  Type: 

[`ThemeDopeSheet`](bpy.types.ThemeDopeSheet.html#bpy.types.ThemeDopeSheet)

      file_browser 

(readonly, never None)

  Type: 

[`ThemeFileBrowser`](bpy.types.ThemeFileBrowser.html#bpy.types.ThemeFileBrowser)

      filepath 

The path to the preset loaded into this theme (if any) (default “”, never None)

  Type: 

str

      graph_editor 

(readonly, never None)

  Type: 

[`ThemeGraphEditor`](bpy.types.ThemeGraphEditor.html#bpy.types.ThemeGraphEditor)

      image_editor 

(readonly, never None)

  Type: 

[`ThemeImageEditor`](bpy.types.ThemeImageEditor.html#bpy.types.ThemeImageEditor)

      info 

(readonly, never None)

  Type: 

[`ThemeInfo`](bpy.types.ThemeInfo.html#bpy.types.ThemeInfo)

      name 

Name of the theme (default “Default”, never None)

  Type: 

str

      nla_editor 

(readonly, never None)

  Type: 

[`ThemeNLAEditor`](bpy.types.ThemeNLAEditor.html#bpy.types.ThemeNLAEditor)

      node_editor 

(readonly, never None)

  Type: 

[`ThemeNodeEditor`](bpy.types.ThemeNodeEditor.html#bpy.types.ThemeNodeEditor)

      outliner 

(readonly, never None)

  Type: 

[`ThemeOutliner`](bpy.types.ThemeOutliner.html#bpy.types.ThemeOutliner)

      preferences 

(readonly, never None)

  Type: 

[`ThemePreferences`](bpy.types.ThemePreferences.html#bpy.types.ThemePreferences)

      properties 

(readonly, never None)

  Type: 

[`ThemeProperties`](bpy.types.ThemeProperties.html#bpy.types.ThemeProperties)

      regions 

Theme properties for common editor regions (readonly, never None)

  Type: 

[`ThemeRegions`](bpy.types.ThemeRegions.html#bpy.types.ThemeRegions)

      sequence_editor 

(readonly, never None)

  Type: 

[`ThemeSequenceEditor`](bpy.types.ThemeSequenceEditor.html#bpy.types.ThemeSequenceEditor)

      spreadsheet 

(readonly, never None)

  Type: 

[`ThemeSpreadsheet`](bpy.types.ThemeSpreadsheet.html#bpy.types.ThemeSpreadsheet)

      statusbar 

(readonly, never None)

  Type: 

[`ThemeStatusBar`](bpy.types.ThemeStatusBar.html#bpy.types.ThemeStatusBar)

      strip_color 

(default None, readonly, never None)

  Type: 

[`bpy_prop_collection`](bpy.types.bpy_prop_collection.html#bpy.types.bpy_prop_collection)[[`ThemeStripColor`](bpy.types.ThemeStripColor.html#bpy.types.ThemeStripColor)]

      text_editor 

(readonly, never None)

  Type: 

[`ThemeTextEditor`](bpy.types.ThemeTextEditor.html#bpy.types.ThemeTextEditor)

      theme_area 

(default `'USER_INTERFACE'`)

  Type: 

Literal[‘USER_INTERFACE’, ‘STYLE’, ‘REGIONS’, ‘COMMON’, ‘VIEW_3D’, ‘DOPESHEET_EDITOR’, ‘FILE_BROWSER’, ‘GRAPH_EDITOR’, ‘IMAGE_EDITOR’, ‘INFO’, ‘CLIP_EDITOR’, ‘NODE_EDITOR’, ‘NLA_EDITOR’, ‘OUTLINER’, ‘PREFERENCES’, ‘PROPERTIES’, ‘CONSOLE’, ‘SPREADSHEET’, ‘STATUSBAR’, ‘TEXT_EDITOR’, ‘TOPBAR’, ‘SEQUENCE_EDITOR’, ‘BONE_COLOR_SETS’]

      topbar 

(readonly, never None)

  Type: 

[`ThemeTopBar`](bpy.types.ThemeTopBar.html#bpy.types.ThemeTopBar)

      user_interface 

(readonly, never None)

  Type: 

[`ThemeUserInterface`](bpy.types.ThemeUserInterface.html#bpy.types.ThemeUserInterface)

      view_3d 

(readonly, never None)

  Type: 

[`ThemeView3D`](bpy.types.ThemeView3D.html#bpy.types.ThemeView3D)

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

  
- [`Preferences.themes`](bpy.types.Preferences.html#bpy.types.Preferences.themes)
