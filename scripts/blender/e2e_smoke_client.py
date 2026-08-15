from __future__ import annotations

import os
import tempfile
from pathlib import Path

from modules.shared.src.gateway.capabilities_socket_client import BlenderSocketClient

port = int(os.environ.get("BLENDERMCP_PORT", "9987"))
output = Path(
    os.environ.get(
        "E2E_OUTPUT",
        str(Path(tempfile.gettempdir()) / "blender-arwaky-e2e.png"),
    )
)
export_output = output.with_suffix(".glb")
hdri_output = output.with_suffix(".hdr")


def write_test_hdri(path: Path) -> None:
    """Write a tiny uncompressed Radiance HDR fixture for Blender loading."""
    header = b"#?RADIANCE\nFORMAT=32-bit_rle_rgbe\n\n-Y 2 +X 2\n"
    pixel = bytes((128, 96, 64, 128))
    path.write_bytes(header + pixel * 4)


write_test_hdri(hdri_output)


def expect_success(label: str, response: dict[str, object]) -> dict[str, object]:
    if response.get("status") != "success":
        raise RuntimeError(f"{label} failed: {response}")
    print(f"PASS {label}")
    return response


with BlenderSocketClient(port=port, timeout=10.0) as client:
    expect_success("get_scene_info", client.send_command("get_scene_info", {}))
    expect_success(
        "create_primitive",
        client.send_command(
            "create_primitive",
            {"primitive_type": "CUBE", "name": "E2ECube", "location": [0, 0, 0]},
        ),
    )
    expect_success(
        "set_object_transform",
        client.send_command(
            "set_object_transform",
            {"object_name": "E2ECube", "location": [1, 2, 3], "scale": [1.5, 1.5, 1.5]},
        ),
    )
    expect_success(
        "place_asset",
        client.send_command(
            "place_asset",
            {
                "asset_id": "E2ECube",
                "location": [4, 5, 6],
                "rotation": [10, 20, 30],
                "scale": [2, 2, 2],
            },
        ),
    )
    object_response = client.send_command("get_object_info", {"object_name": "E2ECube"})
    expect_success("get_object_info", object_response)
    expect_success(
        "set_material",
        client.send_command("set_material", {"object_name": "E2ECube", "material_name": "E2EMaterial"}),
    )
    expect_success(
        "execute_blender_code",
        client.send_command("execute_blender_code", {"code": "print(bpy.context.scene.name)"}),
    )
    expect_success(
        "setup_environment",
        client.send_command(
            "setup_environment",
            {"hdri_id": str(hdri_output), "strength": 1.25},
        ),
    )
    expect_success(
        "export_model",
        client.send_command(
            "export_model",
            {"object_name": "E2ECube", "file_path": str(export_output), "export_format": "glb"},
        ),
    )
    if not export_output.exists() or export_output.stat().st_size == 0:
        raise RuntimeError(f"export artifact missing: {export_output}")
    print("PASS export artifact")
    expect_success(
        "import_glb",
        client.send_command(
            "import_glb",
            {"file_path": str(export_output), "object_name": "ImportedCube"},
        ),
    )
    expect_success(
        "render",
        client.send_command(
            "render",
            {"output_path": str(output), "resolution_x": 320, "resolution_y": 240},
        ),
    )
    if not output.exists() or output.stat().st_size == 0:
        raise RuntimeError(f"render artifact missing: {output}")
    print("PASS render artifact")
    expect_success(
        "get_viewport_screenshot",
        client.send_command(
            "get_viewport_screenshot",
            {"filepath": str(output.with_name("blender-arwaky-e2e-screenshot.png")), "max_size": 320},
        ),
    )
    expect_success("delete_object", client.send_command("delete_object", {"object_name": "E2ECube"}))
    expect_success("delete_imported_object", client.send_command("delete_object", {"object_name": "ImportedCube"}))
    expect_success("cleanup_scene", client.send_command("cleanup_scene", {"mode": "meshes"}))
print("PASS close client")
