from __future__ import annotations

import pytest

from modules.vse.src.capabilities_vse_executor import VseExecutor
from modules.vse.src.root_vse_container import create_vse_feature


class FakeGateway:
    def __init__(self, result):
        self.result = result
        self.codes: list[str] = []

    async def execute_blender_code(self, code: str):
        self.codes.append(code)
        return self.result


@pytest.mark.asyncio
async def test_vse_inspection_returns_typed_strip_state() -> None:
    gateway = FakeGateway(
        {
            "sequence_present": True,
            "strips": [
                {
                    "name": "Color",
                    "strip_type": "COLOR",
                    "channel": 1,
                    "frame_start": 1,
                    "frame_final": 24,
                    "filepath": None,
                }
            ],
        }
    )

    result = await create_vse_feature(gateway).inspect()

    assert result.sequence_present is True
    assert result.strips[0].strip_type == "COLOR"
    assert result.strips[0].frame_final == 24


@pytest.mark.asyncio
async def test_vse_color_strip_can_be_created_without_media_path() -> None:
    gateway = FakeGateway({"changed": True, "strip_name": "Color", "strip_type": "COLOR"})

    result = await create_vse_feature(gateway).create_strip("COLOR", "Color", None, 1, 1, 24)

    assert result.changed is True
    assert result.strip_name == "Color"


@pytest.mark.asyncio
async def test_vse_media_strip_requires_filepath_before_gateway() -> None:
    gateway = FakeGateway({})

    with pytest.raises(ValueError, match="filepath is required"):
        await VseExecutor(gateway).create_strip("MOVIE", "Movie", None, 1, 1, 24)

    assert gateway.codes == []


@pytest.mark.asyncio
async def test_vse_rejects_out_of_range_channel() -> None:
    gateway = FakeGateway({})

    with pytest.raises(ValueError, match="channel must be between"):
        await VseExecutor(gateway).create_strip("COLOR", "Color", None, 129, 1, 24)
