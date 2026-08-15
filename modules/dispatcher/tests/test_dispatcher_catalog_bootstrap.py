from __future__ import annotations

from modules.dispatcher.src.root_dispatcher_container import DispatcherContainer
from modules.shared.src.dispatcher.taxonomy_action_command_vo import ActionCommandVO


class RecordingRouter:
    def __init__(self) -> None:
        self.calls: list[tuple[str, dict[str, object]]] = []

    def execute_action(self, action_name: str, params: dict[str, object]) -> dict[str, object]:
        self.calls.append((action_name, params))
        return {"action": action_name, "parameters": params}


def test_container_bootstraps_canonical_catalog_and_dispatches() -> None:
    router = RecordingRouter()
    container = DispatcherContainer(launcher_action_router=router)
    container.wire()

    result = container.agent.execute_action(ActionCommandVO(action_name="get_scene_info", parameters={}))

    assert result.success is True  # nosec B101
    assert router.calls == [("get_scene_info", {})]  # nosec B101


def test_container_rejects_unknown_action_before_router_call() -> None:
    router = RecordingRouter()
    container = DispatcherContainer(launcher_action_router=router)
    container.wire()

    result = container.agent.execute_action(ActionCommandVO(action_name="not_a_real_action", parameters={}))

    assert result.success is False  # nosec B101
    assert router.calls == []  # nosec B101
