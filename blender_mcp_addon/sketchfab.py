import base64
import logging
import os
import shutil
import tempfile
import zipfile

import bpy  # type: ignore
import mathutils  # type: ignore
import requests  # type: ignore

logger = logging.getLogger(__name__)

# Valid Sketchfab thumbnail sizes
THUMBNAIL_MIN_WIDTH = 400


def get_sketchfab_status():
    """Check if Sketchfab integration is enabled in Blender."""
    try:
        scene = bpy.context.scene
        if scene is None:
            return {"enabled": False, "message": "No active scene"}

        enabled = getattr(scene, "blendermcp_use_sketchfab", False)
        if enabled:
            return {"enabled": True, "message": "Sketchfab integration is enabled"}
        else:
            return {"enabled": False, "message": "Sketchfab integration is disabled"}
    except Exception as e:
        return {"error": str(e)}


def _safe_extract_zip(zip_path, extract_dir):
    """Extract ZIP with path traversal protection."""
    with zipfile.ZipFile(zip_path, "r") as zip_ref:
        for member in zip_ref.namelist():
            member_path = os.path.realpath(os.path.join(extract_dir, member))
            if not member_path.startswith(os.path.realpath(extract_dir)):
                raise RuntimeError(f"Zip path traversal attempt: {member}")
        zip_ref.extractall(extract_dir)


def download_sketchfab_model(uid, normalize_size=True, target_size=1.0):
    """Download a model from Sketchfab by its UID."""
    temp_dir = None
    try:
        api_key = bpy.context.scene.blendermcp_sketchfab_api_key
        if not api_key:
            return {"error": "Sketchfab API key is not configured"}

        headers = {"Authorization": f"Token {api_key}"}
        download_endpoint = f"https://api.sketchfab.com/v3/models/{uid}/download"

        response = requests.get(download_endpoint, headers=headers, timeout=30)
        if response.status_code != 200:
            return {"error": f"Download request failed with status code {response.status_code}"}

        data = response.json()
        gltf_data = data.get("gltf")
        if not gltf_data:
            return {"error": "No gltf download URL available"}

        download_url = gltf_data.get("url")

        # Stream download to avoid loading entire ZIP into memory
        temp_dir = tempfile.mkdtemp()
        zip_file_path = os.path.join(temp_dir, f"{uid}.zip")
        with requests.get(download_url, stream=True, timeout=60) as r:
            r.raise_for_status()
            with open(zip_file_path, "wb") as f:
                for chunk in r.iter_content(chunk_size=8192):
                    f.write(chunk)

        _safe_extract_zip(zip_file_path, temp_dir)

        gltf_files = []
        for root, dirs, files in os.walk(temp_dir):
            for file in files:
                if file.endswith((".gltf", ".glb")):
                    gltf_files.append(os.path.join(root, file))

        if not gltf_files:
            return {"error": "No glTF file found"}

        main_file = gltf_files[0]

        # Track objects BEFORE import
        pre_import_objs = set(bpy.data.objects.keys())

        bpy.ops.import_scene.gltf(filepath=main_file)

        # Find new objects
        post_import_objs = set(bpy.data.objects.keys())
        imported_object_names = list(post_import_objs - pre_import_objs)
        imported_objects = [bpy.data.objects[name] for name in imported_object_names]

        if not imported_objects:
            return {"error": "No objects imported"}

        # Scaling logic
        scale_applied = 1.0
        final_dims = (0.0, 0.0, 0.0)
        world_bbox = None

        if normalize_size and target_size > 0:
            min_v = mathutils.Vector((float("inf"), float("inf"), float("inf")))
            max_v = mathutils.Vector((float("-inf"), float("-inf"), float("-inf")))

            found_mesh = False
            for obj in imported_objects:
                if obj.type == "MESH":
                    found_mesh = True
                    for corner in obj.bound_box:
                        world_corner = obj.matrix_world @ mathutils.Vector(corner)
                        for i in range(3):
                            min_v[i] = min(min_v[i], world_corner[i])
                            max_v[i] = max(max_v[i], world_corner[i])

            if found_mesh:
                dims = max_v - min_v
                max_dim = max(dims)
                if max_dim > 0:
                    scale_applied = target_size / max_dim
                    roots = [
                        obj
                        for obj in imported_objects
                        if obj.parent is None or obj.parent.name not in imported_object_names
                    ]
                    for root in roots:
                        root.scale *= scale_applied

                    final_dims = tuple(dims * scale_applied)
                    world_bbox = (tuple(min_v * scale_applied), tuple(max_v * scale_applied))

        root_objects = [
            obj.name for obj in imported_objects if obj.parent is None or obj.parent.name not in imported_object_names
        ]

        return {
            "success": True,
            "message": "Model imported successfully",
            "imported_objects": imported_object_names,
            "root_objects": root_objects,
            "normalized": normalize_size,
            "scale_applied": scale_applied,
            "dimensions": final_dims,
            "world_bounding_box": world_bbox,
        }

    except Exception as e:
        logger.exception("Failed to download model: %s", str(e))
        return {"error": f"Failed to download model: {str(e)}"}
    finally:
        # Always clean up temp directory
        if temp_dir and os.path.exists(temp_dir):
            shutil.rmtree(temp_dir, ignore_errors=True)


def search_sketchfab_models(query, count=20, downloadable=True, categories=None):
    """Search for models on Sketchfab with optional filtering."""
    try:
        api_key = bpy.context.scene.blendermcp_sketchfab_api_key
        if not api_key:
            return {"error": "Sketchfab API key is not configured"}

        headers = {"Authorization": f"Token {api_key}"}
        params = {"q": query, "type": "models", "downloadable": str(downloadable).lower(), "count": count}
        if categories:
            params["categories"] = categories

        response = requests.get(
            "https://api.sketchfab.com/v3/search",
            headers=headers,
            params=params,
            timeout=10,
        )
        if response.status_code == 200:
            return response.json()
        return {"error": f"Search request failed: {response.status_code}"}
    except Exception as e:
        return {"error": str(e)}


def get_sketchfab_model_preview(uid):
    """Get preview thumbnail for a Sketchfab model."""
    try:
        api_key = bpy.context.scene.blendermcp_sketchfab_api_key
        if not api_key:
            return {"error": "Sketchfab API key is not configured"}

        headers = {"Authorization": f"Token {api_key}"}
        response = requests.get(f"https://api.sketchfab.com/v3/models/{uid}", headers=headers, timeout=30)

        if response.status_code != 200:
            return {"error": f"Failed to get model info: {response.status_code}"}

        data = response.json()
        thumbnails = data.get("thumbnails", {}).get("images", [])
        if not thumbnails:
            return {"error": "No thumbnail available"}

        # Use a reasonable size thumbnail
        thumbnail_url = None
        for thumb in thumbnails:
            if thumb.get("width", 0) >= THUMBNAIL_MIN_WIDTH:
                thumbnail_url = thumb.get("url")
                break
        if not thumbnail_url:
            thumbnail_url = thumbnails[0].get("url")

        if not thumbnail_url:
            return {"error": "No valid thumbnail URL"}

        img_response = requests.get(thumbnail_url, timeout=30)
        image_data = base64.b64encode(img_response.content).decode("ascii")

        ext = thumbnail_url.split(".")[-1].lower()
        fmt = "jpeg" if ext in ("jpg", "jpeg") else "png"

        return {
            "success": True,
            "image_data": image_data,
            "format": fmt,
            "model_name": data.get("name", "Unknown"),
            "author": data.get("user", {}).get("username", "Unknown"),
            "uid": uid,
        }
    except Exception as e:
        return {"error": str(e)}
