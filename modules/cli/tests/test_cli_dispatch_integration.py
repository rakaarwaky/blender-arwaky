from __future__ import annotations

import json

import pytest

from modules.root_cli_main_entry import EXIT_SUCCESS, EXIT_VALIDATION, main
from modules.shared.src.dispatcher.taxonomy_action_command_vo import ActionCommandVO
from modules.shared.src.dispatcher.taxonomy_unified_result_envelope_vo import (
    UnifiedResultEnvelopeVO,
)


class FakeDispatcher:
    def __init__(self, envelope: UnifiedResultEnvelopeVO) -> None:
        self.envelope = envelope
        self.requests: list[ActionCommandVO] = []

    def execute_action(self, request: ActionCommandVO) -> UnifiedResultEnvelopeVO:
        self.requests.append(request)
        return self.envelope


def _json_output(capsys) -> dict[str, object]:
    return json.loads(capsys.readouterr().out)


def test_canonical_command_routes_to_injected_dispatcher_and_returns_json(capsys) -> None:
    dispatcher = FakeDispatcher(
        UnifiedResultEnvelopeVO.success_envelope(
            message="ok",
            tracking_id="track-cli-001",
            data={"object": "Cube"},
            metadata={"source": "dispatcher"},
        )
    )

    exit_code = main(
        [
            "--json",
            "get-scene-info",
            "--filepath",
            "example.blend",
        ],
        dispatcher=dispatcher,
    )

    assert exit_code == EXIT_SUCCESS  # nosec B101
    assert len(dispatcher.requests) == 1  # nosec B101
    assert dispatcher.requests[0].action_name == "get_scene_info"  # nosec B101
    assert dispatcher.requests[0].parameters == {}  # nosec B101
    output = _json_output(capsys)
    assert output["success"] is True  # nosec B101
    assert output["tracking_id"] == "track-cli-001"  # nosec B101
    assert output["result"] == {"object": "Cube"}  # nosec B101


def test_canonical_command_masks_dispatcher_error_and_uses_validation_exit_code(capsys) -> None:
    dispatcher = FakeDispatcher(
        UnifiedResultEnvelopeVO.error_envelope(
            message="internal secret: /root/private",
            tracking_id="track-cli-002",
            error_category="validation_error",
        )
    )

    exit_code = main(
        [
            "--json",
            "get-scene-info",
            "--filepath",
            "example.blend",
        ],
        dispatcher=dispatcher,
    )

    assert exit_code == EXIT_VALIDATION  # nosec B101
    output = _json_output(capsys)
    assert output["success"] is False  # nosec B101
    assert output["error"] == "Operation failed"  # nosec B101
    assert output["category"] == "validation_error"  # nosec B101
    assert output["ref"] == "cli-502"  # nosec B101
    assert output["message"] == "Operation failed"  # nosec B101
    assert output["hint"]  # nosec B101
    assert "detail" in output  # nosec B101
    assert "private" not in json.dumps(output)  # nosec B101


def test_canonical_command_auto_wires_dispatcher_when_not_injected(monkeypatch, capsys) -> None:
    import modules.dispatcher.src.root_dispatcher_container as dispatcher_container_module
    import modules.launcher.src.root_launcher_container as launcher_container_module

    dispatcher = FakeDispatcher(
        UnifiedResultEnvelopeVO.success_envelope(
            message="auto-wired",
            tracking_id="track-cli-003",
            data={"ok": True},
        )
    )

    class FakeLauncherConfigVO:
        pass

    class FakeLauncherContainer:
        def __init__(self, config: object) -> None:  # noqa: ARG002
            self.agent = object()

        def wire(self) -> None:
            return None

    class FakeDispatcherContainer:
        def __init__(self, launcher_action_router: object) -> None:  # noqa: ARG002
            self.agent = dispatcher

        def wire(self) -> None:
            return None

    monkeypatch.setattr(launcher_container_module, "LauncherConfigVO", FakeLauncherConfigVO)
    monkeypatch.setattr(launcher_container_module, "LauncherContainer", FakeLauncherContainer)
    monkeypatch.setattr(dispatcher_container_module, "DispatcherContainer", FakeDispatcherContainer)

    exit_code = main(
        [
            "--json",
            "get-scene-info",
            "--filepath",
            "example.blend",
        ]
    )

    assert exit_code == EXIT_SUCCESS  # nosec B101
    assert len(dispatcher.requests) == 1  # nosec B101
    assert _json_output(capsys)["tracking_id"] == "track-cli-003"  # nosec B101


def test_missing_required_canonical_flag_fails_before_dispatch() -> None:
    dispatcher = FakeDispatcher(UnifiedResultEnvelopeVO.success_envelope(message="unused", tracking_id="unused"))
    with pytest.raises(SystemExit):
        main(["--json", "execute-blender-code"], dispatcher=dispatcher)
    assert dispatcher.requests == []  # nosec B101
