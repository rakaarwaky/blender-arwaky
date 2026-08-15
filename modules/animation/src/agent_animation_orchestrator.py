"""Animation agent orchestrator implementing the Wave 2 aggregate."""

from __future__ import annotations

from modules.animation.src.capabilities_animation_executor import AnimationExecutor


class AnimationOrchestrator:
    """Coordinate animation operations without owning gateway transport."""

    def __init__(self, executor: AnimationExecutor) -> None:
        self._executor = executor

    async def get_state(self, object_name: str, limit: int = 100):
        return await self._executor.get_state(object_name, limit)

    async def insert_keyframe(self, object_name: str, frame: int, data_path: str, index: int | None = None):
        return await self._executor.insert_keyframe(object_name, frame, data_path, index)

    async def set_timeline(self, frame_start: int, frame_end: int, current_frame: int | None = None):
        return await self._executor.set_timeline(frame_start, frame_end, current_frame)

    async def list_keyframes(self, object_name: str, limit: int = 100):
        return await self._executor.list_keyframes(object_name, limit)
