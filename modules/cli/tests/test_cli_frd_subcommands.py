from __future__ import annotations

import json

import pytest

from modules.root_cli_main_entry import EXIT_VALIDATION, _build_parser, main
from modules.shared.src.dispatcher.taxonomy_action_command_vo import ActionCommandVO
from modules.shared.src.dispatcher.taxonomy_unified_result_envelope_vo import UnifiedResultEnvelopeVO


class RecordingDispatcher:
    def __init__(self) -> None:
        self.requests: list[ActionCommandVO] = []

    def execute_action(self, request: ActionCommandVO) -> UnifiedResultEnvelopeVO:
        self.requests.append(request)
        return UnifiedResultEnvelopeVO.success_envelope(
            message="ok",
            tracking_id="cli-subcommand-test",
            data={"action": request.action_name, "parameters": request.parameters},
        )


class RecordingActionRouter:
    def __init__(self) -> None:
        self.calls: list[tuple[str, dict[str, object]]] = []

    def execute_action(self, action_name: str, params: dict[str, object]) -> dict[str, object]:
        self.calls.append((action_name, params))
        return {"action": action_name, "parameters": params}


def _json(capsys) -> dict[str, object]:
    return json.loads(capsys.readouterr().out)


def test_scene_info_routes_exact_action(capsys) -> None:
    dispatcher = RecordingDispatcher()
    assert main(["--json", "get-scene-info"], dispatcher=dispatcher) == 0  # nosec B101
    assert dispatcher.requests[0].action_name == "get_scene_info"  # nosec B101
    assert dispatcher.requests[0].parameters == {}  # nosec B101
    assert _json(capsys)["success"] is True  # nosec B101


def test_create_maps_public_flags_to_action_schema(capsys) -> None:
    dispatcher = RecordingDispatcher()
    exit_code = main(
        ["--json", "create-primitive", "--primitive-type", "CUBE", "--location", "1", "2", "3", "--name", "Cube"],
        dispatcher=dispatcher,
    )
    assert exit_code == 0  # nosec B101
    assert dispatcher.requests[0].action_name == "create_primitive"  # nosec B101
    assert dispatcher.requests[0].parameters == {
        "primitive_type": "CUBE",
        "location": [1.0, 2.0, 3.0],
        "name": "Cube",
    }  # nosec B101
    assert _json(capsys)["tracking_id"] == "cli-subcommand-test"  # nosec B101


def test_import_maps_file_and_name(capsys) -> None:
    dispatcher = RecordingDispatcher()
    assert (
        main(["--json", "import-glb", "--file-path", "asset.glb", "--object-name", "Asset"], dispatcher=dispatcher) == 0
    )  # nosec B101
    assert dispatcher.requests[0].action_name == "import_glb"  # nosec B101
    assert dispatcher.requests[0].parameters == {"file_path": "asset.glb", "object_name": "Asset"}  # nosec B101
    assert _json(capsys)["success"] is True  # nosec B101


def test_run_code_maps_code_action(capsys) -> None:
    dispatcher = RecordingDispatcher()
    assert main(["--json", "execute-blender-code", "--code", "print('ok')"], dispatcher=dispatcher) == 0  # nosec B101
    assert dispatcher.requests[0].action_name == "execute_blender_code"  # nosec B101
    assert dispatcher.requests[0].parameters == {"code": "print('ok')"}  # nosec B101
    assert _json(capsys)["success"] is True  # nosec B101


def test_missing_required_argument_fails_before_dispatch() -> None:
    dispatcher = RecordingDispatcher()
    with pytest.raises(SystemExit):
        main(["--json", "get-object-info"], dispatcher=dispatcher)
    assert dispatcher.requests == []  # nosec B101


def test_unknown_command_has_suggestion(capsys) -> None:
    with pytest.raises(SystemExit) as raised:
        main(["get-runtime-statu"], dispatcher=RecordingDispatcher())
    assert raised.value.code == EXIT_VALIDATION  # nosec B101
    assert "Did you mean 'get-runtime-status'?" in capsys.readouterr().err  # nosec B101


def test_destructive_command_requires_confirmation(capsys) -> None:
    from modules.dispatcher.src.root_dispatcher_container import DispatcherContainer

    router = RecordingActionRouter()
    container = DispatcherContainer(launcher_action_router=router)
    container.wire()

    exit_code = main(["--json", "delete-object", "--object-name", "Cube"], dispatcher=container.agent)

    assert exit_code == EXIT_VALIDATION  # nosec B101
    output = _json(capsys)
    assert output["category"] == "confirmation_error"  # nosec B101
    assert router.calls == []  # nosec B101


def test_destructive_command_forwards_confirmation(capsys) -> None:
    from modules.dispatcher.src.root_dispatcher_container import DispatcherContainer

    router = RecordingActionRouter()
    container = DispatcherContainer(launcher_action_router=router)
    container.wire()

    exit_code = main(["--json", "delete-object", "--object-name", "Cube", "--confirm"], dispatcher=container.agent)

    assert exit_code == 0  # nosec B101
    assert router.calls == [("delete_object", {"object_name": "Cube"})]  # nosec B101
    assert _json(capsys)["success"] is True  # nosec B101


def test_set_env_maps_to_render_action(capsys) -> None:
    dispatcher = RecordingDispatcher()
    assert (
        main(["--json", "setup-environment", "--hdri-id", "fixture.hdr", "--strength", "2.5"], dispatcher=dispatcher)
        == 0
    )  # nosec B101
    assert dispatcher.requests[0].action_name == "setup_environment"  # nosec B101
    assert dispatcher.requests[0].parameters == {"hdri_id": "fixture.hdr", "strength": 2.5}  # nosec B101
    assert _json(capsys)["success"] is True  # nosec B101


def test_place_asset_maps_transform_flags(capsys) -> None:
    dispatcher = RecordingDispatcher()
    assert (  # nosec B101
        main(
            [
                "--json",
                "place-asset",
                "--asset-id",
                "E2ECube",
                "--location",
                "1",
                "2",
                "3",
                "--rotation",
                "10",
                "20",
                "30",
                "--scale",
                "2",
                "2",
                "2",
            ],
            dispatcher=dispatcher,
        )
        == 0
    )
    assert dispatcher.requests[0].action_name == "place_asset"  # nosec B101
    assert dispatcher.requests[0].parameters == {  # nosec B101
        "asset_id": "E2ECube",
        "location": [1.0, 2.0, 3.0],
        "rotation": [10.0, 20.0, 30.0],
        "scale": [2.0, 2.0, 2.0],
    }
    assert _json(capsys)["success"] is True  # nosec B101


def test_cancel_task_requires_confirmation(capsys) -> None:
    from modules.dispatcher.src.root_dispatcher_container import DispatcherContainer

    router = RecordingActionRouter()
    container = DispatcherContainer(launcher_action_router=router)
    container.wire()
    assert main(["--json", "cancel-task", "--task-id", "task-001"], dispatcher=container.agent) == EXIT_VALIDATION  # nosec B101
    assert _json(capsys)["category"] == "confirmation_error"  # nosec B101
    assert router.calls == []  # nosec B101


def test_cancel_task_forwards_after_confirmation(capsys) -> None:
    from modules.dispatcher.src.root_dispatcher_container import DispatcherContainer

    router = RecordingActionRouter()
    container = DispatcherContainer(launcher_action_router=router)
    container.wire()
    assert main(["--json", "cancel-task", "--task-id", "task-001", "--confirm"], dispatcher=container.agent) == 0  # nosec B101
    assert router.calls == [("cancel_task", {"task_id": "task-001"})]  # nosec B101
    assert _json(capsys)["success"] is True  # nosec B101


def test_config_and_set_config_map_typed_json(capsys) -> None:
    dispatcher = RecordingDispatcher()
    assert main(["--json", "get-config", "--key", "blender.port"], dispatcher=dispatcher) == 0  # nosec B101
    assert dispatcher.requests[0].parameters == {"key": "blender.port"}  # nosec B101
    assert _json(capsys)["success"] is True  # nosec B101

    assert (  # nosec B101
        main(
            ["--json", "set-config", "--key", "blender.port", "--value", "9999", "--confirm"],
            dispatcher=dispatcher,
        )
        == 0
    )
    assert dispatcher.requests[-1].parameters == {"key": "blender.port", "value": "9999"}  # nosec B101
    assert dispatcher.requests[-1].confirmation_flag is True  # nosec B101
    assert _json(capsys)["success"] is True  # nosec B101


def test_camera_and_asset_commands_forward_contract_parameters(capsys) -> None:
    dispatcher = RecordingDispatcher()

    assert (
        main(
            [
                "--json",
                "configure-camera",
                "--focal-length",
                "55",
                "--sensor-fit",
                "AUTO",
                "--set-active",
                "--depth-of-field-enabled",
            ],
            dispatcher=dispatcher,
        )
        == 0
    )  # nosec B101
    assert _json(capsys)["success"] is True  # nosec B101
    camera_request = dispatcher.requests[-1]
    assert camera_request.action_name == "configure_camera"  # nosec B101
    assert camera_request.parameters["focal_length"] == 55.0  # nosec B101
    assert camera_request.parameters["set_active"] is True  # nosec B101

    assert (
        main(
            [
                "--json",
                "download-asset",
                "--provider",
                "Polyhaven",
                "--asset-id",
                "chair",
                "--asset-type",
                "model",
                "--cache-dir",
                ".cache/assets",
                "--max-size",
                "1000000",
            ],
            dispatcher=dispatcher,
        )
        == 0
    )  # nosec B101
    asset_request = dispatcher.requests[-1]
    assert asset_request.action_name == "download_asset"  # nosec B101
    assert asset_request.parameters["provider"] == "Polyhaven"  # nosec B101
    assert asset_request.parameters["max_size"] == 1000000  # nosec B101
    assert _json(capsys)["success"] is True  # nosec B101


def test_help_surface_has_valid_examples_and_safety_metadata() -> None:
    parser = _build_parser()
    root_help = parser.format_help()
    normalized_root_help = " ".join(root_help.split())

    assert "get-scene-info" in normalized_root_help  # nosec B101
    assert "[launcher] Start Blender with integration component active" in normalized_root_help  # nosec B101
    assert "shutdown-blender" in normalized_root_help  # nosec B101
    assert "cancel-task" in normalized_root_help  # nosec B101
    assert "set-config" in normalized_root_help  # nosec B101

    subparsers = next(action for action in parser._actions if isinstance(getattr(action, "choices", None), dict))
    action_help = subparsers.choices["get-scene-info"].format_help()
    shutdown_help = subparsers.choices["shutdown-blender"].format_help()
    set_config_help = subparsers.choices["set-config"].format_help()

    assert "--filepath FILEPATH" in action_help  # nosec B101
    assert "get-scene-info" in normalized_root_help  # nosec B101
    assert "launcher" in shutdown_help  # nosec B101
    assert "set-config" in set_config_help  # nosec B101


def test_cli_exposes_every_canonical_action_once() -> None:
    from modules.shared.src.dispatcher.taxonomy_dispatcher_constant import DISPATCHER_ACTION_SCHEMAS

    parser = _build_parser()
    subparsers = next(action for action in parser._actions if isinstance(getattr(action, "choices", None), dict))
    expected = {
        action.replace("_", "-") for owner_actions in DISPATCHER_ACTION_SCHEMAS.values() for action in owner_actions
    }
    assert len(expected) == 80  # nosec B101
    assert set(subparsers.choices) == expected  # nosec B101
    assert "run" not in subparsers.choices  # nosec B101
    assert "scene-info" not in subparsers.choices  # nosec B101
    assert "execute-blender-code" in subparsers.choices  # nosec B101
