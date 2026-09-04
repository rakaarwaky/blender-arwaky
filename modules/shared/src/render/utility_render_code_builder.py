"""Render utility: Blender code builders.

Stateless technical functions that generate Blender Python code.
"""

from __future__ import annotations

from ..common.taxonomy_core_vo import PythonCode
from .taxonomy_render_vo import (
    CameraConfigVO,
    HdriConfigVO,
    RenderSceneVO,
    ViewportCaptureVO,
)


def build_viewport_capture_code(request: ViewportCaptureVO) -> PythonCode:
    """Build viewport capture code."""
    output_path = str(request.output_path)
    image_format = str(request.image_format).upper()

    lines = [
        "import bpy",
        "import json",
        "",
        f"output_path = {output_path!r}",
        f"image_format = {image_format!r}",
        "",
        "scene = bpy.context.scene",
        "scene.render.filepath = output_path",
        "scene.render.image_settings.file_format = image_format",
        "",
        "bpy.ops.render.render(write_still=True)",
        "",
        "result = {",
        "    'artifact_path': bpy.path.abspath(scene.render.filepath),",
        "    'width': int(scene.render.resolution_x),",
        "    'height': int(scene.render.resolution_y),",
        "    'format': image_format",
        "}",
        "",
        "print(json.dumps(result))",
    ]

    return PythonCode("\n".join(lines))


def build_scene_render_code(request: RenderSceneVO) -> PythonCode:
    """Build scene render code."""
    output_path = str(request.output_path)
    engine = str(request.render_engine).upper()
    resolution_x = int(request.resolution_x)
    resolution_y = int(request.resolution_y)
    samples = int(request.samples)
    use_denoising = bool(request.use_denoising)

    lines = [
        "import bpy",
        "import json",
        "import time",
        "",
        f"output_path = {output_path!r}",
        f"engine = {engine!r}",
        f"resolution_x = {resolution_x!r}",
        f"resolution_y = {resolution_y!r}",
        f"samples = {samples!r}",
        f"use_denoising = {use_denoising!r}",
        "",
        "scene = bpy.context.scene",
        "start_time = time.perf_counter()",
        "",
        "scene.render.filepath = output_path",
        "scene.render.resolution_x = resolution_x",
        "scene.render.resolution_y = resolution_y",
        "",
        "if engine == 'CYCLES':",
        "    scene.render.engine = 'CYCLES'",
        "    scene.cycles.samples = samples",
        "    scene.cycles.use_denoising = use_denoising",
        "elif engine == 'BLENDER_EEVEE':",
        "    scene.render.engine = 'BLENDER_EEVEE'",
        "    if hasattr(scene, 'eevee'):",
        "        scene.eevee.taa_render_samples = samples",
        "else:",
        "    scene.render.engine = 'CYCLES'",
        "    scene.cycles.samples = samples",
        "    scene.cycles.use_denoising = use_denoising",
        "",
        "bpy.ops.render.render(write_still=True)",
        "",
        "render_time = round(time.perf_counter() - start_time, 3)",
        "actual_engine = scene.render.engine",
        "denoising_applied = bool(use_denoising and actual_engine == 'CYCLES')",
        "",
        "result = {",
        "    'artifact_path': bpy.path.abspath(scene.render.filepath),",
        "    'width': int(scene.render.resolution_x),",
        "    'height': int(scene.render.resolution_y),",
        "    'render_time': render_time,",
        "    'engine_used': actual_engine,",
        "    'denoising_applied': denoising_applied",
        "}",
        "",
        "print(json.dumps(result))",
    ]

    return PythonCode("\n".join(lines))


def build_camera_config_code(request: CameraConfigVO) -> PythonCode:
    """Build camera configuration code."""
    camera_name = str(request.camera_ref or "Camera")
    focal_length = float(request.focal_length)
    sensor_fit = str(request.sensor_fit).upper()
    set_active = bool(request.set_active)
    create_if_missing = bool(request.create_if_missing)
    use_dof = bool(request.depth_of_field_enabled)
    focus_distance = float(request.focus_distance or 0.0)
    aperture = float(request.aperture)

    lines = [
        "import bpy",
        "import json",
        "",
        f"camera_name = {camera_name!r}",
        f"focal_length = {focal_length!r}",
        f"sensor_fit = {sensor_fit!r}",
        f"set_active = {set_active!r}",
        f"create_if_missing = {create_if_missing!r}",
        f"use_dof = {use_dof!r}",
        f"focus_distance = {focus_distance!r}",
        f"aperture = {aperture!r}",
        "",
        "scene = bpy.context.scene",
        "camera = bpy.data.objects.get(camera_name)",
        "",
        "if camera is None and create_if_missing:",
        "    bpy.ops.object.camera_add()",
        "    camera = bpy.context.active_object",
        "    camera.name = camera_name",
        "",
        "if camera is not None and camera.type == 'CAMERA':",
        "    camera.data.lens = focal_length",
        "    camera.data.sensor_fit = sensor_fit",
        "    camera.data.dof.use_dof = use_dof",
        "    if use_dof:",
        "        camera.data.dof.focus_distance = focus_distance",
        "        camera.data.dof.aperture_fstop = aperture",
        "    if set_active:",
        "        scene.camera = camera",
        "",
        "active_status = bool(camera is not None and scene.camera == camera)",
        "",
        "result = {",
        "    'camera_reference': camera.name if camera else '',",
        "    'final_focal_length': float(camera.data.lens) if camera and camera.type == 'CAMERA' else focal_length,",
        "    'active_status': active_status,",
        "    'depth_of_field_applied': bool(camera.data.dof.use_dof) if camera and camera.type == 'CAMERA' else False",
        "}",
        "",
        "print(json.dumps(result))",
    ]

    return PythonCode("\n".join(lines))


def build_hdri_config_code(request: HdriConfigVO) -> PythonCode:
    """Build HDRI configuration code."""
    hdri_path = str(request.hdri_path)
    strength = float(request.strength)
    rotation = float(request.rotation)
    background_visible = bool(request.background_visible)

    lines = [
        "import bpy",
        "import json",
        "",
        f"hdri_path = {hdri_path!r}",
        f"strength = {strength!r}",
        f"rotation = {rotation!r}",
        f"background_visible = {background_visible!r}",
        "",
        "scene = bpy.context.scene",
        "world = scene.world",
        "",
        "if world is None:",
        "    world = bpy.data.worlds.new('World')",
        "    scene.world = world",
        "",
        "world.use_nodes = True",
        "tree = world.node_tree",
        "nodes = tree.nodes",
        "links = tree.links",
        "",
        "output_node = nodes.get('World Output')",
        "if output_node is None:",
        "    output_node = nodes.new('ShaderNodeOutputWorld')",
        "    output_node.name = 'World Output'",
        "",
        "background_node = nodes.get('Background')",
        "if background_node is None:",
        "    background_node = nodes.new('ShaderNodeBackground')",
        "    background_node.name = 'Background'",
        "",
        "environment_node = nodes.get('Environment Texture')",
        "if environment_node is None:",
        "    environment_node = nodes.new('ShaderNodeTexEnvironment')",
        "    environment_node.name = 'Environment Texture'",
        "",
        "mapping_node = nodes.get('Mapping')",
        "if mapping_node is None:",
        "    mapping_node = nodes.new('ShaderNodeMapping')",
        "    mapping_node.name = 'Mapping'",
        "",
        "texcoord_node = nodes.get('Texture Coordinate')",
        "if texcoord_node is None:",
        "    texcoord_node = nodes.new('ShaderNodeTexCoord')",
        "    texcoord_node.name = 'Texture Coordinate'",
        "",
        "environment_node.image = bpy.data.images.load(hdri_path)",
        "mapping_node.inputs['Rotation'].default_value[2] = rotation",
        "background_node.inputs['Strength'].default_value = strength",
        "",
        "links.new(texcoord_node.outputs['Generated'], mapping_node.inputs['Vector'])",
        "links.new(mapping_node.outputs['Vector'], environment_node.inputs['Vector'])",
        "links.new(environment_node.outputs['Color'], background_node.inputs['Color'])",
        "links.new(background_node.outputs['Background'], output_node.inputs['Surface'])",
        "",
        "if hasattr(world, 'cycles_visibility'):",
        "    world.cycles_visibility.camera = background_visible",
        "",
        "result = {",
        "    'environment_ref': world.name,",
        "    'applied_strength': strength,",
        "    'applied_rotation': rotation",
        "}",
        "",
        "print(json.dumps(result))",
    ]

    return PythonCode("\n".join(lines))
