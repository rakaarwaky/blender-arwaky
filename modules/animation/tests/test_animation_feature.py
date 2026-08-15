from __future__ import annotations

import pytest

from modules.animation.src.capabilities_animation_executor import AnimationExecutor
from modules.animation.src.root_animation_container import create_animation_feature


class FakeGateway:
    def __init__(self, result):
        self.result = result
        self.codes: list[str] = []

    async def execute_blender_code(self, code: str):
        self.codes.append(code)
        return self.result


@pytest.mark.asyncio
async def test_animation_state_returns_curves_and_keyframes() -> None:
    gateway = FakeGateway(
        {
            "object_name": "Cube",
            "action_name": "CubeAction",
            "frame_start": 1,
            "frame_end": 120,
            "current_frame": 24,
            "curves": [
                {
                    "data_path": "location",
                    "array_index": 0,
                    "keyframes": [{"frame": 1, "value": 0, "index": 0}],
                }
            ],
        }
    )

    result = await create_animation_feature(gateway).get_state("Cube")

    assert result.action_name == "CubeAction"
    assert result.curves[0].keyframes[0].frame == 1
    assert '"Cube"' in gateway.codes[0]


@pytest.mark.asyncio
async def test_animation_rejects_unsupported_path_before_gateway() -> None:
    gateway = FakeGateway({})

    with pytest.raises(ValueError, match="Unsupported animation data path"):
        await AnimationExecutor(gateway).insert_keyframe("Cube", 1, "location.x")

    assert gateway.codes == []


@pytest.mark.asyncio
async def test_animation_timeline_rejects_out_of_range_current_frame() -> None:
    gateway = FakeGateway({})

    with pytest.raises(ValueError, match="within the timeline range"):
        await AnimationExecutor(gateway).set_timeline(1, 10, 20)


@pytest.mark.asyncio
async def test_animation_keyframe_returns_typed_mutation() -> None:
    gateway = FakeGateway({"object_name": "Cube", "data_path": "scale", "frame": 12, "changed": True})

    result = await create_animation_feature(gateway).insert_keyframe("Cube", 12, "scale")

    assert result.object_name == "Cube"
    assert result.data_path == "scale"
    assert result.frame == 12
