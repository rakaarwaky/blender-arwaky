from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class RigifyInspectArmatureRequest:
    """Validated request for inspecting one armature through the Blender bridge."""

    object_name: str
    limit: int = 100

    def __post_init__(self) -> None:
        name = str(self.object_name).strip()
        if not name or len(name) > 128 or any(ord(char) < 32 for char in name):
            raise ValueError("object_name must contain 1-128 printable characters")
        if not 1 <= int(self.limit) <= 1000:
            raise ValueError("limit must be between 1 and 1000")


def map_inspect_armature(request: RigifyInspectArmatureRequest) -> dict[str, object]:
    """Map a validated Rigify request to the canonical Blender command."""
    return {
        "type": "inspect_armature",
        "params": {
            "object_name": str(request.object_name).strip(),
            "limit": int(request.limit),
        },
    }
