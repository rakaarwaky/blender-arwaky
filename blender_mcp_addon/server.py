import contextlib
import hashlib
import io
import json
import logging
import math
import queue
import random
import socket
import struct
import threading
import time
from contextlib import redirect_stdout
from pathlib import Path

import bpy

from . import polyhaven, sketchfab, utils

logger = logging.getLogger(__name__)

# Max message size (10MB)
MAX_MESSAGE_SIZE = 10 * 1024 * 1024


class BlenderMCPServer:
    def __init__(self, host="localhost", port=9876):
        self.host = host
        self.port = port
        self.running = False
        self.socket = None
        self.server_thread = None
        self.command_queue = queue.Queue()
        self._timer_handle = None
        self._shutdown_lock = threading.Lock()
        self._shutdown_requested = False
        self._pending_responses = []  # Track pending res_q for shutdown signaling

    def start(self):
        if self.running:
            return
        self.running = True
        self._shutdown_requested = False
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.socket.bind((self.host, self.port))
            self.socket.listen(5)
            self.socket.settimeout(1.0)

            self.server_thread = threading.Thread(target=self._server_loop)
            self.server_thread.daemon = True
            self.server_thread.start()

            # Timer for processing commands in main thread (GUI mode)
            if not bpy.app.background:
                self._timer_handle = bpy.app.timers.register(self.process_commands, first_interval=0.1, persistent=True)

            logger.info("BlenderMCP server started on %s:%s", self.host, self.port)
        except Exception as e:
            logger.error("Failed to start server: %s", e)
            self.stop()

    def stop(self):
        with self._shutdown_lock:
            if self._shutdown_requested:
                return
            self._shutdown_requested = True
            self.running = False

        # Signal all pending response queues to unblock waiting threads
        for res_q in self._pending_responses:
            with contextlib.suppress(queue.Full):
                res_q.put_nowait(None)
        self._pending_responses.clear()

        if self.socket:
            try:
                self.socket.close()
            except Exception as e:
                logger.debug("Error closing socket: %s", e)
            self.socket = None

        if self._timer_handle:
            try:
                bpy.app.timers.unregister(self.process_commands)
            except Exception as e:
                logger.debug("Error unregistering timer: %s", e)
            self._timer_handle = None

        # Clear queue
        while not self.command_queue.empty():
            try:
                self.command_queue.get_nowait()
            except queue.Empty:
                break

        if self.server_thread:
            self.server_thread.join(timeout=2.0)
            self.server_thread = None
        logger.info("BlenderMCP server stopped")

    def _server_loop(self):
        while self.running:
            try:
                client, addr = self.socket.accept()
                t = threading.Thread(target=self._handle_client, args=(client,))
                t.daemon = True
                t.start()
            except TimeoutError:
                continue
            except Exception as e:
                if self.running:
                    logger.error("Server accept error: %s", e)
                time.sleep(0.1)

    def _handle_client(self, client):
        """Handle a single client connection with length-prefixed message framing."""
        client.settimeout(30.0)
        try:
            while self.running:
                try:
                    # Read 4-byte length header
                    header = b""
                    while len(header) < 4:
                        chunk = client.recv(4 - len(header))
                        if not chunk:
                            return
                        header += chunk

                    msg_len = struct.unpack("!I", header)[0]
                    if msg_len > MAX_MESSAGE_SIZE:
                        logger.warning("Message too large: %d bytes", msg_len)
                        return

                    # Read message body
                    body = b""
                    while len(body) < msg_len:
                        chunk = client.recv(min(8192, msg_len - len(body)))
                        if not chunk:
                            return
                        body += chunk

                    command = json.loads(body.decode("utf-8"))

                    res_q = queue.Queue()
                    self._pending_responses.append(res_q)
                    try:
                        self.command_queue.put((command, client, res_q))
                        try:
                            res_q.get(timeout=30.0)
                        except queue.Empty:
                            logger.warning("Command %s timed out", command.get("type"))
                            self._send_response(client, {"status": "error", "message": "Command timed out"})
                    finally:
                        with contextlib.suppress(ValueError):
                            self._pending_responses.remove(res_q)

                except TimeoutError:
                    continue
                except (ConnectionError, BrokenPipeError, OSError) as e:
                    logger.error("Client connection error: %s", e)
                    break
                except (json.JSONDecodeError, UnicodeDecodeError) as e:
                    logger.warning("Invalid message: %s", e)
                    continue
        finally:
            with contextlib.suppress(Exception):
                client.close()

    def _send_response(self, client, response):
        """Send a length-prefixed JSON response."""
        try:
            data = json.dumps(response).encode("utf-8")
            header = struct.pack("!I", len(data))
            client.sendall(header + data)
        except Exception as e:
            logger.debug("Error sending response: %s", e)

    def process_commands(self):
        if self._shutdown_requested:
            return 0.1

        while not self.command_queue.empty():
            try:
                cmd, client, res_q = self.command_queue.get_nowait()
                try:
                    if self._shutdown_requested:
                        break
                    response = self.execute_command(cmd)
                    self._send_response(client, response)
                except Exception as e:
                    logger.exception("Exec error: %s", e)
                    self._send_response(client, {"status": "error", "message": str(e)})
                finally:
                    res_q.put(True)
            except queue.Empty:
                break
        return 0.1

    def execute_command(self, command):
        cmd_type = command.get("type")
        params = command.get("params", {})

        # Dispatch table (removed hunyuan/hyper3d handlers)
        handlers = {
            "get_scene_info": self.get_scene_info,
            "cleanup_scene": self.cleanup_scene,
            "list_scene_objects": self.list_scene_objects,
            "get_object_hierarchy": self.get_object_hierarchy,
            "undo": self.undo,
            "redo": self.redo,
            "setup_environment": self.setup_environment,
            "configure_camera": self.configure_camera,
            "get_object_info": self.get_object_info,
            "place_asset": self.place_asset,
            "create_primitive": self.create_primitive,
            "set_object_transform": self.set_object_transform,
            "delete_object": self.delete_object,
            "set_material": self.set_material,
            "create_material": self.create_material,
            "set_material_properties": self.set_material_properties,
            "set_material_texture": self.set_material_texture,
            "apply_modifier": self.apply_modifier,
            "import_glb": self.import_glb,
            "import_asset": self.import_asset,
            "export_model": self.export_model,
            "get_viewport_screenshot": utils.get_viewport_screenshot,
            "render": self.render,
            "set_render_settings": self.set_render_settings,
            "inspect_geometry_node_group": self.inspect_geometry_node_group,
            "create_geometry_node_group": self.create_geometry_node_group,
            "set_geometry_node_link": self.set_geometry_node_link,
            "set_geometry_node_modifier": self.set_geometry_node_modifier,
            "get_animation_state": self.get_animation_state,
            "insert_object_keyframe": self.insert_object_keyframe,
            "set_timeline_range": self.set_timeline_range,
            "list_object_keyframes": self.list_object_keyframes,
            "get_mesh_statistics": self.get_mesh_statistics,
            "validate_mesh": self.validate_mesh,
            "perform_mesh_edit_operation": self.perform_mesh_edit_operation,
            "ensure_mesh_uv_layer": self.ensure_mesh_uv_layer,
            "inspect_compositor_nodes": self.inspect_compositor_nodes,
            "configure_compositor": self.configure_compositor,
            "create_compositor_node": self.create_compositor_node,
            "set_compositor_link": self.set_compositor_link,
            "inspect_sequence_editor": self.inspect_sequence_editor,
            "create_sequence_strip": self.create_sequence_strip,
            "create_character": self.create_character,
            "randomize_character": self.randomize_character,
            "remove_character": self.remove_character,
            "install_mpfb_asset_pack": self.install_mpfb_asset_pack,
            "inspect_mpfb_assets": self.inspect_mpfb_assets,
            "remove_sequence_strip": self.remove_sequence_strip,
            "render_sequence": self.render_sequence,
            "get_physics_state": self.get_physics_state,
            "configure_rigid_body": self.configure_rigid_body,
            "configure_cloth_simulation": self.configure_cloth_simulation,
            "bake_physics_simulation": self.bake_physics_simulation,
            "clear_physics_bake": self.clear_physics_bake,
            "get_simulation_state": self.get_simulation_state,
            "get_simulation_cache_status": self.get_simulation_cache_status,
            "configure_particle_system": self.configure_particle_system,
            "configure_force_field": self.configure_force_field,
            "configure_fluid_domain": self.configure_fluid_domain,
            "inspect_armature": self.inspect_armature,
            "set_pose_bone_transform": self.set_pose_bone_transform,
            "configure_bone_constraint": self.configure_bone_constraint,
            "configure_shape_key": self.configure_shape_key,
            "get_deformation_state": self.get_deformation_state,
            "bind_character_to_rig": self.bind_character_to_rig,
            "create_rigify_metarig": self.create_rigify_metarig,
            "execute_blender_code": self.execute_blender_code,
            "get_polyhaven_categories": polyhaven.get_polyhaven_categories,
            "search_polyhaven_assets": polyhaven.search_polyhaven_assets,
            "download_polyhaven_asset": polyhaven.download_polyhaven_asset,
            "set_texture": polyhaven.set_texture,
            "cleanup_polyhaven": polyhaven.cleanup_polyhaven,
            "get_polyhaven_status": polyhaven.get_polyhaven_status,
            "get_polyhaven_asset_details": polyhaven.get_polyhaven_asset_details,
            "get_sketchfab_status": sketchfab.get_sketchfab_status,
            "get_telemetry_consent": self.get_telemetry_consent,
            "search_sketchfab_models": sketchfab.search_sketchfab_models,
            "get_sketchfab_model_preview": sketchfab.get_sketchfab_model_preview,
            "download_sketchfab_model": sketchfab.download_sketchfab_model,
        }

        handler = handlers.get(cmd_type)
        if not handler:
            return {"status": "error", "message": f"Unknown command: {cmd_type}"}

        try:
            result = handler(**params)
            return {"status": "success", "result": result}
        except Exception as e:
            logger.exception("Command execution failed: %s", command.get("type"))
            return {"status": "error", "message": str(e)}

    def get_scene_info(self):
        scene = bpy.context.scene
        total_objects = len(scene.objects)
        return {
            "name": scene.name,
            "objects": [{"name": o.name, "type": o.type} for o in scene.objects[:50]],
            "total_count": total_objects,
            "truncated": total_objects > 50,
        }

    def cleanup_scene(self, mode):
        """Remove scene content according to the validated cleanup mode."""
        if mode not in {"all", "objects", "meshes"}:
            raise ValueError(f"Unsupported cleanup mode: {mode}")
        if mode in {"all", "objects"}:
            bpy.ops.object.select_all(action="SELECT")
            bpy.ops.object.delete(use_global=False)
        else:
            for obj in list(bpy.data.objects):
                if obj.type == "MESH":
                    bpy.data.objects.remove(obj, do_unlink=True)
        return {"mode": mode, "removed": True}

    def list_scene_objects(self, include_hidden=False, object_type=None, limit=100):
        """List bounded structured object summaries from the active scene."""
        limit = int(limit)
        if not 1 <= limit <= 1000:
            raise ValueError("limit must be between 1 and 1000")
        requested_type = str(object_type).upper() if object_type else None
        objects = []
        for obj in bpy.context.scene.objects:
            if not include_hidden and obj.hide_get():
                continue
            if requested_type and obj.type != requested_type:
                continue
            objects.append(
                {
                    "name": obj.name,
                    "type": obj.type,
                    "parent": obj.parent.name if obj.parent else None,
                    "collections": [collection.name for collection in obj.users_collection],
                    "visible": not obj.hide_get(),
                    "location": list(obj.location),
                }
            )
            if len(objects) >= limit:
                break
        total_matching = sum(
            1
            for obj in bpy.context.scene.objects
            if (include_hidden or not obj.hide_get()) and (not requested_type or obj.type == requested_type)
        )
        return {
            "objects": objects,
            "count": len(objects),
            "total_matching": total_matching,
            "truncated": total_matching > len(objects),
            "include_hidden": bool(include_hidden),
            "object_type": requested_type,
        }

    def get_object_hierarchy(self, object_name=None, include_hidden=False, max_depth=32):
        """Return a bounded parent-child hierarchy for one object or scene roots."""
        max_depth = int(max_depth)
        if not 1 <= max_depth <= 64:
            raise ValueError("max_depth must be between 1 and 64")

        def visible(obj):
            return bool(include_hidden) or not obj.hide_get()

        def node(obj, depth):
            item = {"name": obj.name, "type": obj.type, "children": []}
            if depth >= max_depth:
                item["truncated"] = bool(obj.children)
                return item
            for child in sorted(obj.children, key=lambda value: value.name):
                if visible(child):
                    item["children"].append(node(child, depth + 1))
            return item

        if object_name:
            root = bpy.data.objects.get(str(object_name))
            if root is None:
                raise ValueError(f"Object not found: {object_name}")
            roots = [root] if visible(root) else []
        else:
            roots = sorted(
                [obj for obj in bpy.context.scene.objects if obj.parent is None and visible(obj)],
                key=lambda value: value.name,
            )
        return {
            "roots": [node(root, 0) for root in roots],
            "root_count": len(roots),
            "object_name": str(object_name) if object_name else None,
            "include_hidden": bool(include_hidden),
            "max_depth": max_depth,
        }

    def undo(self):
        """Undo the most recent Blender edit operation."""
        try:
            result = bpy.ops.ed.undo()
        except RuntimeError as error:
            if not bpy.app.background:
                raise
            try:
                bpy.ops.ed.undo_push(message="Blender Arwaky")
                result = bpy.ops.ed.undo()
            except RuntimeError as background_error:
                return {
                    "operation": "undo",
                    "status": "unavailable",
                    "reason": "background_context",
                    "message": str(background_error or error),
                }
        return {"operation": "undo", "status": "finished" if "FINISHED" in result else str(result)}

    def redo(self):
        """Redo the most recently undone Blender edit operation."""
        try:
            result = bpy.ops.ed.redo()
        except RuntimeError as error:
            if not bpy.app.background:
                raise
            return {
                "operation": "redo",
                "status": "unavailable",
                "reason": "background_context",
                "message": str(error),
            }
        return {"operation": "redo", "status": "finished" if "FINISHED" in result else str(result)}

    def setup_environment(self, hdri_id, strength=1.0):
        """Configure a local HDRI file as the active World environment.

        ``hdri_id`` is a local, already-available asset reference. Asset
        acquisition remains owned by the Asset feature; this handler only
        applies the resolved file in Blender.
        """
        hdri_path = Path(str(hdri_id)).expanduser()
        if not hdri_path.is_file():
            raise FileNotFoundError(f"HDRI asset not found: {hdri_id}")
        if hdri_path.suffix.lower() not in {".hdr", ".exr"}:
            raise ValueError("HDRI asset must use .hdr or .exr format")
        strength = float(strength)
        if not math.isfinite(strength) or not 0.0 <= strength <= 10.0:
            raise ValueError("HDRI strength must be between 0 and 10")

        scene = bpy.context.scene
        world = scene.world or bpy.data.worlds.new(name="World")
        scene.world = world
        world.use_nodes = True
        nodes = world.node_tree.nodes
        links = world.node_tree.links
        nodes.clear()
        output = nodes.new("ShaderNodeOutputWorld")
        background = nodes.new("ShaderNodeBackground")
        environment = nodes.new("ShaderNodeTexEnvironment")
        environment.image = bpy.data.images.load(str(hdri_path.resolve()), check_existing=True)
        background.inputs["Strength"].default_value = strength
        links.new(environment.outputs["Color"], background.inputs["Color"])
        links.new(background.outputs["Background"], output.inputs["Surface"])
        return {
            "hdri_id": str(hdri_path.resolve()),
            "environment_ref": world.name,
            "strength": strength,
        }

    def configure_camera(
        self,
        camera_ref=None,
        focal_length=50.0,
        sensor_fit="AUTO",
        framing_target=None,
        set_active=False,
        depth_of_field_enabled=False,
        focus_distance=None,
        focus_object=None,
        aperture=2.8,
        create_if_missing=True,
    ):
        """Configure a real Blender camera according to FR-RND-003."""
        focal_length = float(focal_length)
        aperture = float(aperture)
        if not math.isfinite(focal_length) or not 1.0 <= focal_length <= 500.0:
            raise ValueError("focal_length must be between 1 and 500")
        if sensor_fit not in {"AUTO", "HORIZONTAL", "VERTICAL"}:
            raise ValueError(f"Unsupported sensor_fit: {sensor_fit}")
        if not math.isfinite(aperture) or aperture <= 0.0:
            raise ValueError("aperture must be a positive finite number")

        scene = bpy.context.scene
        camera = bpy.data.objects.get(str(camera_ref)) if camera_ref else scene.camera
        if camera is None:
            if not create_if_missing:
                raise ValueError("Camera not found and create_if_missing is false")
            camera_data = bpy.data.cameras.new("Camera")
            camera = bpy.data.objects.new("Camera", camera_data)
            scene.collection.objects.link(camera)
        if camera.type != "CAMERA":
            raise ValueError(f"Object is not a camera: {camera.name}")

        camera.data.lens = focal_length
        camera.data.sensor_fit = sensor_fit
        camera.data.dof.use_dof = bool(depth_of_field_enabled)
        camera.data.dof.aperture_fstop = aperture

        if focus_distance is not None:
            focus_distance = float(focus_distance)
            if not math.isfinite(focus_distance) or focus_distance <= 0.0:
                raise ValueError("focus_distance must be positive and finite")
            camera.data.dof.focus_distance = focus_distance

        if focus_object:
            target = bpy.data.objects.get(str(focus_object))
            if target is None:
                raise ValueError(f"Focus object not found: {focus_object}")
            camera.data.dof.focus_object = target

        if framing_target:
            target = bpy.data.objects.get(str(framing_target))
            if target is None:
                raise ValueError(f"Framing target not found: {framing_target}")
            direction = target.location - camera.location
            if direction.length == 0:
                raise ValueError("Framing target must not share the camera location")
            camera.rotation_euler = direction.to_track_quat("-Z", "Y").to_euler()

        if set_active:
            scene.camera = camera

        return {
            "camera_ref": camera.name,
            "focal_length": camera.data.lens,
            "sensor_fit": camera.data.sensor_fit,
            "active": scene.camera == camera,
            "depth_of_field_enabled": camera.data.dof.use_dof,
            "focus_distance": camera.data.dof.focus_distance,
            "focus_object": camera.data.dof.focus_object.name if camera.data.dof.focus_object else None,
            "aperture": camera.data.dof.aperture_fstop,
        }

    def place_asset(self, asset_id, location=None, rotation=None, scale=None):
        """Place an existing scene object identified by an exact asset reference."""
        obj = bpy.data.objects.get(str(asset_id))
        if obj is None:
            raise ValueError(f"Asset object not found: {asset_id}")
        if location is not None:
            if len(location) != 3 or not all(math.isfinite(float(value)) for value in location):
                raise ValueError("location must contain three finite numbers")
            obj.location = tuple(float(value) for value in location)
        if rotation is not None:
            if len(rotation) != 3 or not all(math.isfinite(float(value)) for value in rotation):
                raise ValueError("rotation must contain three finite degree values")
            obj.rotation_euler = tuple(math.radians(float(value)) for value in rotation)
        if scale is not None:
            if len(scale) != 3 or not all(math.isfinite(float(value)) and float(value) != 0.0 for value in scale):
                raise ValueError("scale must contain three finite non-zero numbers")
            obj.scale = tuple(float(value) for value in scale)
        return {
            "asset_id": str(asset_id),
            "object_name": obj.name,
            "location": list(obj.location),
            "rotation": list(obj.rotation_euler),
            "scale": list(obj.scale),
        }

    def get_object_info(self, object_name):
        obj = bpy.data.objects.get(object_name)
        if not obj:
            return {"error": "Not found"}
        return {
            "name": obj.name,
            "type": obj.type,
            "location": list(obj.location),
            "rotation": list(obj.rotation_euler),
            "scale": list(obj.scale),
            "modifiers": [modifier.name for modifier in obj.modifiers],
            "materials": [slot.material.name for slot in obj.material_slots if slot.material],
        }

    def create_primitive(self, primitive_type, location=None, scale=None, name=None):
        """Create a primitive mesh through Blender's public operators."""
        operation = getattr(bpy.ops.mesh, f"primitive_{str(primitive_type).lower()}_add", None)
        if operation is None:
            raise ValueError(f"Unsupported primitive type: {primitive_type}")
        operation(location=tuple(location or (0, 0, 0)))
        obj = bpy.context.object
        if obj is None:
            raise RuntimeError("Blender did not create an active object")
        if scale is not None:
            obj.scale = tuple(scale)
        if name:
            obj.name = name
        return {"name": obj.name, "type": obj.type, "location": list(obj.location), "scale": list(obj.scale)}

    def set_object_transform(self, object_name, location=None, rotation=None, scale=None):
        """Update object transform; rotation input is expressed in degrees."""
        obj = bpy.data.objects.get(object_name)
        if obj is None:
            raise ValueError(f"Object not found: {object_name}")
        if location is not None:
            obj.location = tuple(location)
        if rotation is not None:
            import math

            obj.rotation_euler = tuple(math.radians(value) for value in rotation)
        if scale is not None:
            obj.scale = tuple(scale)
        return {
            "name": obj.name,
            "location": list(obj.location),
            "rotation": list(obj.rotation_euler),
            "scale": list(obj.scale),
        }

    def delete_object(self, object_name):
        """Delete a named object from the current scene."""
        obj = bpy.data.objects.get(object_name)
        if obj is None:
            raise ValueError(f"Object not found: {object_name}")
        bpy.data.objects.remove(obj, do_unlink=True)
        return {"name": object_name, "deleted": True}

    def set_material(self, object_name, material_name):
        """Assign an existing or newly-created material to an object."""
        obj = bpy.data.objects.get(object_name)
        if obj is None:
            raise ValueError(f"Object not found: {object_name}")
        material = bpy.data.materials.get(material_name) or bpy.data.materials.new(material_name)
        if (
            obj.data
            and hasattr(obj.data, "materials")
            and material.name not in [item.name for item in obj.data.materials if item]
        ):
            obj.data.materials.append(material)
        return {"object_name": object_name, "material_name": material.name}

    @staticmethod
    def _validate_rgba(base_color):
        """Validate and normalize an RGB/RGBA color in Blender's 0-1 range."""
        if base_color is None:
            return None
        values = [float(value) for value in base_color]
        if len(values) == 3:
            values.append(1.0)
        if len(values) != 4 or not all(math.isfinite(value) and 0.0 <= value <= 1.0 for value in values):
            raise ValueError("base_color must contain 3 or 4 finite channels in the range 0-1")
        return values

    @staticmethod
    def _principled_material(material):
        material.use_nodes = True
        node = material.node_tree.nodes.get("Principled BSDF")
        if node is None:
            raise RuntimeError(f"Material has no Principled BSDF node: {material.name}")
        return node

    def create_material(
        self,
        material_name,
        base_color=None,
        metallic=0.0,
        roughness=0.5,
        reuse_existing=True,
    ):
        """Create or reuse a bounded Principled BSDF material."""
        name = str(material_name).strip()
        if not name:
            raise ValueError("material_name is required")
        metallic = float(metallic)
        roughness = float(roughness)
        if not 0.0 <= metallic <= 1.0 or not math.isfinite(metallic):
            raise ValueError("metallic must be between 0 and 1")
        if not 0.0 <= roughness <= 1.0 or not math.isfinite(roughness):
            raise ValueError("roughness must be between 0 and 1")
        color = self._validate_rgba(base_color if base_color is not None else [0.8, 0.8, 0.8, 1.0])
        material = bpy.data.materials.get(name)
        created = material is None
        if material is not None and not reuse_existing:
            raise ValueError(f"Material already exists: {name}")
        if material is None:
            material = bpy.data.materials.new(name=name)
        node = self._principled_material(material)
        node.inputs["Base Color"].default_value = color
        node.inputs["Metallic"].default_value = metallic
        node.inputs["Roughness"].default_value = roughness
        return {
            "material_name": material.name,
            "created": created,
            "base_color": list(node.inputs["Base Color"].default_value),
            "metallic": float(node.inputs["Metallic"].default_value),
            "roughness": float(node.inputs["Roughness"].default_value),
        }

    def set_material_properties(self, material_name, base_color=None, metallic=None, roughness=None):
        """Update supplied Principled BSDF properties without changing omitted values."""
        material = bpy.data.materials.get(str(material_name))
        if material is None:
            raise ValueError(f"Material not found: {material_name}")
        node = self._principled_material(material)
        if base_color is not None:
            node.inputs["Base Color"].default_value = self._validate_rgba(base_color)
        for key, raw_value in (("Metallic", metallic), ("Roughness", roughness)):
            if raw_value is not None:
                value = float(raw_value)
                if not math.isfinite(value) or not 0.0 <= value <= 1.0:
                    raise ValueError(f"{key.lower()} must be between 0 and 1")
                node.inputs[key].default_value = value
        return {
            "material_name": material.name,
            "base_color": list(node.inputs["Base Color"].default_value),
            "metallic": float(node.inputs["Metallic"].default_value),
            "roughness": float(node.inputs["Roughness"].default_value),
        }

    def set_material_texture(self, material_name, file_path):
        """Attach a local image texture to a material's base color input."""
        material = bpy.data.materials.get(str(material_name))
        if material is None:
            raise ValueError(f"Material not found: {material_name}")
        path = Path(str(file_path)).expanduser()
        if not path.is_file():
            raise FileNotFoundError(f"Texture file not found: {file_path}")
        node = self._principled_material(material)
        image = bpy.data.images.load(str(path.resolve()), check_existing=True)
        texture = material.node_tree.nodes.new("ShaderNodeTexImage")
        texture.image = image
        material.node_tree.links.new(texture.outputs["Color"], node.inputs["Base Color"])
        return {
            "material_name": material.name,
            "file_path": str(path.resolve()),
            "texture_node": texture.name,
        }

    def apply_modifier(self, object_name, modifier_name):
        """Apply a named modifier to an object."""
        obj = bpy.data.objects.get(object_name)
        if obj is None:
            raise ValueError(f"Object not found: {object_name}")
        modifier = obj.modifiers.get(modifier_name)
        if modifier is None:
            raise ValueError(f"Modifier not found: {modifier_name}")
        bpy.context.view_layer.objects.active = obj
        obj.select_set(True)
        bpy.ops.object.modifier_apply(modifier=modifier_name)
        return {"object_name": object_name, "modifier_name": modifier_name, "applied": True}

    def import_asset(
        self,
        file_path,
        asset_type="model",
        target_collection=None,
        scale_normalization=False,
        duplicate_policy="rename",
        format_hint=None,
    ):
        """Import a cached asset and return canonical Blender object references."""
        path = Path(str(file_path)).expanduser()
        if not path.is_file():
            raise FileNotFoundError(f"Asset file not found: {file_path}")
        before = {obj.name for obj in bpy.context.scene.objects}
        suffix = (format_hint or path.suffix).lower().lstrip(".")
        if suffix in {"glb", "gltf"}:
            bpy.ops.import_scene.gltf(filepath=str(path))
        elif suffix == "obj":
            bpy.ops.wm.obj_import(filepath=str(path))
        elif suffix == "fbx":
            bpy.ops.import_scene.fbx(filepath=str(path))
        else:
            raise ValueError(f"Unsupported asset import format: {suffix or asset_type}")
        imported = [obj for obj in bpy.context.scene.objects if obj.name not in before]
        if target_collection:
            collection = bpy.data.collections.get(str(target_collection)) or bpy.data.collections.new(
                str(target_collection)
            )
            if collection.name not in [item.name for item in bpy.context.scene.collection.children]:
                bpy.context.scene.collection.children.link(collection)
            for obj in imported:
                for old_collection in list(obj.users_collection):
                    old_collection.objects.unlink(obj)
                collection.objects.link(obj)
        if scale_normalization:
            for obj in imported:
                obj.scale = (1.0, 1.0, 1.0)
        if duplicate_policy == "reject" and any(obj.name in before for obj in imported):
            raise ValueError("Duplicate asset import rejected")
        return {
            "file_path": str(path),
            "asset_type": str(asset_type),
            "objects": [obj.name for obj in imported],
            "collection": target_collection,
            "duplicate_policy": duplicate_policy,
        }

    def import_glb(self, file_path, object_name=None):
        """Import a GLB/GLTF file and return imported object names."""
        before = {obj.name for obj in bpy.context.scene.objects}
        bpy.ops.import_scene.gltf(filepath=file_path)
        imported = [obj for obj in bpy.context.scene.objects if obj.name not in before]
        if object_name and imported:
            imported[0].name = object_name
        return {"file_path": file_path, "objects": [obj.name for obj in imported]}

    def export_model(self, object_name, file_path, export_format="glb"):
        """Export one selected object using Blender's supported exporter."""
        obj = bpy.data.objects.get(object_name)
        if obj is None:
            raise ValueError(f"Object not found: {object_name}")
        bpy.ops.object.select_all(action="DESELECT")
        obj.select_set(True)
        bpy.context.view_layer.objects.active = obj
        if export_format == "glb":
            bpy.ops.export_scene.gltf(filepath=file_path, export_format="GLB", use_selection=True)
        elif export_format == "fbx":
            bpy.ops.export_scene.fbx(filepath=file_path, use_selection=True)
        elif export_format == "obj":
            bpy.ops.wm.obj_export(filepath=file_path, export_selected_objects=True)
        else:
            raise ValueError(f"Unsupported export format: {export_format}")
        return {"object_name": object_name, "file_path": file_path, "export_format": export_format}

    def render(self, output_path, resolution_x=1920, resolution_y=1080):
        """Render the active scene to an image file and return its metadata."""
        scene = bpy.context.scene
        previous_resolution = (scene.render.resolution_x, scene.render.resolution_y, scene.render.resolution_percentage)
        previous_filepath = scene.render.filepath
        try:
            scene.render.resolution_x = int(resolution_x)
            scene.render.resolution_y = int(resolution_y)
            scene.render.resolution_percentage = 100
            scene.render.filepath = output_path
            bpy.ops.render.render(write_still=True)
            return {
                "filepath": output_path,
                "width": scene.render.resolution_x,
                "height": scene.render.resolution_y,
            }
        finally:
            scene.render.resolution_x, scene.render.resolution_y, scene.render.resolution_percentage = (
                previous_resolution
            )
            scene.render.filepath = previous_filepath

    def set_render_settings(
        self,
        engine=None,
        resolution_x=1920,
        resolution_y=1080,
        resolution_percentage=100,
        samples=None,
        use_transparent=None,
    ):
        """Apply bounded scene render settings and return the effective values."""
        scene = bpy.context.scene
        resolution_x = int(resolution_x)
        resolution_y = int(resolution_y)
        resolution_percentage = int(resolution_percentage)
        if not 1 <= resolution_x <= 16384 or not 1 <= resolution_y <= 16384:
            raise ValueError("resolution dimensions must be between 1 and 16384")
        if not 1 <= resolution_percentage <= 100:
            raise ValueError("resolution_percentage must be between 1 and 100")
        if engine:
            engine = str(engine).upper()
            valid_engines = {item.identifier for item in scene.render.bl_rna.properties["engine"].enum_items}
            if engine not in valid_engines:
                raise ValueError(f"Unsupported render engine: {engine}")
            scene.render.engine = engine
        scene.render.resolution_x = resolution_x
        scene.render.resolution_y = resolution_y
        scene.render.resolution_percentage = resolution_percentage
        if samples is not None:
            samples = int(samples)
            if not 1 <= samples <= 65536:
                raise ValueError("samples must be between 1 and 65536")
            if hasattr(scene, "cycles"):
                scene.cycles.samples = samples
            eevee = getattr(scene, "eevee", None)
            if eevee is not None and hasattr(eevee, "taa_render_samples"):
                eevee.taa_render_samples = samples
        if use_transparent is not None:
            scene.render.film_transparent = bool(use_transparent)
        result = {
            "engine": scene.render.engine,
            "resolution_x": scene.render.resolution_x,
            "resolution_y": scene.render.resolution_y,
            "resolution_percentage": scene.render.resolution_percentage,
            "use_transparent": scene.render.film_transparent,
        }
        if hasattr(scene, "cycles"):
            result["cycles_samples"] = scene.cycles.samples
        return result

    def inspect_armature(self, object_name, limit=100):
        """Inspect a bounded armature hierarchy and pose summary."""
        limit = self._bounded_wave_three_limit(limit)
        obj = bpy.data.objects.get(str(object_name))
        if obj is None:
            raise ValueError(f"Armature object not found: {object_name}")
        if obj.type != "ARMATURE":
            raise ValueError("inspect_armature requires an armature object")
        bones = []
        for bone in list(obj.data.bones)[:limit]:
            pose_bone = obj.pose.bones.get(bone.name)
            bones.append(
                {
                    "name": bone.name,
                    "parent": bone.parent.name if bone.parent else None,
                    "children": [child.name for child in list(bone.children)[:64]],
                    "use_deform": bone.use_deform,
                    "head": list(bone.head_local),
                    "tail": list(bone.tail_local),
                    "pose_location": list(pose_bone.location) if pose_bone else [0.0, 0.0, 0.0],
                    "pose_rotation": list(pose_bone.rotation_euler) if pose_bone else [0.0, 0.0, 0.0],
                    "pose_scale": list(pose_bone.scale) if pose_bone else [1.0, 1.0, 1.0],
                }
            )
        return {"object_name": obj.name, "bone_count": len(obj.data.bones), "bones": bones}

    def set_pose_bone_transform(self, armature_name, bone_name, location=None, rotation_euler=None, scale=None):
        """Set one bounded pose-bone transform."""
        location = self._bounded_wave_five_vector(location, "location", -100000.0, 100000.0)
        rotation_euler = self._bounded_wave_five_vector(
            rotation_euler, "rotation_euler", -math.tau * 1000.0, math.tau * 1000.0
        )
        scale = self._bounded_wave_five_vector(scale, "scale", -1000.0, 1000.0)
        if location is None and rotation_euler is None and scale is None:
            raise ValueError("at least one pose transform vector is required")
        obj = bpy.data.objects.get(str(armature_name))
        if obj is None:
            raise ValueError(f"Armature object not found: {armature_name}")
        if obj.type != "ARMATURE":
            raise ValueError("set_pose_bone_transform requires an armature object")
        pose_bone = obj.pose.bones.get(str(bone_name))
        if pose_bone is None:
            raise ValueError(f"Pose bone not found: {bone_name}")
        changed = False
        if location is not None:
            changed = changed or list(pose_bone.location) != location
            pose_bone.location = location
        if rotation_euler is not None:
            pose_bone.rotation_mode = "XYZ"
            changed = changed or list(pose_bone.rotation_euler) != rotation_euler
            pose_bone.rotation_euler = rotation_euler
        if scale is not None:
            changed = changed or list(pose_bone.scale) != scale
            pose_bone.scale = scale
        return {
            "object_name": obj.name,
            "changed": changed,
            "operation": "set_pose_bone_transform",
            "bone_name": pose_bone.name,
        }

    def configure_bone_constraint(
        self,
        armature_name,
        bone_name,
        constraint_type,
        enabled,
        constraint_name=None,
        target_object=None,
        subtarget=None,
    ):
        """Create, update, or remove one allow-listed pose-bone constraint."""
        constraint_type = str(constraint_type).upper()
        if constraint_type not in {"COPY_LOCATION", "COPY_ROTATION", "LIMIT_LOCATION", "LIMIT_ROTATION"}:
            raise ValueError(f"Unsupported bone constraint type: {constraint_type}")
        name = str(constraint_name or f"Arwaky_{constraint_type}").strip()
        if not name or len(name) > 128:
            raise ValueError("constraint_name must be 1-128 characters")
        if subtarget is not None and len(str(subtarget)) > 128:
            raise ValueError("subtarget must not exceed 128 characters")
        obj = bpy.data.objects.get(str(armature_name))
        if obj is None:
            raise ValueError(f"Armature object not found: {armature_name}")
        if obj.type != "ARMATURE":
            raise ValueError("configure_bone_constraint requires an armature object")
        pose_bone = obj.pose.bones.get(str(bone_name))
        if pose_bone is None:
            raise ValueError(f"Pose bone not found: {bone_name}")
        constraint = pose_bone.constraints.get(name)
        if not bool(enabled):
            if constraint is None:
                return {
                    "object_name": obj.name,
                    "changed": False,
                    "operation": "configure_bone_constraint",
                    "bone_name": pose_bone.name,
                    "constraint_name": name,
                }
            pose_bone.constraints.remove(constraint)
            return {
                "object_name": obj.name,
                "changed": True,
                "operation": "configure_bone_constraint",
                "bone_name": pose_bone.name,
                "constraint_name": name,
            }
        if constraint is not None and constraint.type != constraint_type:
            pose_bone.constraints.remove(constraint)
            constraint = None
        if constraint is None:
            constraint = pose_bone.constraints.new(type=constraint_type)
            constraint.name = name
        if target_object:
            target = bpy.data.objects.get(str(target_object))
            if target is None:
                raise ValueError(f"Constraint target object not found: {target_object}")
            if hasattr(constraint, "target"):
                constraint.target = target
        if subtarget is not None and hasattr(constraint, "subtarget"):
            constraint.subtarget = str(subtarget)
        return {
            "object_name": obj.name,
            "changed": True,
            "operation": "configure_bone_constraint",
            "bone_name": pose_bone.name,
            "constraint_name": constraint.name,
        }

    def configure_shape_key(
        self,
        object_name,
        shape_key_name,
        enabled,
        value=0.0,
        slider_min=0.0,
        slider_max=1.0,
    ):
        """Create, update, or remove one bounded mesh shape key."""
        name = str(shape_key_name).strip()
        if not name or len(name) > 128:
            raise ValueError("shape_key_name must be 1-128 characters")
        value = self._bounded_wave_five_scalar(value, "value", -10.0, 10.0)
        slider_min = self._bounded_wave_five_scalar(slider_min, "slider_min", -10.0, 10.0)
        slider_max = self._bounded_wave_five_scalar(slider_max, "slider_max", -10.0, 10.0)
        if slider_min > slider_max:
            raise ValueError("slider_min must be less than or equal to slider_max")
        if not slider_min <= value <= slider_max:
            raise ValueError("value must be within slider limits")
        obj = bpy.data.objects.get(str(object_name))
        if obj is None:
            raise ValueError(f"Object not found: {object_name}")
        if obj.type != "MESH":
            raise ValueError("configure_shape_key requires a mesh object")
        key = obj.data.shape_keys.key_blocks.get(name) if obj.data.shape_keys else None
        if bool(enabled):
            if key is None:
                key = obj.shape_key_add(name=name)
            key.value = value
            key.slider_min = slider_min
            key.slider_max = slider_max
            return {
                "object_name": obj.name,
                "changed": True,
                "operation": "configure_shape_key",
                "shape_key_name": key.name,
            }
        if key is None:
            raise ValueError(f"Shape key not found: {name}")
        if key.name == "Basis":
            raise ValueError("Basis shape key cannot be removed")
        obj.shape_key_remove(key)
        return {
            "object_name": obj.name,
            "changed": True,
            "operation": "configure_shape_key",
            "shape_key_name": name,
        }

    def get_deformation_state(self, object_name):
        """Inspect bounded armature modifiers, constraints, and shape keys."""
        obj = bpy.data.objects.get(str(object_name))
        if obj is None:
            raise ValueError(f"Object not found: {object_name}")
        if obj.type != "MESH":
            raise ValueError("get_deformation_state requires a mesh object")
        armature_modifiers = []
        constraints = []
        for modifier in list(obj.modifiers)[:64]:
            if modifier.type != "ARMATURE":
                continue
            armature_modifiers.append(
                {"name": modifier.name, "object_name": modifier.object.name if modifier.object else None}
            )
            armature = modifier.object
            if armature and armature.type == "ARMATURE":
                for pose_bone in list(armature.pose.bones)[:1000]:
                    for constraint in list(pose_bone.constraints)[:32]:
                        constraints.append(
                            {
                                "bone_name": pose_bone.name,
                                "name": constraint.name,
                                "type": constraint.type,
                                "target_object": constraint.target.name if constraint.target else None,
                                "subtarget": getattr(constraint, "subtarget", ""),
                            }
                        )
        for constraint in list(obj.constraints)[:64]:
            constraints.append(
                {
                    "bone_name": None,
                    "name": constraint.name,
                    "type": constraint.type,
                    "target_object": constraint.target.name if constraint.target else None,
                    "subtarget": getattr(constraint, "subtarget", ""),
                }
            )
        shape_keys = []
        if obj.data.shape_keys:
            for key in list(obj.data.shape_keys.key_blocks)[:128]:
                shape_keys.append(
                    {"name": key.name, "value": key.value, "slider_min": key.slider_min, "slider_max": key.slider_max}
                )
        return {
            "object_name": obj.name,
            "armature_modifiers": armature_modifiers,
            "constraints": constraints[:128],
            "shape_keys": shape_keys,
        }

    def create_rigify_metarig(
        self,
        character_object_name,
        armature_name=None,
        preset="human",
        bind_character=True,
        replace_existing=False,
    ):
        """Run the native MPFB2 Rigify definition, weights, and generation workflow."""
        character_name = str(character_object_name).strip()
        requested_armature_name = str(armature_name).strip() if armature_name else ""
        preset_name = str(preset).casefold().strip()
        if not character_name or len(character_name) > 128 or any(ord(char) < 32 for char in character_name):
            raise ValueError("character_object_name must contain 1-128 printable characters")
        if requested_armature_name and (
            len(requested_armature_name) > 128 or any(ord(char) < 32 for char in requested_armature_name)
        ):
            raise ValueError("armature_name must contain 1-128 printable characters")
        if preset_name != "human":
            raise ValueError("preset must be human")
        if not isinstance(bind_character, bool):
            raise ValueError("bind_character must be boolean")
        if not isinstance(replace_existing, bool):
            raise ValueError("replace_existing must be boolean")
        character = bpy.data.objects.get(character_name)
        if character is None:
            raise ValueError(f"Character object not found: {character_name}")
        if character.type != "MESH":
            raise ValueError("create_rigify_metarig requires a mesh character object")

        from bl_ext.user_default.mpfb.services.humanservice import HumanService
        from bl_ext.user_default.mpfb.services.objectservice import ObjectService
        from bl_ext.user_default.mpfb.services.rigservice import RigService

        native_rig_name = "rigify.human_toes"
        existing_generated = next(
            (
                obj
                for obj in bpy.data.objects
                if obj.type == "ARMATURE"
                and ObjectService.object_is_generated_rigify_rig(obj)
                and obj.name == (requested_armature_name or f"{character.name}_Rigify_Control")
            ),
            None,
        )
        if existing_generated is not None:
            final_rig = existing_generated
            meta_rig = ObjectService.find_rigify_metarig_by_rig(final_rig)
            created = False
            native_loaded = True
        else:
            meta_rig = ObjectService.find_object_of_type_amongst_nearest_relatives(character, "Skeleton")
            if meta_rig is None or RigService.identify_rig(meta_rig) != native_rig_name:
                meta_rig = HumanService.add_builtin_rig(character, native_rig_name, import_weights=True)
            if meta_rig is None or meta_rig.type != "ARMATURE":
                raise RuntimeError("Native MPFB2 Rigify metarig creation failed")
            if RigService.identify_rig(meta_rig) != native_rig_name:
                raise RuntimeError("MPFB2 returned an invalid Rigify metarig")
            final_name = requested_armature_name or f"{character.name}_Rigify_Control"
            final_rig = RigService.generate_rigify_rig(meta_rig, name=final_name, meta_rig_action="hide")
            if final_rig is None or final_rig.type != "ARMATURE":
                raise RuntimeError("Native MPFB2 Rigify final generation failed")
            created = True
            native_loaded = True

        binding = None
        if bind_character:
            binding = self.bind_character_to_rig(
                character_object_name=character.name,
                armature_name=final_rig.name,
                modifier_name=f"{final_rig.name}_Armature",
                replace_existing=replace_existing,
            )
        modifiers = [modifier for modifier in character.modifiers if modifier.type == "ARMATURE"]
        return {
            "character_object_name": character.name,
            "armature_name": final_rig.name,
            "metarig_name": meta_rig.name if meta_rig else None,
            "preset": preset_name,
            "native_rig": native_rig_name,
            "native_loaded": native_loaded,
            "created": created,
            "metarig_bone_count": len(meta_rig.data.bones) if meta_rig else 0,
            "bone_count": len(final_rig.data.bones),
            "deform_bone_count": len([bone for bone in final_rig.data.bones if bone.use_deform]),
            "bound": bool(binding),
            "modifier_name": binding.get("modifier_name") if binding else None,
            "armature_modifiers": [modifier.name for modifier in modifiers],
            "operation": "create_rigify_metarig",
        }

    def bind_character_to_rig(
        self,
        character_object_name,
        armature_name,
        modifier_name="Rigify_Armature",
        replace_existing=False,
    ):
        """Bind one character mesh to an existing armature modifier."""
        character_name = str(character_object_name).strip()
        rig_name = str(armature_name).strip()
        modifier_label = str(modifier_name).strip() or "Rigify_Armature"
        if not character_name or len(character_name) > 128 or any(ord(char) < 32 for char in character_name):
            raise ValueError("character_object_name must contain 1-128 printable characters")
        if not rig_name or len(rig_name) > 128 or any(ord(char) < 32 for char in rig_name):
            raise ValueError("armature_name must contain 1-128 printable characters")
        if len(modifier_label) > 128 or any(ord(char) < 32 for char in modifier_label):
            raise ValueError("modifier_name must contain at most 128 printable characters")
        if not isinstance(replace_existing, bool):
            raise ValueError("replace_existing must be boolean")
        character = bpy.data.objects.get(character_name)
        if character is None:
            raise ValueError(f"Character object not found: {character_name}")
        if character.type != "MESH":
            raise ValueError("bind_character_to_rig requires a mesh character object")
        armature = bpy.data.objects.get(rig_name)
        if armature is None:
            raise ValueError(f"Armature object not found: {rig_name}")
        if armature.type != "ARMATURE":
            raise ValueError("bind_character_to_rig requires an armature object")
        existing = [modifier for modifier in character.modifiers if modifier.type == "ARMATURE"]
        matching = next((modifier for modifier in existing if modifier.object is armature), None)
        if matching is not None and not replace_existing:
            return {
                "object_name": character.name,
                "armature_name": armature.name,
                "modifier_name": matching.name,
                "changed": False,
                "replaced_count": 0,
                "operation": "bind_character_to_rig",
            }
        if existing and not replace_existing:
            raise ValueError("character already has an armature modifier; set replace_existing=true to replace it")
        for modifier in existing:
            character.modifiers.remove(modifier)
        modifier = character.modifiers.new(name=modifier_label, type="ARMATURE")
        modifier.object = armature
        modifier.use_deform_preserve_volume = False
        return {
            "object_name": character.name,
            "armature_name": armature.name,
            "modifier_name": modifier.name,
            "changed": True,
            "replaced_count": len(existing),
            "operation": "bind_character_to_rig",
        }

    @staticmethod
    def _bounded_wave_five_scalar(value, name, lower, upper):
        scalar = float(value)
        if not math.isfinite(scalar) or not lower <= scalar <= upper:
            raise ValueError(f"{name} must be between {lower} and {upper}")
        return scalar

    @classmethod
    def _bounded_wave_five_vector(cls, value, name, lower, upper):
        if value is None:
            return None
        if len(value) != 3:
            raise ValueError(f"{name} must contain exactly 3 numbers")
        return [cls._bounded_wave_five_scalar(item, name, lower, upper) for item in value]

    @staticmethod
    def _bounded_wave_three_limit(value):
        limit = int(value)
        if not 1 <= limit <= 1000:
            raise ValueError("limit must be between 1 and 1000")
        return limit

    @staticmethod
    def _bounded_wave_three_frame(value):
        frame = int(value)
        if not -100000 <= frame <= 100000:
            raise ValueError("frame must be between -100000 and 100000")
        return frame

    @staticmethod
    def _bounded_wave_three_channel(value):
        channel = int(value)
        if not 1 <= channel <= 128:
            raise ValueError("channel must be between 1 and 128")
        return channel

    @staticmethod
    def _validated_wave_three_output_path(value):
        path = Path(str(value)).expanduser()
        if not str(path).strip() or path.name in {"", ".", ".."}:
            raise ValueError("output_path must be a file path")
        if path.exists() and path.is_dir():
            raise ValueError("output_path must be a file path")
        return path.resolve()

    @staticmethod
    def _sequence_collection(scene, create=False):
        editor = scene.sequence_editor_create() if create else scene.sequence_editor
        if editor is None:
            return None
        strips = getattr(editor, "strips", None)
        if strips is None:
            strips = getattr(editor, "sequences", None)
        return strips

    def inspect_compositor_nodes(self, limit=100):
        """Inspect a bounded compositor graph for the active scene."""
        limit = self._bounded_wave_three_limit(limit)
        scene = bpy.context.scene
        nodes = []
        links = []
        node_tree = scene.node_tree if scene.use_nodes and scene.node_tree else None
        if node_tree:
            for node in list(node_tree.nodes)[:limit]:
                nodes.append(
                    {
                        "name": node.name,
                        "node_type": node.bl_idname,
                        "inputs": [socket.name for socket in list(node.inputs)[:128]],
                        "outputs": [socket.name for socket in list(node.outputs)[:128]],
                    }
                )
            for link in list(node_tree.links)[:limit]:
                links.append(
                    {
                        "from_node": link.from_node.name,
                        "from_socket": link.from_socket.name,
                        "to_node": link.to_node.name,
                        "to_socket": link.to_socket.name,
                    }
                )
        return {"use_nodes": bool(scene.use_nodes), "nodes": nodes, "links": links}

    def configure_compositor(self, use_nodes):
        """Enable or disable compositor node usage."""
        scene = bpy.context.scene
        use_nodes = bool(use_nodes)
        changed = scene.use_nodes != use_nodes
        scene.use_nodes = use_nodes
        return {"changed": changed, "use_nodes": bool(scene.use_nodes)}

    def create_compositor_node(self, node_type, node_name=None):
        """Create one allow-listed compositor node."""
        allowed = {
            "CompositorNodeRGB",
            "CompositorNodeMixRGB",
            "CompositorNodeBlur",
            "CompositorNodeComposite",
            "CompositorNodeViewer",
        }
        node_type = str(node_type)
        if node_type not in allowed:
            raise ValueError(f"Unsupported compositor node type: {node_type}")
        scene = bpy.context.scene
        scene.use_nodes = True
        node = scene.node_tree.nodes.new(node_type)
        if node_name:
            name = str(node_name).strip()
            if not name or len(name) > 128:
                raise ValueError("node_name must be 1-128 characters")
            node.name = name
        return {"changed": True, "node_name": node.name, "node_type": node.bl_idname, "use_nodes": True}

    def set_compositor_link(self, from_node, from_socket, to_node, to_socket):
        """Create one validated compositor socket link."""
        scene = bpy.context.scene
        if not scene.use_nodes or scene.node_tree is None:
            raise ValueError("Compositor nodes are disabled")
        source = scene.node_tree.nodes.get(str(from_node))
        target = scene.node_tree.nodes.get(str(to_node))
        if source is None or target is None:
            raise ValueError("Compositor source or target node not found")
        source_socket = source.outputs.get(str(from_socket))
        target_socket = target.inputs.get(str(to_socket))
        if source_socket is None or target_socket is None:
            raise ValueError("Compositor source or target socket not found")
        for link in scene.node_tree.links:
            if link.from_socket == source_socket and link.to_socket == target_socket:
                return {"changed": False, "message": "Link already exists"}
        scene.node_tree.links.new(source_socket, target_socket)
        return {"changed": True, "message": "Link created"}

    def inspect_sequence_editor(self, limit=100):
        """Inspect bounded VSE strip state."""
        limit = self._bounded_wave_three_limit(limit)
        scene = bpy.context.scene
        strips = self._sequence_collection(scene)
        values = []
        if strips is not None:
            for strip in list(strips)[:limit]:
                values.append(
                    {
                        "name": strip.name,
                        "strip_type": strip.type,
                        "channel": strip.channel,
                        "frame_start": strip.frame_final_start,
                        "frame_final": strip.frame_final_end,
                        "filepath": getattr(strip, "filepath", None),
                    }
                )
        return {"sequence_present": strips is not None, "strips": values}

    def create_character(self, plugin_id="mpfb2", name="MPFB_Human"):
        """Create one MPFB2 human through the explicitly mapped public operator."""
        if str(plugin_id).strip() != "mpfb2":
            raise ValueError("create_character is mapped only to provider mpfb2")
        character_name = str(name).strip() or "MPFB_Human"
        if len(character_name) > 64 or any(char in character_name for char in "\r\n\x00"):
            raise ValueError("character name must be 1-64 characters without control characters")
        try:
            from bl_ext.user_default.mpfb.services.humanservice import HumanService
        except ImportError as error:
            raise RuntimeError("MPFB2 is not installed or enabled in Blender") from error
        objects_before = set(bpy.data.objects)
        character = HumanService.create_human()
        if character is None:
            active = bpy.context.view_layer.objects.active
            character = active if active not in objects_before else None
        if character is None:
            raise RuntimeError("MPFB2 create_human completed without a new character")
        if character_name not in bpy.data.objects or bpy.data.objects.get(character_name) is character:
            character.name = character_name
        return {
            "changed": True,
            "plugin_id": "mpfb2",
            "operation": "character.create",
            "object_name": character.name,
            "blender_version": bpy.app.version_string,
        }

    def randomize_character(self, plugin_id="mpfb2", name="MPFB_RandomHuman", seed=0):
        """Create one deterministic MPFB2 random human through the public operator."""
        if str(plugin_id).strip() != "mpfb2":
            raise ValueError("randomize_character is mapped only to provider mpfb2")
        character_name = str(name).strip() or "MPFB_RandomHuman"
        if len(character_name) > 64 or any(ord(char) < 32 for char in character_name):
            raise ValueError("character name must be 1-64 characters without control characters")
        if isinstance(seed, bool) or not isinstance(seed, int) or seed < 0:
            raise ValueError("seed must be an integer greater than or equal to zero")
        objects_before = set(bpy.data.objects)
        try:
            from bl_ext.user_default.mpfb.services.humanservice import HumanService
            from bl_ext.user_default.mpfb.services.randomizationservice import RandomizationService
        except ImportError as error:
            raise RuntimeError("MPFB2 is not installed or enabled in Blender") from error
        randomization_spec = RandomizationService.get_default_phenotype_spec()
        macro_detail_dict = RandomizationService.randomize_macro_info_dict(
            randomization_spec,
            random.Random(seed),
        )
        basemesh = HumanService.create_human(macro_detail_dict=macro_detail_dict)
        active = bpy.context.view_layer.objects.active
        character = basemesh or (active if active not in objects_before else None)
        if character is None:
            raise RuntimeError("MPFB2 randomization completed without a new character")
        if character_name not in bpy.data.objects or bpy.data.objects.get(character_name) is character:
            character.name = character_name
        return {
            "changed": True,
            "plugin_id": "mpfb2",
            "operation": "character.randomize",
            "object_name": character.name,
            "seed": seed,
            "blender_version": bpy.app.version_string,
        }

    def remove_character(self, plugin_id="mpfb2", object_name="", confirm=False):
        """Remove one verified MPFB2 basemesh root closure without touching unrelated objects."""
        if str(plugin_id).strip() != "mpfb2":
            raise ValueError("remove_character is mapped only to provider mpfb2")
        if confirm is not True:
            raise ValueError("remove_character requires confirm=true")
        target_name = str(object_name).strip()
        if not target_name or len(target_name) > 128 or any(ord(char) < 32 for char in target_name):
            raise ValueError("object_name must be 1-128 characters without control characters")
        target = bpy.data.objects.get(target_name)
        if target is None:
            raise ValueError(f"MPFB2 character object not found: {target_name}")
        if target.type != "MESH":
            raise ValueError("remove_character target must be an MPFB2 basemesh")
        if not hasattr(target, "MPFB_HUM_gender") or getattr(target, "MPFB_GEN_object_type", None) not in {
            None,
            "Basemesh",
        }:
            raise ValueError("target is not a verified MPFB2 basemesh")
        root = target
        visited = set()
        while root.parent is not None and root.name not in visited:
            visited.add(root.name)
            root = root.parent
        closure = {root, target, *root.children_recursive}
        removed_names = sorted(obj.name for obj in closure)
        for obj in closure:
            bpy.data.objects.remove(obj, do_unlink=True)
        return {
            "changed": True,
            "plugin_id": "mpfb2",
            "operation": "character.remove",
            "removed_objects": removed_names,
            "blender_version": bpy.app.version_string,
        }

    def install_mpfb_asset_pack(
        self,
        plugin_id="mpfb2",
        asset_pack_id="makehuman_system_assets",
        cache_path="",
        sha256="",
    ):
        """Install one verified MPFB2 asset pack through the public AssetService API."""
        if str(plugin_id).strip() != "mpfb2":
            raise ValueError("install_mpfb_asset_pack is mapped only to provider mpfb2")
        pack_id = str(asset_pack_id).strip()
        if pack_id != "makehuman_system_assets":
            raise ValueError("only the official makehuman_system_assets pack is currently mapped")
        archive_path = Path(str(cache_path)).expanduser()
        if not archive_path.is_absolute() or not archive_path.is_file():
            raise ValueError("cache_path must be an existing absolute asset pack archive")
        expected = str(sha256).lower().strip()
        if len(expected) != 64 or any(character not in "0123456789abcdef" for character in expected):
            raise ValueError("sha256 must be a 64-character hexadecimal digest")
        digest = hashlib.sha256(archive_path.read_bytes()).hexdigest()
        if digest != expected:
            raise ValueError("asset pack checksum mismatch")
        try:
            from bl_ext.user_default.mpfb.services.assetservice import AssetService
            from bl_ext.user_default.mpfb.services.locationservice import LocationService
        except ImportError as error:
            raise RuntimeError("MPFB2 is not installed or enabled in Blender") from error
        archive_error = AssetService.check_asset_pack_zip(str(archive_path))
        if archive_error not in {None, "MACOS", "STRUCTURE"}:
            raise ValueError(f"invalid MPFB2 asset pack: {archive_error}")
        user_data = Path(LocationService.get_user_data()).expanduser()
        if not user_data.is_absolute():
            raise RuntimeError("MPFB2 user data path must be absolute")
        user_data.mkdir(parents=True, exist_ok=True)
        extraction_error = AssetService.fix_and_extract_asset_pack_zip(str(archive_path), str(user_data))
        if extraction_error:
            raise RuntimeError(f"MPFB2 asset pack installation failed: {extraction_error}")
        AssetService.rescan_pack_metadata()
        if not AssetService.system_assets_pack_is_installed():
            raise RuntimeError("MPFB2 asset pack installed but system pack metadata was not detected")
        return {
            "changed": True,
            "plugin_id": "mpfb2",
            "operation": "asset_pack.install",
            "asset_pack_id": pack_id,
            "user_data_path": str(user_data.resolve()),
            "pack_names": sorted(AssetService.get_pack_names()),
            "blender_version": bpy.app.version_string,
        }

    def inspect_mpfb_assets(self, plugin_id="mpfb2"):
        """Inspect MPFB2 asset pack metadata and minimum system pack readiness."""
        if str(plugin_id).strip() != "mpfb2":
            raise ValueError("inspect_mpfb_assets is mapped only to provider mpfb2")
        try:
            from bl_ext.user_default.mpfb.services.assetservice import AssetService
            from bl_ext.user_default.mpfb.services.locationservice import LocationService
        except ImportError as error:
            raise RuntimeError("MPFB2 is not installed or enabled in Blender") from error
        pack_names = sorted(AssetService.get_pack_names())
        asset_counts = {
            name: len(AssetService.get_asset_names_in_pack(name)) for name in pack_names
        }
        return {
            "plugin_id": "mpfb2",
            "operation": "asset_pack.inspect",
            "system_assets_installed": AssetService.system_assets_pack_is_installed(),
            "pack_names": pack_names,
            "asset_counts": asset_counts,
            "user_data_path": str(Path(LocationService.get_user_data()).expanduser().resolve()),
            "blender_version": bpy.app.version_string,
        }

    def create_sequence_strip(
        self,
        strip_type,
        strip_name,
        filepath=None,
        channel=1,
        frame_start=1,
        frame_end=None,
    ):
        """Create a bounded VSE strip from explicit media types."""
        strip_type = str(strip_type).upper()
        if strip_type not in {"COLOR", "IMAGE", "MOVIE", "SOUND"}:
            raise ValueError(f"Unsupported sequence strip type: {strip_type}")
        name = str(strip_name).strip()
        if not name or len(name) > 128:
            raise ValueError("strip_name must be 1-128 characters")
        channel = self._bounded_wave_three_channel(channel)
        start = self._bounded_wave_three_frame(frame_start)
        end = start + 1 if frame_end is None else self._bounded_wave_three_frame(frame_end)
        if end <= start:
            raise ValueError("frame_end must be greater than frame_start")
        if strip_type != "COLOR":
            if not filepath:
                raise ValueError("filepath is required for media strips")
            media_path = Path(str(filepath)).expanduser()
            if not media_path.is_file():
                raise FileNotFoundError(str(filepath))
            filepath = str(media_path.resolve())
        strips = self._sequence_collection(bpy.context.scene, create=True)
        if strips is None:
            raise RuntimeError("Blender sequence editor collection is unavailable")
        if strip_type == "COLOR":
            strip = strips.new_effect(name=name, type="COLOR", channel=channel, frame_start=start, frame_end=end)
        elif strip_type == "IMAGE":
            strip = strips.new_image(name=name, filepath=filepath, channel=channel, frame_start=start)
            strip.frame_final_end = end
        elif strip_type == "MOVIE":
            strip = strips.new_movie(name=name, filepath=filepath, channel=channel, frame_start=start)
        else:
            strip = strips.new_sound(name=name, filepath=filepath, channel=channel, frame_start=start)
        return {"changed": True, "strip_name": strip.name, "strip_type": strip.type}

    def remove_sequence_strip(self, strip_name):
        """Remove one exact VSE strip."""
        name = str(strip_name).strip()
        if not name:
            raise ValueError("strip_name is required")
        strips = self._sequence_collection(bpy.context.scene)
        if strips is None:
            raise ValueError("Sequence editor is not initialized")
        strip = strips.get(name)
        if strip is None:
            raise ValueError(f"Sequence strip not found: {name}")
        strips.remove(strip)
        return {"changed": True, "strip_name": name}

    def render_sequence(self, output_path, frame_start=None, frame_end=None):
        """Render a bounded sequence range using Blender's real render operator."""
        path = self._validated_wave_three_output_path(output_path)
        start = None if frame_start is None else self._bounded_wave_three_frame(frame_start)
        end = None if frame_end is None else self._bounded_wave_three_frame(frame_end)
        if start is not None and end is not None and end < start:
            raise ValueError("frame_end must be greater than or equal to frame_start")
        scene = bpy.context.scene
        previous = (scene.frame_start, scene.frame_end, scene.render.filepath)
        try:
            if start is not None:
                scene.frame_start = start
            if end is not None:
                scene.frame_end = end
            scene.render.filepath = str(path)
            bpy.ops.render.render(animation=True, write_still=True)
            return {
                "changed": True,
                "output_path": str(path),
                "frame_start": scene.frame_start,
                "frame_end": scene.frame_end,
            }
        finally:
            scene.frame_start, scene.frame_end, scene.render.filepath = previous

    def get_physics_state(self, object_name):
        """Inspect rigid body and cloth state for one object."""
        obj = bpy.data.objects.get(str(object_name))
        if obj is None:
            raise ValueError(f"Object not found: {object_name}")
        rigid = obj.rigid_body
        cloth = next((item for item in obj.modifiers if item.type == "CLOTH"), None)
        settings = cloth.settings if cloth else None
        return {
            "object_name": obj.name,
            "rigid_body_enabled": rigid is not None,
            "rigid_body_type": rigid.type if rigid else None,
            "rigid_body_mass": rigid.mass if rigid else None,
            "rigid_body_kinematic": rigid.kinematic if rigid else None,
            "cloth_enabled": cloth is not None,
            "cloth_quality": settings.quality if settings else None,
            "cloth_pin_group": settings.vertex_group_mass if settings else None,
        }

    def configure_rigid_body(self, object_name, enabled, body_type="ACTIVE", mass=1.0, kinematic=False):
        """Configure or remove a bounded rigid body component."""
        obj = bpy.data.objects.get(str(object_name))
        if obj is None:
            raise ValueError(f"Object not found: {object_name}")
        body_type = str(body_type).upper()
        if body_type not in {"ACTIVE", "PASSIVE"}:
            raise ValueError(f"Unsupported rigid body type: {body_type}")
        mass = float(mass)
        if not 0.001 <= mass <= 1.0e6 or not math.isfinite(mass):
            raise ValueError("mass must be between 0.001 and 1000000")
        changed = False
        if bool(enabled):
            bpy.ops.object.select_all(action="DESELECT")
            obj.select_set(True)
            bpy.context.view_layer.objects.active = obj
            if obj.rigid_body is None:
                bpy.ops.rigidbody.object_add()
                changed = True
            rigid = obj.rigid_body
            if rigid.type != body_type or rigid.mass != mass or rigid.kinematic != bool(kinematic):
                changed = True
            rigid.type = body_type
            rigid.mass = mass
            rigid.kinematic = bool(kinematic)
        elif obj.rigid_body is not None:
            bpy.ops.object.select_all(action="DESELECT")
            obj.select_set(True)
            bpy.context.view_layer.objects.active = obj
            bpy.ops.rigidbody.object_remove()
            changed = True
        return {
            "object_name": obj.name,
            "changed": changed,
            "operation": "configure_rigid_body",
            "body_type": body_type if bool(enabled) else None,
            "mass": mass if bool(enabled) else None,
        }

    def configure_cloth_simulation(self, object_name, enabled, quality=5, pin_group=None):
        """Configure or remove a bounded cloth modifier."""
        obj = bpy.data.objects.get(str(object_name))
        if obj is None:
            raise ValueError(f"Object not found: {object_name}")
        quality = int(quality)
        if not 1 <= quality <= 80:
            raise ValueError("quality must be between 1 and 80")
        if pin_group is not None and len(str(pin_group)) > 64:
            raise ValueError("pin_group must not exceed 64 characters")
        cloth = next((item for item in obj.modifiers if item.type == "CLOTH"), None)
        changed = False
        if bool(enabled):
            if cloth is None:
                cloth = obj.modifiers.new(name="Cloth", type="CLOTH")
                changed = True
            cloth.settings.quality = quality
            if pin_group is not None:
                cloth.settings.vertex_group_mass = str(pin_group)
        elif cloth is not None:
            obj.modifiers.remove(cloth)
            changed = True
        return {
            "object_name": obj.name,
            "changed": changed,
            "operation": "configure_cloth_simulation",
            "quality": cloth.settings.quality if cloth and bool(enabled) else None,
        }

    def bake_physics_simulation(self, frame_start=None, frame_end=None):
        """Bake the active scene's physics cache through Blender's cache operator."""
        start = None if frame_start is None else self._bounded_wave_three_frame(frame_start)
        end = None if frame_end is None else self._bounded_wave_three_frame(frame_end)
        if start is not None and end is not None and end < start:
            raise ValueError("frame_end must be greater than or equal to frame_start")
        scene = bpy.context.scene
        previous = (scene.frame_start, scene.frame_end)
        try:
            if start is not None:
                scene.frame_start = start
            if end is not None:
                scene.frame_end = end
            bpy.ops.ptcache.bake_all(bake=True)
            return {
                "object_name": None,
                "changed": True,
                "operation": "bake_physics_simulation",
                "frame_start": scene.frame_start,
                "frame_end": scene.frame_end,
            }
        finally:
            scene.frame_start, scene.frame_end = previous

    def clear_physics_bake(self):
        """Clear all active scene physics cache data through Blender."""
        bpy.ops.ptcache.free_bake_all()
        return {"object_name": None, "changed": True, "operation": "clear_physics_bake"}

    def get_simulation_state(self, object_name):
        """Inspect bounded particle, force-field, and fluid modifier state."""
        obj = bpy.data.objects.get(str(object_name))
        if obj is None:
            raise ValueError(f"Object not found: {object_name}")
        particles = []
        for particle_system in list(obj.particle_systems)[:16]:
            settings = particle_system.settings
            particles.append(
                {
                    "name": particle_system.name,
                    "count": settings.count,
                    "frame_start": settings.frame_start,
                    "frame_end": settings.frame_end,
                    "lifetime": settings.lifetime,
                    "physics_type": settings.physics_type,
                }
            )
        effector = (
            obj
            if obj.field is not None
            else next((item for item in bpy.data.objects if item.get("arwaky_force_target") == obj.name), None)
        )
        field = effector.field if effector is not None else None
        fluid_modifier = next((item for item in obj.modifiers if item.type == "FLUID"), None)
        domain = fluid_modifier.domain_settings if fluid_modifier else None
        return {
            "object_name": obj.name,
            "particle_systems": particles,
            "force_field_enabled": field is not None and field.type != "NONE",
            "force_field_type": field.type if field is not None and field.type != "NONE" else None,
            "force_field_strength": field.strength if field is not None and field.type != "NONE" else None,
            "fluid_domain_enabled": domain is not None,
            "fluid_domain_type": domain.domain_type if domain else None,
            "fluid_resolution": domain.resolution_max if domain else None,
            "fluid_cache_type": domain.cache_type if domain else None,
        }

    def get_simulation_cache_status(self):
        """Inspect bounded cache state without creating a task registry."""
        scene = bpy.context.scene
        caches = []
        for obj in list(bpy.data.objects)[:1000]:
            for modifier in list(obj.modifiers)[:32]:
                if modifier.type not in {"CLOTH", "FLUID"}:
                    continue
                point_cache = getattr(modifier, "point_cache", None)
                domain = getattr(modifier, "domain_settings", None)
                caches.append(
                    {
                        "object_name": obj.name,
                        "modifier_name": modifier.name,
                        "modifier_type": modifier.type,
                        "is_baked": bool(getattr(point_cache, "is_baked", False)) if point_cache else False,
                        "cache_frame_start": getattr(domain, "cache_frame_start", None)
                        if domain
                        else getattr(point_cache, "frame_start", None),
                        "cache_frame_end": getattr(domain, "cache_frame_end", None)
                        if domain
                        else getattr(point_cache, "frame_end", None),
                    }
                )
        return {
            "frame_start": scene.frame_start,
            "frame_end": scene.frame_end,
            "current_frame": scene.frame_current,
            "cache_states": caches[:100],
        }

    def configure_particle_system(
        self,
        object_name,
        enabled,
        count=1000,
        frame_start=1,
        frame_end=200,
        lifetime=50.0,
        physics_type="NEWTON",
    ):
        """Configure one bounded particle system on a mesh object."""
        obj = bpy.data.objects.get(str(object_name))
        if obj is None:
            raise ValueError(f"Object not found: {object_name}")
        if obj.type != "MESH":
            raise ValueError("Particle systems require a mesh object")
        count = int(count)
        frame_start = self._bounded_wave_three_frame(frame_start)
        frame_end = self._bounded_wave_three_frame(frame_end)
        lifetime = float(lifetime)
        physics_type = str(physics_type).upper()
        if not 1 <= count <= 1_000_000:
            raise ValueError("count must be between 1 and 1000000")
        if frame_end <= frame_start:
            raise ValueError("frame_end must be greater than frame_start")
        if not math.isfinite(lifetime) or not 0.1 <= lifetime <= 100000.0:
            raise ValueError("lifetime must be between 0.1 and 100000")
        if physics_type not in {"NEWTON", "KEYED", "BOIDS", "FLUID"}:
            raise ValueError(f"Unsupported particle physics type: {physics_type}")
        changed = False
        bpy.ops.object.select_all(action="DESELECT")
        obj.select_set(True)
        bpy.context.view_layer.objects.active = obj
        if bool(enabled):
            if len(obj.particle_systems) == 0:
                bpy.ops.object.particle_system_add()
                changed = True
            particle_system = obj.particle_systems[-1]
            settings = particle_system.settings
            if (
                settings.count,
                settings.frame_start,
                settings.frame_end,
                settings.lifetime,
                settings.physics_type,
            ) != (count, frame_start, frame_end, lifetime, physics_type):
                changed = True
            settings.count = count
            settings.frame_start = frame_start
            settings.frame_end = frame_end
            settings.lifetime = lifetime
            settings.physics_type = physics_type
            return {
                "object_name": obj.name,
                "changed": changed,
                "operation": "configure_particle_system",
                "particle_system_name": particle_system.name,
            }
        if len(obj.particle_systems) > 0:
            bpy.ops.object.particle_system_remove()
            changed = True
        return {
            "object_name": obj.name,
            "changed": changed,
            "operation": "configure_particle_system",
            "particle_system_name": None,
        }

    def configure_force_field(
        self,
        object_name,
        enabled,
        field_type="FORCE",
        strength=1.0,
        noise=0.0,
    ):
        """Configure a bounded force field on an existing object."""
        obj = bpy.data.objects.get(str(object_name))
        if obj is None:
            raise ValueError(f"Object not found: {object_name}")
        field_type = str(field_type).upper()
        strength = float(strength)
        noise = float(noise)
        if field_type not in {"FORCE", "WIND", "VORTEX", "MAGNET", "TURBULENCE"}:
            raise ValueError(f"Unsupported force field type: {field_type}")
        if not math.isfinite(strength) or not -1.0e6 <= strength <= 1.0e6:
            raise ValueError("strength must be between -1000000 and 1000000")
        if not math.isfinite(noise) or not 0.0 <= noise <= 1.0e6:
            raise ValueError("noise must be between 0 and 1000000")
        effector = (
            obj
            if obj.field is not None
            else next((item for item in bpy.data.objects if item.get("arwaky_force_target") == obj.name), None)
        )
        if bool(enabled):
            changed = False
            if effector is None or effector.field is None:
                bpy.ops.object.effector_add(type=field_type, location=obj.location)
                effector = bpy.context.object
                effector.name = f"{obj.name}_ForceField"
                effector["arwaky_force_target"] = obj.name
                changed = True
            field = effector.field
            previous = (field.type, field.strength, field.noise)
            field.type = field_type
            field.strength = strength
            field.noise = noise
            changed = changed or previous != (field.type, field.strength, field.noise)
            return {
                "object_name": obj.name,
                "changed": changed,
                "operation": "configure_force_field",
                "force_field_type": field.type,
                "effector_name": effector.name,
            }
        if effector is None or effector.field is None:
            return {
                "object_name": obj.name,
                "changed": False,
                "operation": "configure_force_field",
                "force_field_type": None,
            }
        if effector is not obj and effector.get("arwaky_force_target") == obj.name:
            bpy.data.objects.remove(effector, do_unlink=True)
            return {
                "object_name": obj.name,
                "changed": True,
                "operation": "configure_force_field",
                "force_field_type": None,
            }
        previous = (effector.field.type, effector.field.strength, effector.field.noise)
        effector.field.type = "NONE"
        return {
            "object_name": obj.name,
            "changed": previous[0] != "NONE",
            "operation": "configure_force_field",
            "force_field_type": None,
        }

    def configure_fluid_domain(
        self,
        object_name,
        enabled,
        domain_type="LIQUID",
        resolution=64,
        cache_type="REPLAY",
    ):
        """Configure a bounded fluid domain modifier baseline."""
        obj = bpy.data.objects.get(str(object_name))
        if obj is None:
            raise ValueError(f"Object not found: {object_name}")
        if obj.type != "MESH":
            raise ValueError("Fluid domains require a mesh object")
        domain_type = str(domain_type).upper()
        cache_type = str(cache_type).upper()
        resolution = int(resolution)
        if domain_type not in {"LIQUID", "GAS"}:
            raise ValueError(f"Unsupported fluid domain type: {domain_type}")
        if not 4 <= resolution <= 512:
            raise ValueError("resolution must be between 4 and 512")
        if cache_type not in {"REPLAY", "MODULAR", "FINAL"}:
            raise ValueError(f"Unsupported fluid cache type: {cache_type}")
        modifier = next((item for item in obj.modifiers if item.type == "FLUID"), None)
        changed = False
        if bool(enabled):
            if modifier is None:
                modifier = obj.modifiers.new(name="Fluid", type="FLUID")
                changed = True
            modifier.fluid_type = "DOMAIN"
            domain = modifier.domain_settings
            if domain is None:
                raise RuntimeError("Blender did not initialize fluid domain settings")
            previous = (domain.domain_type, domain.resolution_max, domain.cache_type)
            domain.domain_type = domain_type
            domain.resolution_max = resolution
            domain.cache_type = cache_type
            changed = changed or previous != (domain.domain_type, domain.resolution_max, domain.cache_type)
            return {
                "object_name": obj.name,
                "changed": changed,
                "operation": "configure_fluid_domain",
                "fluid_domain_type": domain.domain_type,
            }
        if modifier is not None:
            obj.modifiers.remove(modifier)
            changed = True
        return {
            "object_name": obj.name,
            "changed": changed,
            "operation": "configure_fluid_domain",
            "fluid_domain_type": None,
        }

    @staticmethod
    def _bounded_wave_two_limit(value):
        limit = int(value)
        if not 1 <= limit <= 1000:
            raise ValueError("limit must be between 1 and 1000")
        return limit

    @staticmethod
    def _bounded_wave_two_frame(value):
        frame = int(value)
        if not -100000 <= frame <= 100000:
            raise ValueError("frame must be between -100000 and 100000")
        return frame

    def inspect_geometry_node_group(self, node_group_name):
        """Inspect a bounded Geometry Nodes graph and its interface sockets."""
        name = str(node_group_name).strip()
        if not name:
            raise ValueError("node_group_name is required")
        group = bpy.data.node_groups.get(name)
        if group is None:
            raise ValueError(f"Geometry Nodes group not found: {name}")
        links = []
        for link in list(group.links)[:256]:
            links.append(
                {
                    "from_node": link.from_node.name,
                    "from_socket": link.from_socket.name,
                    "to_node": link.to_node.name,
                    "to_socket": link.to_socket.name,
                }
            )
        sockets = []
        interface = getattr(group, "interface", None)
        if interface is not None and hasattr(interface, "items_tree"):
            for item in list(interface.items_tree)[:256]:
                if hasattr(item, "socket_type"):
                    sockets.append(
                        {
                            "name": item.name,
                            "socket_type": item.socket_type,
                            "is_output": getattr(item, "in_out", "INPUT") == "OUTPUT",
                        }
                    )
        return {
            "name": group.name,
            "node_count": len(group.nodes),
            "link_count": len(links),
            "links": links,
            "sockets": sockets,
        }

    def create_geometry_node_group(self, node_group_name, object_name=None):
        """Create or reuse a Geometry Nodes group and optionally bind a modifier."""
        name = str(node_group_name).strip()
        if not name or len(name) > 128:
            raise ValueError("node_group_name must be 1-128 characters")
        group = bpy.data.node_groups.get(name)
        created = group is None
        if group is None:
            group = bpy.data.node_groups.new(name, "GeometryNodeTree")
            interface = getattr(group, "interface", None)
            if interface is not None:
                interface.new_socket(name="Geometry", in_out="INPUT", socket_type="NodeSocketGeometry")
                interface.new_socket(name="Geometry", in_out="OUTPUT", socket_type="NodeSocketGeometry")
            input_node = group.nodes.new("NodeGroupInput")
            output_node = group.nodes.new("NodeGroupOutput")
            input_socket = input_node.outputs.get("Geometry")
            output_socket = output_node.inputs.get("Geometry")
            if input_socket is not None and output_socket is not None:
                group.links.new(input_socket, output_socket)
        modifier_name = None
        resolved_object = None
        if object_name:
            obj = bpy.data.objects.get(str(object_name))
            if obj is None:
                raise ValueError(f"Object not found: {object_name}")
            modifier = next((item for item in obj.modifiers if item.type == "NODES"), None)
            if modifier is None:
                modifier = obj.modifiers.new(name="GeometryNodes", type="NODES")
            modifier.node_group = group
            modifier_name = modifier.name
            resolved_object = obj.name
        return {
            "group_name": group.name,
            "created": created,
            "changed": created or bool(modifier_name),
            "object_name": resolved_object,
            "modifier_name": modifier_name,
        }

    def set_geometry_node_link(self, node_group_name, from_node, from_socket, to_node, to_socket):
        """Create one validated Geometry Nodes socket link."""
        group = bpy.data.node_groups.get(str(node_group_name))
        if group is None:
            raise ValueError(f"Geometry Nodes group not found: {node_group_name}")
        source = group.nodes.get(str(from_node))
        target = group.nodes.get(str(to_node))
        if source is None or target is None:
            raise ValueError("Geometry Nodes source or target node not found")
        source_socket = source.outputs.get(str(from_socket))
        target_socket = target.inputs.get(str(to_socket))
        if source_socket is None or target_socket is None:
            raise ValueError("Geometry Nodes source or target socket not found")
        for link in group.links:
            if link.from_socket == source_socket and link.to_socket == target_socket:
                return {"group_name": group.name, "changed": False, "message": "Link already exists"}
        group.links.new(source_socket, target_socket)
        return {"group_name": group.name, "changed": True, "message": "Link created"}

    def set_geometry_node_modifier(self, object_name, node_group_name):
        """Bind an existing Geometry Nodes group to an object modifier."""
        obj = bpy.data.objects.get(str(object_name))
        if obj is None:
            raise ValueError(f"Object not found: {object_name}")
        group = bpy.data.node_groups.get(str(node_group_name))
        if group is None:
            raise ValueError(f"Geometry Nodes group not found: {node_group_name}")
        modifier = next((item for item in obj.modifiers if item.type == "NODES"), None)
        if modifier is None:
            modifier = obj.modifiers.new(name="GeometryNodes", type="NODES")
        changed = modifier.node_group != group
        modifier.node_group = group
        return {
            "group_name": group.name,
            "changed": changed,
            "object_name": obj.name,
            "modifier_name": modifier.name,
        }

    def get_animation_state(self, object_name, limit=100):
        """Inspect bounded action and F-curve state for one object."""
        limit = self._bounded_wave_two_limit(limit)
        obj = bpy.data.objects.get(str(object_name))
        if obj is None:
            raise ValueError(f"Object not found: {object_name}")
        action = obj.animation_data.action if obj.animation_data and obj.animation_data.action else None
        curves = []
        if action:
            for curve in list(action.fcurves)[:limit]:
                curves.append(
                    {
                        "data_path": curve.data_path,
                        "array_index": curve.array_index,
                        "keyframes": [
                            {
                                "frame": point.co.x,
                                "value": point.co.y,
                            }
                            for point in list(curve.keyframe_points)[:limit]
                        ],
                    }
                )
        scene = bpy.context.scene
        return {
            "object_name": obj.name,
            "action_name": action.name if action else None,
            "frame_start": scene.frame_start,
            "frame_end": scene.frame_end,
            "current_frame": scene.frame_current,
            "curve_count": len(curves),
            "curves": curves,
        }

    def insert_object_keyframe(self, object_name, frame, data_path, index=None):
        """Insert a keyframe only for supported transform data paths."""
        frame = self._bounded_wave_two_frame(frame)
        path = str(data_path)
        if path not in {"location", "rotation_euler", "scale"}:
            raise ValueError(f"Unsupported animation data path: {path}")
        if index is None:
            keyframe_index = -1
        else:
            keyframe_index = int(index)
            if not 0 <= keyframe_index <= 3:
                raise ValueError("index must be between 0 and 3")
        obj = bpy.data.objects.get(str(object_name))
        if obj is None:
            raise ValueError(f"Object not found: {object_name}")
        bpy.context.scene.frame_set(frame)
        obj.keyframe_insert(data_path=path, index=keyframe_index, frame=frame)
        return {"object_name": obj.name, "data_path": path, "frame": frame, "index": index, "changed": True}

    def set_timeline_range(self, frame_start, frame_end, current_frame=None):
        """Set a bounded scene timeline range."""
        start = self._bounded_wave_two_frame(frame_start)
        end = self._bounded_wave_two_frame(frame_end)
        if end < start:
            raise ValueError("frame_end must be greater than or equal to frame_start")
        scene = bpy.context.scene
        current = scene.frame_current if current_frame is None else self._bounded_wave_two_frame(current_frame)
        if not start <= current <= end:
            raise ValueError("current_frame must be within the timeline range")
        scene.frame_start = start
        scene.frame_end = end
        scene.frame_set(current)
        return {"frame_start": start, "frame_end": end, "current_frame": scene.frame_current}

    def list_object_keyframes(self, object_name, limit=100):
        """Return the same bounded animation state under an explicit list action."""
        return self.get_animation_state(object_name, limit)

    def get_mesh_statistics(self, object_name):
        """Return bounded mesh topology and UV statistics."""
        obj = bpy.data.objects.get(str(object_name))
        if obj is None:
            raise ValueError(f"Object not found: {object_name}")
        if obj.type != "MESH":
            raise ValueError(f"Object is not a mesh: {obj.name}")
        mesh = obj.data
        return {
            "object_name": obj.name,
            "vertex_count": len(mesh.vertices),
            "edge_count": len(mesh.edges),
            "polygon_count": len(mesh.polygons),
            "uv_layer_count": len(mesh.uv_layers),
            "has_custom_normals": bool(getattr(mesh, "has_custom_normals", False)),
        }

    def validate_mesh(self, object_name, limit=100):
        """Validate loose vertices, degenerate faces, and non-manifold edges."""
        limit = self._bounded_wave_two_limit(limit)
        obj = bpy.data.objects.get(str(object_name))
        if obj is None:
            raise ValueError(f"Object not found: {object_name}")
        if obj.type != "MESH":
            raise ValueError(f"Object is not a mesh: {obj.name}")
        import bmesh

        bm = bmesh.new()
        try:
            bm.from_mesh(obj.data)
            bm.verts.ensure_lookup_table()
            bm.edges.ensure_lookup_table()
            bm.faces.ensure_lookup_table()
            findings = []
            loose = [vertex.index for vertex in bm.verts if not vertex.link_edges][:limit]
            degenerate = [face.index for face in bm.faces if len(face.verts) < 3 or face.calc_area() <= 1.0e-12][:limit]
            non_manifold = [edge.index for edge in bm.edges if not edge.is_manifold][:limit]
            for category, values in (
                ("loose_vertices", loose),
                ("degenerate_faces", degenerate),
                ("non_manifold_edges", non_manifold),
            ):
                if values:
                    findings.append({"category": category, "count": len(values), "examples": values})
            return {"object_name": obj.name, "valid": not findings, "findings": findings}
        finally:
            bm.free()

    def perform_mesh_edit_operation(self, object_name, operation):
        """Perform one bounded bmesh operation without requiring edit-mode context."""
        operation = str(operation)
        if operation not in {"recalculate_normals", "triangulate", "remove_doubles"}:
            raise ValueError(f"Unsupported mesh operation: {operation}")
        obj = bpy.data.objects.get(str(object_name))
        if obj is None:
            raise ValueError(f"Object not found: {object_name}")
        if obj.type != "MESH":
            raise ValueError(f"Object is not a mesh: {obj.name}")
        import bmesh

        bm = bmesh.new()
        try:
            bm.from_mesh(obj.data)
            changed = False
            if operation == "recalculate_normals":
                bmesh.ops.recalc_face_normals(bm, faces=list(bm.faces))
                changed = True
            elif operation == "triangulate":
                result = bmesh.ops.triangulate(bm, faces=list(bm.faces))
                changed = bool(result.get("faces"))
            else:
                result = bmesh.ops.remove_doubles(bm, verts=list(bm.verts), dist=1.0e-6)
                changed = bool(result.get("targetmap"))
            bm.to_mesh(obj.data)
            obj.data.update()
            return {"object_name": obj.name, "operation": operation, "changed": changed}
        finally:
            bm.free()

    def ensure_mesh_uv_layer(self, object_name, uv_layer_name="UVMap"):
        """Create or reuse a named UV layer for a mesh object."""
        name = str(uv_layer_name).strip() or "UVMap"
        if len(name) > 64:
            raise ValueError("uv_layer_name must not exceed 64 characters")
        obj = bpy.data.objects.get(str(object_name))
        if obj is None:
            raise ValueError(f"Object not found: {object_name}")
        if obj.type != "MESH":
            raise ValueError(f"Object is not a mesh: {obj.name}")
        layer = obj.data.uv_layers.get(name)
        created = layer is None
        if layer is None:
            layer = obj.data.uv_layers.new(name=name)
        return {
            "object_name": obj.name,
            "operation": "ensure_mesh_uv_layer",
            "changed": created,
            "uv_layer_name": layer.name,
        }

    def execute_blender_code(self, code):
        out = io.StringIO()
        try:
            with redirect_stdout(out):
                exec(code, {"bpy": bpy, "mathutils": __import__("mathutils")})  # nosec
            return {"executed": True, "result": out.getvalue()}
        except Exception as e:
            return {"executed": False, "error": str(e)}

    def get_telemetry_consent(self):
        try:
            addon_prefs = bpy.context.preferences.addons[__package__].preferences
            return {
                "consent": getattr(addon_prefs, "telemetry_consent", False),
                "message": "Telemetry consent status retrieved",
            }
        except Exception as e:
            return {"error": f"Failed to get telemetry consent: {str(e)}"}
