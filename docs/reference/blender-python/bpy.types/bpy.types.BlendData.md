# bpy.types.BlendData

# BlendData(bpy_struct)

 

base class — [`bpy_struct`](bpy.types.bpy_struct.html#bpy.types.bpy_struct)

   class bpy.types.BlendData(bpy_struct) 

Main data structure representing a .blend file and all its data-blocks

   actions 

Action data-blocks (default None, readonly)

  Type: 

[`BlendDataActions`](bpy.types.BlendDataActions.html#bpy.types.BlendDataActions)[[`Action`](bpy.types.Action.html#bpy.types.Action)]

      all_ids 

Read-only list of all IDs listed in Blender data-base (default None, readonly)

  Type: 

[`bpy_prop_collection`](bpy.types.bpy_prop_collection.html#bpy.types.bpy_prop_collection)[[`ID`](bpy.types.ID.html#bpy.types.ID)]

      annotations 

Annotation data-blocks (legacy Grease Pencil) (default None, readonly)

  Type: 

[`BlendDataAnnotations`](bpy.types.BlendDataAnnotations.html#bpy.types.BlendDataAnnotations)[[`Annotation`](bpy.types.Annotation.html#bpy.types.Annotation)]

      armatures 

Armature data-blocks (default None, readonly)

  Type: 

[`BlendDataArmatures`](bpy.types.BlendDataArmatures.html#bpy.types.BlendDataArmatures)[[`Armature`](bpy.types.Armature.html#bpy.types.Armature)]

      brushes 

Brush data-blocks (default None, readonly)

  Type: 

[`BlendDataBrushes`](bpy.types.BlendDataBrushes.html#bpy.types.BlendDataBrushes)[[`Brush`](bpy.types.Brush.html#bpy.types.Brush)]

      cache_files 

Cache Files data-blocks (default None, readonly)

  Type: 

[`BlendDataCacheFiles`](bpy.types.BlendDataCacheFiles.html#bpy.types.BlendDataCacheFiles)[[`CacheFile`](bpy.types.CacheFile.html#bpy.types.CacheFile)]

      cameras 

Camera data-blocks (default None, readonly)

  Type: 

[`BlendDataCameras`](bpy.types.BlendDataCameras.html#bpy.types.BlendDataCameras)[[`Camera`](bpy.types.Camera.html#bpy.types.Camera)]

      collections 

Collection data-blocks (default None, readonly)

  Type: 

[`BlendDataCollections`](bpy.types.BlendDataCollections.html#bpy.types.BlendDataCollections)[[`Collection`](bpy.types.Collection.html#bpy.types.Collection)]

      colorspace 

Information about the color space used for data-blocks in a blend file (readonly, never None)

  Type: 

[`BlendFileColorspace`](bpy.types.BlendFileColorspace.html#bpy.types.BlendFileColorspace)

      curves 

Curve data-blocks (default None, readonly)

  Type: 

[`BlendDataCurves`](bpy.types.BlendDataCurves.html#bpy.types.BlendDataCurves)[[`Curve`](bpy.types.Curve.html#bpy.types.Curve)]

      filepath 

Path to the .blend file (default “”, readonly, never None)

  Type: 

str

      fonts 

Vector font data-blocks (default None, readonly)

  Type: 

[`BlendDataFonts`](bpy.types.BlendDataFonts.html#bpy.types.BlendDataFonts)[[`VectorFont`](bpy.types.VectorFont.html#bpy.types.VectorFont)]

      grease_pencils 

Grease Pencil data-blocks (default None, readonly)

  Type: 

[`BlendDataGreasePencilsV3`](bpy.types.BlendDataGreasePencilsV3.html#bpy.types.BlendDataGreasePencilsV3)[[`GreasePencil`](bpy.types.GreasePencil.html#bpy.types.GreasePencil)]

      hair_curves 

Hair curve data-blocks (default None, readonly)

  Type: 

[`BlendDataHairCurves`](bpy.types.BlendDataHairCurves.html#bpy.types.BlendDataHairCurves)[[`Curves`](bpy.types.Curves.html#bpy.types.Curves)]

      images 

Image data-blocks (default None, readonly)

  Type: 

[`BlendDataImages`](bpy.types.BlendDataImages.html#bpy.types.BlendDataImages)[[`Image`](bpy.types.Image.html#bpy.types.Image)]

      is_dirty 

Have recent edits been saved to disk (default False, readonly)

  Type: 

bool

      is_saved 

Has the current session been saved to disk as a .blend file (default False, readonly)

  Type: 

bool

      lattices 

Lattice data-blocks (default None, readonly)

  Type: 

[`BlendDataLattices`](bpy.types.BlendDataLattices.html#bpy.types.BlendDataLattices)[[`Lattice`](bpy.types.Lattice.html#bpy.types.Lattice)]

      libraries 

Library data-blocks (default None, readonly)

  Type: 

[`BlendDataLibraries`](bpy.types.BlendDataLibraries.html#bpy.types.BlendDataLibraries)[[`Library`](bpy.types.Library.html#bpy.types.Library)]

      lightprobes 

Light Probe data-blocks (default None, readonly)

  Type: 

[`BlendDataProbes`](bpy.types.BlendDataProbes.html#bpy.types.BlendDataProbes)[[`LightProbe`](bpy.types.LightProbe.html#bpy.types.LightProbe)]

      lights 

Light data-blocks (default None, readonly)

  Type: 

[`BlendDataLights`](bpy.types.BlendDataLights.html#bpy.types.BlendDataLights)[[`Light`](bpy.types.Light.html#bpy.types.Light)]

      linestyles 

Line Style data-blocks (default None, readonly)

  Type: 

[`BlendDataLineStyles`](bpy.types.BlendDataLineStyles.html#bpy.types.BlendDataLineStyles)[[`FreestyleLineStyle`](bpy.types.FreestyleLineStyle.html#bpy.types.FreestyleLineStyle)]

      masks 

Masks data-blocks (default None, readonly)

  Type: 

[`BlendDataMasks`](bpy.types.BlendDataMasks.html#bpy.types.BlendDataMasks)[[`Mask`](bpy.types.Mask.html#bpy.types.Mask)]

      materials 

Material data-blocks (default None, readonly)

  Type: 

[`BlendDataMaterials`](bpy.types.BlendDataMaterials.html#bpy.types.BlendDataMaterials)[[`Material`](bpy.types.Material.html#bpy.types.Material)]

      meshes 

Mesh data-blocks (default None, readonly)

  Type: 

[`BlendDataMeshes`](bpy.types.BlendDataMeshes.html#bpy.types.BlendDataMeshes)[[`Mesh`](bpy.types.Mesh.html#bpy.types.Mesh)]

      metaballs 

Metaball data-blocks (default None, readonly)

  Type: 

[`BlendDataMetaBalls`](bpy.types.BlendDataMetaBalls.html#bpy.types.BlendDataMetaBalls)[[`MetaBall`](bpy.types.MetaBall.html#bpy.types.MetaBall)]

      movieclips 

Movie Clip data-blocks (default None, readonly)

  Type: 

[`BlendDataMovieClips`](bpy.types.BlendDataMovieClips.html#bpy.types.BlendDataMovieClips)[[`MovieClip`](bpy.types.MovieClip.html#bpy.types.MovieClip)]

      node_groups 

Node group data-blocks (default None, readonly)

  Type: 

[`BlendDataNodeTrees`](bpy.types.BlendDataNodeTrees.html#bpy.types.BlendDataNodeTrees)[[`NodeTree`](bpy.types.NodeTree.html#bpy.types.NodeTree)]

      objects 

Object data-blocks (default None, readonly)

  Type: 

[`BlendDataObjects`](bpy.types.BlendDataObjects.html#bpy.types.BlendDataObjects)[[`Object`](bpy.types.Object.html#bpy.types.Object)]

      paint_curves 

Paint Curves data-blocks (default None, readonly)

  Type: 

[`BlendDataPaintCurves`](bpy.types.BlendDataPaintCurves.html#bpy.types.BlendDataPaintCurves)[[`PaintCurve`](bpy.types.PaintCurve.html#bpy.types.PaintCurve)]

      palettes 

Palette data-blocks (default None, readonly)

  Type: 

[`BlendDataPalettes`](bpy.types.BlendDataPalettes.html#bpy.types.BlendDataPalettes)[[`Palette`](bpy.types.Palette.html#bpy.types.Palette)]

      particles 

Particle data-blocks (default None, readonly)

  Type: 

[`BlendDataParticles`](bpy.types.BlendDataParticles.html#bpy.types.BlendDataParticles)[[`ParticleSettings`](bpy.types.ParticleSettings.html#bpy.types.ParticleSettings)]

      pointclouds 

Point cloud data-blocks (default None, readonly)

  Type: 

[`BlendDataPointClouds`](bpy.types.BlendDataPointClouds.html#bpy.types.BlendDataPointClouds)[[`PointCloud`](bpy.types.PointCloud.html#bpy.types.PointCloud)]

      scenes 

Scene data-blocks (default None, readonly)

  Type: 

[`BlendDataScenes`](bpy.types.BlendDataScenes.html#bpy.types.BlendDataScenes)[[`Scene`](bpy.types.Scene.html#bpy.types.Scene)]

      screens 

Screen data-blocks (default None, readonly)

  Type: 

[`BlendDataScreens`](bpy.types.BlendDataScreens.html#bpy.types.BlendDataScreens)[[`Screen`](bpy.types.Screen.html#bpy.types.Screen)]

      shape_keys 

Shape Key data-blocks (default None, readonly)

  Type: 

[`bpy_prop_collection`](bpy.types.bpy_prop_collection.html#bpy.types.bpy_prop_collection)[[`Key`](bpy.types.Key.html#bpy.types.Key)]

      sounds 

Sound data-blocks (default None, readonly)

  Type: 

[`BlendDataSounds`](bpy.types.BlendDataSounds.html#bpy.types.BlendDataSounds)[[`Sound`](bpy.types.Sound.html#bpy.types.Sound)]

      speakers 

Speaker data-blocks (default None, readonly)

  Type: 

[`BlendDataSpeakers`](bpy.types.BlendDataSpeakers.html#bpy.types.BlendDataSpeakers)[[`Speaker`](bpy.types.Speaker.html#bpy.types.Speaker)]

      texts 

Text data-blocks (default None, readonly)

  Type: 

[`BlendDataTexts`](bpy.types.BlendDataTexts.html#bpy.types.BlendDataTexts)[[`Text`](bpy.types.Text.html#bpy.types.Text)]

      textures 

Texture data-blocks (default None, readonly)

  Type: 

[`BlendDataTextures`](bpy.types.BlendDataTextures.html#bpy.types.BlendDataTextures)[[`Texture`](bpy.types.Texture.html#bpy.types.Texture)]

      use_autopack 

Automatically pack all external data into .blend file (default False)

  Type: 

bool

      version 

File format version the .blend file was saved with (array of 3 items, in [0, inf], default (0, 0, 0), readonly)

  Type: 

[`bpy_prop_array`](bpy.types.bpy_prop_array.html#bpy.types.bpy_prop_array)[int]

      volumes 

Volume data-blocks (default None, readonly)

  Type: 

[`BlendDataVolumes`](bpy.types.BlendDataVolumes.html#bpy.types.BlendDataVolumes)[[`Volume`](bpy.types.Volume.html#bpy.types.Volume)]

      window_managers 

Window manager data-blocks (default None, readonly)

  Type: 

[`BlendDataWindowManagers`](bpy.types.BlendDataWindowManagers.html#bpy.types.BlendDataWindowManagers)[[`WindowManager`](bpy.types.WindowManager.html#bpy.types.WindowManager)]

      workspaces 

Workspace data-blocks (default None, readonly)

  Type: 

[`BlendDataWorkSpaces`](bpy.types.BlendDataWorkSpaces.html#bpy.types.BlendDataWorkSpaces)[[`WorkSpace`](bpy.types.WorkSpace.html#bpy.types.WorkSpace)]

      worlds 

World data-blocks (default None, readonly)

  Type: 

[`BlendDataWorlds`](bpy.types.BlendDataWorlds.html#bpy.types.BlendDataWorlds)[[`World`](bpy.types.World.html#bpy.types.World)]

      pack_linked_ids_hierarchy(root_id) 

Pack the given linked ID and its dependencies into current blendfile

  Parameters: 

root_id ([`ID`](bpy.types.ID.html#bpy.types.ID) | None) – Root linked ID to pack

  Returns: 

The packed ID matching the given root ID

  Return type: 

[`ID`](bpy.types.ID.html#bpy.types.ID)

      batch_remove(ids) 

Remove (delete) several IDs at once.

 

Note that this function is quicker than individual calls to `remove()` (from `bpy.types.BlendData` ID collections), but less safe/versatile (it can break Blender, e.g. by removing all scenes…).

  Parameters: 

ids (Sequence[[`bpy.types.ID`](bpy.types.ID.html#bpy.types.ID)]) – Sequence of IDs (types can be mixed).

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

      file_path_foreach(visit_path_fn, *, subset=None, visit_types=None, flags={'SKIP_PACKED', 'SKIP_WEAK_REFERENCES'}) 

Call `visit_path_fn` for the file paths used by all ID data-blocks in current `bpy.data`.

 

For list of valid set members for visit_types, see: [`bpy.types.KeyingSetPath.id_type`](bpy.types.KeyingSetPath.html#bpy.types.KeyingSetPath.id_type).

  Parameters:  
- visit_path_fn (Callable[[[`bpy.types.ID`](bpy.types.ID.html#bpy.types.ID), str, [`bpy.types.BlendDataPathMeta`](bpy.types.BlendDataPathMeta.html#bpy.types.BlendDataPathMeta)], str|None]) – function that takes three parameters: the data-block, a file path, and a [`bpy.types.BlendDataPathMeta`](bpy.types.BlendDataPathMeta.html#bpy.types.BlendDataPathMeta) metadata object. The function should return either `None` or a `str`. In the latter case, the visited file path will be replaced with the returned string. 
- subset (set[str] | None) – When given, only these data-blocks and their used file paths will be visited. 
- visit_types (set[str] | None) – When given, only visit data-blocks of these types. Ignored if `subset` is also given. 
- flags (set[str]) – Set of flags that influence which data-blocks are visited. See [File Path Foreach Flag Items](bpy_types_enum_items/file_path_foreach_flag_items.html#rna-enum-file-path-foreach-flag-items).       file_path_map(*, subset=None, key_types=None, include_libraries=False) 

Returns a mapping of all ID data-blocks in current `bpy.data` to a set of all file paths used by them.

 

For list of valid set members for key_types, see: [`bpy.types.KeyingSetPath.id_type`](bpy.types.KeyingSetPath.html#bpy.types.KeyingSetPath.id_type).

  Parameters:  
- subset (Sequence[[`bpy.types.ID`](bpy.types.ID.html#bpy.types.ID)] | None) – When given, only these data-blocks and their used file paths will be included as keys/values in the map. 
- key_types (set[str] | None) – When given, filter the keys mapped by ID types. Ignored if `subset` is also given. 
- include_libraries (bool) – Include library file paths of linked data. False by default.   Returns: 

dictionary of [`bpy.types.ID`](bpy.types.ID.html#bpy.types.ID) instances, with sets of file path strings as their values.

  Return type: 

dict[[`bpy.types.ID`](bpy.types.ID.html#bpy.types.ID), set[str]]

      orphans_purge(do_local_ids=True, do_linked_ids=True, do_recursive=False) 

Remove (delete) all IDs with no user.

  Parameters:  
- do_local_ids (bool) – Include unused local IDs in the deletion, defaults to True 
- do_linked_ids (bool) – Include unused linked IDs in the deletion, defaults to True 
- do_recursive (bool) – Recursively check for unused IDs, ensuring no orphaned one remain after a single run of that function, defaults to False   Returns: 

The number of deleted IDs.

  Return type: 

int

      static temp_data(*, filepath=None) 

A context manager that temporarily creates blender file data.

  Parameters: 

filepath (str | bytes | None) – The file path for the newly temporary data. When None, the path of the currently open file is used.

  Returns: 

Blend file data which is freed once the context exits.

  Return type: 

`bpy.types.BlendData`

      user_map(*, subset=None, key_types=None, value_types=None) 

Returns a mapping of all ID data-blocks in current `bpy.data` to a set of all data-blocks using them.

 

For list of valid set members for key_types & value_types, see: [`bpy.types.KeyingSetPath.id_type`](bpy.types.KeyingSetPath.html#bpy.types.KeyingSetPath.id_type).

  Parameters:  
- subset (Sequence[[`bpy.types.ID`](bpy.types.ID.html#bpy.types.ID)] | None) – When passed, only these data-blocks and their users will be included as keys/values in the map. 
- key_types (set[str] | None) – Filter the keys mapped by ID types. 
- value_types (set[str] | None) – Filter the values in the set by ID types.   Returns: 

dictionary that maps data-blocks ID’s to their users.

  Return type: 

dict[[`bpy.types.ID`](bpy.types.ID.html#bpy.types.ID), set[[`bpy.types.ID`](bpy.types.ID.html#bpy.types.ID)]]

      

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

  
- [`Context.blend_data`](bpy.types.Context.html#bpy.types.Context.blend_data)   
- [`RenderEngine.update`](bpy.types.RenderEngine.html#bpy.types.RenderEngine.update)
