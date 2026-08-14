from __future__ import annotations

import json
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


def test_run_routes_command_to_injected_dispatcher_and_returns_json(capsys) -> None:
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
            "run",
            "--filepath",
            "/tmp/example.blend",
            "--action",
            "get_scene_info",
            "--params",
            '{"include_objects": true}',
        ],
        dispatcher=dispatcher,
    )

    assert exit_code == EXIT_SUCCESS
    assert len(dispatcher.requests) == 1
    assert dispatcher.requests[0].action_name == "get_scene_info"
    assert dispatcher.requests[0].parameters == {"include_objects": True}
    output = _json_output(capsys)
    assert output["success"] is True
    assert output["tracking_id"] == "track-cli-001"
    assert output["result"] == {"object": "Cube"}


def test_run_masks_dispatcher_error_and_uses_validation_exit_code(capsys) -> None:
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
            "run",
            "--filepath",
            "/tmp/example.blend",
            "--action",
            "get_scene_info",
        ],
        dispatcher=dispatcher,
    )

    assert exit_code == EXIT_VALIDATION
    output = _json_output(capsys)
    assert output == {
        "success": False,
        "error": "Operation failed",
        "category": "validation_error",
        "ref": "cli-502",
    }
    assert "private" not in json.dumps(output)


def test_run_auto_wires_dispatcher_when_not_injected(monkeypatch, capsys) -> None:
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
        def __init__(self, config: object) -> None:
            self.agent = object()

        def wire(self) -> None:
            return None

    class FakeDispatcherContainer:
        def __init__(self, launcher_action_router: object) -> None:
            self.agent = dispatcher

        def wire(self) -> None:
            return None

    monkeypatch.setattr(launcher_container_module, "LauncherConfigVO", FakeLauncherConfigVO)
    monkeypatch.setattr(launcher_container_module, "LauncherContainer", FakeLauncherContainer)
    monkeypatch.setattr(dispatcher_container_module, "DispatcherContainer", FakeDispatcherContainer)

    exit_code = main(
        [
            "--json",
            "run",
            "--filepath",
            "/tmp/example.blend",
            "--action",
            "get_scene_info",
        ]
    )

    assert exit_code == EXIT_SUCCESS
    assert len(dispatcher.requests) == 1
    assert _json_output(capsys)["tracking_id"] == "track-cli-003"


def test_invalid_json_params_is_masked_with_validation_exit_code(capsys) -> None:
    exit_code = main(
        [
            "--json",
            "run",
            "--filepath",
            "/tmp/example.blend",
            "--action",
            "get_scene_info",
            "--params",
            "{not-json}",
        ],
        dispatcher=FakeDispatcher(UnifiedResultEnvelopeVO.success_envelope(message="unused", tracking_id="unused")),
    )

    assert exit_code == EXIT_VALIDATION
    output = _json_output(capsys)
    assert output["success"] is False
    assert output["category"] == "validation_error"
    assert output["ref"] == "cli-400"
