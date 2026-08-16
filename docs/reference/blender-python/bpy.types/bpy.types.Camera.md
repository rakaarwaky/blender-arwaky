# bpy.types.Camera

# Camera(ID)

 

base classes — [`bpy_struct`](bpy.types.bpy_struct.html#bpy.types.bpy_struct), [`ID`](bpy.types.ID.html#bpy.types.ID)

   class bpy.types.Camera(ID) 

Camera data-block for storing camera settings

   angle 

Camera lens field of view (in [0.00640536, 3.01675], default 0.69115)

  Type: 

float

      angle_x 

Camera lens horizontal field of view (in [0.00640536, 3.01675], default 0.0)

  Type: 

float

      angle_y 

Camera lens vertical field of view (in [0.00640536, 3.01675], default 0.0)

  Type: 

float

      animation_data 

Animation data for this data-block (readonly)

  Type: 

[`AnimData`](bpy.types.AnimData.html#bpy.types.AnimData) | None

      background_images 

List of background images (default None, readonly)

  Type: 

[`CameraBackgroundImages`](bpy.types.CameraBackgroundImages.html#bpy.types.CameraBackgroundImages)[[`CameraBackgroundImage`](bpy.types.CameraBackgroundImage.html#bpy.types.CameraBackgroundImage)]

      central_cylindrical_radius 

Radius of the virtual cylinder (in [1e-05, inf], default 1.0)

  Type: 

float

      central_cylindrical_range_u_max 

Maximum Longitude value for the central cylindrical lens (in [-inf, inf], default 3.14159)

  Type: 

float

      central_cylindrical_range_u_min 

Minimum Longitude value for the central cylindrical lens (in [-inf, inf], default -3.14159)

  Type: 

float

      central_cylindrical_range_v_max 

Maximum Height value for the central cylindrical lens (in [-inf, inf], default 1.0)

  Type: 

float

      central_cylindrical_range_v_min 

Minimum Height value for the central cylindrical lens (in [-inf, inf], default -1.0)

  Type: 

float

      clip_end 

Camera far clipping distance (in [1e-06, inf], default 1000.0)

  Type: 

float

      clip_start 

Camera near clipping distance (in [1e-06, inf], default 0.1)

  Type: 

float

      composition_guide_color 

Color and alpha for compositional guide overlays (array of 4 items, in [0, inf], default (0.5, 0.5, 0.5, 1.0))

  Type: 

[`bpy_prop_array`](bpy.types.bpy_prop_array.html#bpy.types.bpy_prop_array)[float]

      custom_bytecode 

Compiled bytecode of the custom shader (default “”, never None)

  Type: 

str

      custom_bytecode_hash 

Hash of the compiled bytecode of the custom shader, for quick equality checking (default “”, never None)

  Type: 

str

      custom_filepath 

Path to the shader defining the custom camera (default “”, never None)

  Type: 

str

      custom_mode 

(default `'INTERNAL'`)

  
- `INTERNAL` Internal – Use internal text data-block. 
- `EXTERNAL` External – Use external file.   Type: 

Literal[‘INTERNAL’, ‘EXTERNAL’]

      custom_shader 

Shader defining the custom camera

  Type: 

[`Text`](bpy.types.Text.html#bpy.types.Text) | None

      cycles_custom 

Parameters for custom (OSL-based) cameras (readonly)

  Type: 

`CyclesCustomCameraSettings` | None

      display_size 

Apparent size of the Camera object in the 3D View (in [0.01, 1000], default 1.0)

  Type: 

float

      dof 

(readonly)

  Type: 

[`CameraDOFSettings`](bpy.types.CameraDOFSettings.html#bpy.types.CameraDOFSettings) | None

      fisheye_fov 

Field of view for the fisheye lens (in [0.1745, 31.4159], default 3.14159)

  Type: 

float

      fisheye_lens 

Lens focal length (mm) (in [0.01, 100], default 10.5)

  Type: 

float

      fisheye_polynomial_k0 

Coefficient K0 of the lens polynomial (in [-inf, inf], default -1.17351e-05)

  Type: 

float

      fisheye_polynomial_k1 

Coefficient K1 of the lens polynomial (in [-inf, inf], default -0.0199887)

  Type: 

float

      fisheye_polynomial_k2 

Coefficient K2 of the lens polynomial (in [-inf, inf], default -3.3525e-06)

  Type: 

float

      fisheye_polynomial_k3 

Coefficient K3 of the lens polynomial (in [-inf, inf], default 3.0993e-06)

  Type: 

float

      fisheye_polynomial_k4 

Coefficient K4 of the lens polynomial (in [-inf, inf], default -2.61e-08)

  Type: 

float

      latitude_max 

Maximum latitude (vertical angle) for the equirectangular lens (in [-1.5708, 1.5708], default 1.5708)

  Type: 

float

      latitude_min 

Minimum latitude (vertical angle) for the equirectangular lens (in [-1.5708, 1.5708], default -1.5708)

  Type: 

float

      lens 

Perspective Camera focal length value in millimeters (in [1, inf], default 50.0)

  Type: 

float

      lens_unit 

Unit to edit lens in for the user interface (default `'MILLIMETERS'`)

  
- `MILLIMETERS` Millimeters – Specify focal length of the lens in millimeters. 
- `FOV` Field of View – Specify the lens as the field of view’s angle.   Type: 

Literal[‘MILLIMETERS’, ‘FOV’]

      longitude_max 

Maximum longitude (horizontal angle) for the equirectangular lens (in [-inf, inf], default 3.14159)

  Type: 

float

      longitude_min 

Minimum longitude (horizontal angle) for the equirectangular lens (in [-inf, inf], default -3.14159)

  Type: 

float

      ortho_scale 

Orthographic Camera scale (similar to zoom) (in [0, inf], default 6.0)

  Type: 

float

      panorama_type 

Distortion to use for the calculation (default `'FISHEYE_EQUISOLID'`)

  
- `EQUIRECTANGULAR` Equirectangular – Spherical camera for environment maps, also known as Lat Long panorama. 
- `EQUIANGULAR_CUBEMAP_FACE` Equiangular Cubemap Face – Single face of an equiangular cubemap. 
- `MIRRORBALL` Mirror Ball – Mirror ball mapping for environment maps. 
- `FISHEYE_EQUIDISTANT` Fisheye Equidistant – Ideal for fulldomes, ignore the sensor dimensions. 
- `FISHEYE_EQUISOLID` Fisheye Equisolid – Similar to most fisheye modern lens, takes sensor dimensions into consideration. 
- `FISHEYE_LENS_POLYNOMIAL` Fisheye Lens Polynomial – Defines the lens projection as polynomial to allow real world camera lenses to be mimicked. 
- `CENTRAL_CYLINDRICAL` Central Cylindrical – Projection onto a virtual cylinder from its center, similar as a rotating panoramic camera.   Type: 

Literal[‘EQUIRECTANGULAR’, ‘EQUIANGULAR_CUBEMAP_FACE’, ‘MIRRORBALL’, ‘FISHEYE_EQUIDISTANT’, ‘FISHEYE_EQUISOLID’, ‘FISHEYE_LENS_POLYNOMIAL’, ‘CENTRAL_CYLINDRICAL’]

      passepartout_alpha 

Opacity (alpha) of the darkened overlay in Camera view (in [0, 1], default 0.5)

  Type: 

float

      sensor_fit 

Method to fit image and field of view angle inside the sensor (default `'AUTO'`)

  
- `AUTO` Auto – Fit to the sensor width or height depending on image resolution. 
- `HORIZONTAL` Horizontal – Fit to the sensor width. 
- `VERTICAL` Vertical – Fit to the sensor height.   Type: 

Literal[‘AUTO’, ‘HORIZONTAL’, ‘VERTICAL’]

      sensor_height 

Vertical size of the image sensor area in millimeters (in [1, inf], default 24.0)

  Type: 

float

      sensor_width 

Horizontal size of the image sensor area in millimeters (in [1, inf], default 36.0)

  Type: 

float

      shift_x 

Camera horizontal shift (in [-inf, inf], default 0.0)

  Type: 

float

      shift_y 

Camera vertical shift (in [-inf, inf], default 0.0)

  Type: 

float

      show_background_images 

Display reference images behind objects in the 3D View (default False)

  Type: 

bool

      show_composition_center 

Display center composition guide inside the camera view (default False)

  Type: 

bool

      show_composition_center_diagonal 

Display diagonal center composition guide inside the camera view (default False)

  Type: 

bool

      show_composition_golden 

Display golden ratio composition guide inside the camera view (default False)

  Type: 

bool

      show_composition_golden_tria_a 

Display golden triangle A composition guide inside the camera view (default False)

  Type: 

bool

      show_composition_golden_tria_b 

Display golden triangle B composition guide inside the camera view (default False)

  Type: 

bool

      show_composition_harmony_tri_a 

Display harmony A composition guide inside the camera view (default False)

  Type: 

bool

      show_composition_harmony_tri_b 

Display harmony B composition guide inside the camera view (default False)

  Type: 

bool

      show_composition_thirds 

Display rule of thirds composition guide inside the camera view (default False)

  Type: 

bool

      show_limits 

Display the clipping range and focus point on the camera (default False)

  Type: 

bool

      show_mist 

Display a line from the Camera to indicate the mist area (default False)

  Type: 

bool

      show_name 

Show the active Camera’s name in Camera view (default False)

  Type: 

bool

      show_passepartout 

Show a darkened overlay outside the image area in Camera view (default True)

  Type: 

bool

      show_safe_areas 

Show TV title safe and action safe areas in Camera view (default False)

  Type: 

bool

      show_safe_center 

Show safe areas to fit content in a different aspect ratio (default False)

  Type: 

bool

      show_sensor 

Show sensor size (film gate) in Camera view (default False)

  Type: 

bool

      stereo 

(readonly, never None)

  Type: 

[`CameraStereoData`](bpy.types.CameraStereoData.html#bpy.types.CameraStereoData)

      type 

Camera types (default `'PERSP'`)

  Type: 

Literal[‘PERSP’, ‘ORTHO’, ‘PANO’, ‘CUSTOM’]

      view_frame(*, scene=None) 

Return 4 points for the cameras frame (before object transformation)

  Parameters: 

scene ([`Scene`](bpy.types.Scene.html#bpy.types.Scene) | None) – Scene to use for aspect calculation, when omitted 1:1 aspect is used (optional)

  Returns: 

`result_1`, Result, [`mathutils.Vector`](mathutils.html#mathutils.Vector)

 

`result_2`, Result, [`mathutils.Vector`](mathutils.html#mathutils.Vector)

 

`result_3`, Result, [`mathutils.Vector`](mathutils.html#mathutils.Vector)

 

`result_4`, Result, [`mathutils.Vector`](mathutils.html#mathutils.Vector)

  Return type: 

tuple[[`mathutils.Vector`](mathutils.html#mathutils.Vector), [`mathutils.Vector`](mathutils.html#mathutils.Vector), [`mathutils.Vector`](mathutils.html#mathutils.Vector), [`mathutils.Vector`](mathutils.html#mathutils.Vector)]

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

  
- `bpy.context.camera` 
- [`BlendData.cameras`](bpy.types.BlendData.html#bpy.types.BlendData.cameras) 
- [`BlendDataCameras.new`](bpy.types.BlendDataCameras.html#bpy.types.BlendDataCameras.new)   
- [`BlendDataCameras.remove`](bpy.types.BlendDataCameras.html#bpy.types.BlendDataCameras.remove) 
- [`RenderEngine.update_custom_camera`](bpy.types.RenderEngine.html#bpy.types.RenderEngine.update_custom_camera)
