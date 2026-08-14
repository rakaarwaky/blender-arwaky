from __future__ import annotations

import json
import os
import sys
import time
from pathlib import Path

from modules.shared.src.gateway.capabilities_socket_client import BlenderSocketClient


port = int(os.environ.get("BLENDERMCP_PORT", "9987"))
output = Path(os.environ.get("E2E_OUTPUT", "/tmp/blender-arwaky-e2e.png"))


def expect_success(label: str, response: dict[str, object]) -> None:
    if response.get("status") != "success":
        raise RuntimeError(f"{label} failed: {response}")
    print(f"PASS {label}")


with BlenderSocketClient(port=port, timeout=10.0) as client:
    expect_success("get_scene_info", client.send_command("get_scene_info", {}))
    expect_success(
        "execute_code",
        client.send_command(
            "execute_code",
            {
                "code": "import bpy; bpy.ops.mesh.primitive_cube_add(location=(0, 0, 0)); bpy.context.object.name='E2ECube'"
            },
        ),
    )
    object_response = client.send_command("get_object_info", {"name": "E2ECube"})
    expect_success("get_object_info", object_response)
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
print("PASS close client")
