# bpy.types.Preferences

# Preferences(bpy_struct)

 

base class — [`bpy_struct`](bpy.types.bpy_struct.html#bpy.types.bpy_struct)

   class bpy.types.Preferences(bpy_struct) 

Global preferences

   active_section 

Preferences (default `'INTERFACE'`)

  Type: 

Literal[[Preference Section Items](bpy_types_enum_items/preference_section_items.html#rna-enum-preference-section-items)]

      addons 

(default None, readonly)

  Type: 

[`Addons`](bpy.types.Addons.html#bpy.types.Addons)[[`Addon`](bpy.types.Addon.html#bpy.types.Addon)]

      app_template 

(default “”, never None)

  Type: 

str

      apps 

Preferences that work only for apps (readonly, never None)

  Type: 

[`PreferencesApps`](bpy.types.PreferencesApps.html#bpy.types.PreferencesApps)

      asset_libraries 

Setup for custom and builtin asset libraries (readonly, never None)

  Type: 

[`PreferencesAssetLibraries`](bpy.types.PreferencesAssetLibraries.html#bpy.types.PreferencesAssetLibraries)

      autoexec_paths 

(default None, readonly)

  Type: 

[`PathCompareCollection`](bpy.types.PathCompareCollection.html#bpy.types.PathCompareCollection)[[`PathCompare`](bpy.types.PathCompare.html#bpy.types.PathCompare)]

      edit 

Settings for interacting with Blender data (readonly, never None)

  Type: 

[`PreferencesEdit`](bpy.types.PreferencesEdit.html#bpy.types.PreferencesEdit)

      experimental 

Settings for features that are still early in their development stage (readonly, never None)

  Type: 

[`PreferencesExperimental`](bpy.types.PreferencesExperimental.html#bpy.types.PreferencesExperimental)

      extensions 

Settings for extensions (readonly, never None)

  Type: 

[`PreferencesExtensions`](bpy.types.PreferencesExtensions.html#bpy.types.PreferencesExtensions)

      filepaths 

Default paths for external files (readonly, never None)

  Type: 

[`PreferencesFilePaths`](bpy.types.PreferencesFilePaths.html#bpy.types.PreferencesFilePaths)

      inputs 

Settings for input devices (readonly, never None)

  Type: 

[`PreferencesInput`](bpy.types.PreferencesInput.html#bpy.types.PreferencesInput)

      is_dirty 

Preferences have changed (default False)

  Type: 

bool

      keymap 

Shortcut setup for keyboards and other input devices (readonly, never None)

  Type: 

[`PreferencesKeymap`](bpy.types.PreferencesKeymap.html#bpy.types.PreferencesKeymap)

      show_hidden_ids 

Show data-blocks with dot-prefixed names in search menus (default False)

  Type: 

bool

      studio_lights 

(default None, readonly)

  Type: 

[`StudioLights`](bpy.types.StudioLights.html#bpy.types.StudioLights)[[`StudioLight`](bpy.types.StudioLight.html#bpy.types.StudioLight)]

      system 

Graphics driver and operating system settings (readonly, never None)

  Type: 

[`PreferencesSystem`](bpy.types.PreferencesSystem.html#bpy.types.PreferencesSystem)

      themes 

(default None, readonly)

  Type: 

[`bpy_prop_collection`](bpy.types.bpy_prop_collection.html#bpy.types.bpy_prop_collection)[[`Theme`](bpy.types.Theme.html#bpy.types.Theme)]

      ui_styles 

(default None, readonly)

  Type: 

[`bpy_prop_collection`](bpy.types.bpy_prop_collection.html#bpy.types.bpy_prop_collection)[[`ThemeStyle`](bpy.types.ThemeStyle.html#bpy.types.ThemeStyle)]

      use_preferences_save 

Save preferences on exit when modified (unless factory settings have been loaded) (default True)

  Type: 

bool

      use_recent_searches 

Sort the recently searched items at the top (default True)

  Type: 

bool

      version 

Version of Blender the userpref.blend was saved with (array of 3 items, in [0, inf], default (0, 0, 0), readonly)

  Type: 

[`bpy_prop_array`](bpy.types.bpy_prop_array.html#bpy.types.bpy_prop_array)[int]

      view 

Preferences related to viewing data (readonly, never None)

  Type: 

[`PreferencesView`](bpy.types.PreferencesView.html#bpy.types.PreferencesView)

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

  
- [`Context.preferences`](bpy.types.Context.html#bpy.types.Context.preferences)
