from unittest import mock

from modules.shared.src.dispatcher.taxonomy_action_command_vo import ActionCommandVO
from modules.shared.src.dispatcher.taxonomy_unified_result_envelope_vo import UnifiedResultEnvelopeVO
from modules.shared.src.launcher.taxonomy_launcher_vo import (
    LaunchOutcomeVO,
    RuntimeState,
    RuntimeStatusVO,
    ShutdownOutcomeVO,
)


class FakeArgs:
    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)


class TestInitCommand:
    def test_launch_success(self):
        from modules.cli.src.surface_init_command import handle

        launcher = mock.Mock()
        launcher.launch.return_value = LaunchOutcomeVO(success=True, process_id=1234, bridge_endpoint="localhost:9876")
        args = FakeArgs(mode="headless", filepath="/tmp/test.blend", port=9876, timeout=30)
        result = handle(args, launcher=launcher)
        assert result.success is True
        assert result.data["pid"] == 1234
        launcher.launch.assert_called_once()

    def test_launch_failure(self):
        from modules.cli.src.surface_init_command import handle

        launcher = mock.Mock()
        launcher.launch.return_value = LaunchOutcomeVO(success=False, error="Blender executable not found")
        args = FakeArgs(mode="headless", filepath="/tmp/test.blend", port=9876, timeout=30)
        result = handle(args, launcher=launcher)
        assert result.success is False
        assert "not found" in (result.error or "").lower()

    def test_no_launcher(self):
        from modules.cli.src.surface_init_command import handle

        args = FakeArgs(mode="headless", filepath="/tmp/test.blend", port=9876, timeout=30)
        result = handle(args, launcher=None)
        assert result.success is False
        assert result.category == "configuration_error"


class TestCloseCommand:
    def test_shutdown_success(self):
        from modules.cli.src.surface_close_command import handle

        launcher = mock.Mock()
        launcher.shutdown.return_value = ShutdownOutcomeVO(success=True)
        result = handle(FakeArgs(filepath="/tmp/test.blend"), launcher=launcher)
        assert result.success is True
        assert "closed" in (result.message or "").lower()
        launcher.shutdown.assert_called_once_with(force=False, allow_escalation=True)

    def test_shutdown_failure(self):
        from modules.cli.src.surface_close_command import handle

        launcher = mock.Mock()
        launcher.shutdown.return_value = ShutdownOutcomeVO(success=False, error="Process not found")
        result = handle(FakeArgs(filepath="/tmp/test.blend"), launcher=launcher)
        assert result.success is False

    def test_no_launcher(self):
        from modules.cli.src.surface_close_command import handle

        result = handle(FakeArgs(filepath="/tmp/test.blend"), launcher=None)
        assert result.success is False
        assert result.category == "configuration_error"


class TestStatusCommand:
    def test_status_running(self):
        from modules.cli.src.surface_status_command import handle

        launcher = mock.Mock()
        launcher.check_status.return_value = RuntimeStatusVO(state=RuntimeState.RUNNING_READY, process_id=1234, ready=True, stale=False)
        result = handle(FakeArgs(), launcher=launcher)
        assert result.success is True
        assert result.data["state"] == "running_ready"
        assert result.data["pid"] == 1234

    def test_status_not_running(self):
        from modules.cli.src.surface_status_command import handle

        launcher = mock.Mock()
        launcher.check_status.return_value = RuntimeStatusVO(state=RuntimeState.NOT_RUNNING)
        result = handle(FakeArgs(), launcher=launcher)
        assert result.success is True
        assert result.data["state"] == "not_running"

    def test_no_launcher(self):
        from modules.cli.src.surface_status_command import handle

        result = handle(FakeArgs(), launcher=None)
        assert result.success is False
        assert result.category == "configuration_error"


class TestRunCommand:
    def test_run_success(self):
        from modules.cli.src.surface_run_command import handle

        dispatcher = mock.Mock()
        dispatcher.execute_action.return_value = UnifiedResultEnvelopeVO(success=True, message="Action executed", tracking_id="tid-1")
        args = FakeArgs(action="get_scene_info", params={}, filepath="/tmp/test.blend")
        result = handle(args, dispatcher=dispatcher)
        assert result.success is True
        dispatcher.execute_action.assert_called_once()
        request = dispatcher.execute_action.call_args[0][0]
        assert isinstance(request, ActionCommandVO)
        assert request.action_name == "get_scene_info"

    def test_run_unknown_action(self):
        from modules.cli.src.surface_run_command import handle

        args = FakeArgs(action="nonexistent_action", params={}, filepath="/tmp/test.blend")
        result = handle(args, dispatcher=mock.Mock())
        assert result.success is False
        assert result.category == "validation_error"

    def test_run_missing_required_param(self):
        from modules.cli.src.surface_run_command import handle

        args = FakeArgs(action="delete_object", params={}, filepath="/tmp/test.blend")
        result = handle(args, dispatcher=mock.Mock())
        assert result.success is False
        assert result.category == "validation_error"
        assert "missing" in (result.error or "").lower()

    def test_no_dispatcher(self):
        from modules.cli.src.surface_run_command import handle

        args = FakeArgs(action="get_scene_info", params={}, filepath="/tmp/test.blend")
        result = handle(args, dispatcher=None)
        assert result.success is False
        assert result.category == "configuration_error"


class TestScreenshotCommand:
    def test_screenshot_success(self):
        from modules.cli.src.surface_screenshot_command import handle

        dispatcher = mock.Mock()
        dispatcher.execute_action.return_value = UnifiedResultEnvelopeVO(success=True, message="Screenshot saved", tracking_id="tid-2")
        args = FakeArgs(output="/tmp/screenshot.png", max_size=800, view_angle="PERSPECTIVE", shading="MATERIAL", no_overlays=False, focus_object=None)
        result = handle(args, dispatcher=dispatcher)
        assert result.success is True
        assert result.data["filepath"] == "/tmp/screenshot.png"

    def test_screenshot_failure(self):
        from modules.cli.src.surface_screenshot_command import handle

        dispatcher = mock.Mock()
        dispatcher.execute_action.return_value = UnifiedResultEnvelopeVO(success=False, message="Blender not responding", tracking_id="tid-2", error_category="connection_error")
        args = FakeArgs(output="/tmp/screenshot.png", max_size=800, view_angle="PERSPECTIVE", shading="MATERIAL", no_overlays=False, focus_object=None)
        result = handle(args, dispatcher=dispatcher)
        assert result.success is False

    def test_no_dispatcher(self):
        from modules.cli.src.surface_screenshot_command import handle

        args = FakeArgs(output="/tmp/screenshot.png", max_size=800, view_angle="PERSPECTIVE", shading="MATERIAL", no_overlays=False)
        result = handle(args, dispatcher=None)
        assert result.success is False
        assert result.category == "configuration_error"


class TestRenderCommand:
    def test_render_success(self):
        from modules.cli.src.surface_render_command import handle

        dispatcher = mock.Mock()
        dispatcher.execute_action.return_value = UnifiedResultEnvelopeVO(success=True, message="Render started", tracking_id="tid-3")
        args = FakeArgs(output="/tmp/render.png", resolution_x=1920, resolution_y=1080, filepath="/tmp/test.blend")
        result = handle(args, dispatcher=dispatcher)
        assert result.success is True
        assert result.data["filepath"] == "/tmp/render.png"

    def test_render_failure(self):
        from modules.cli.src.surface_render_command import handle

        dispatcher = mock.Mock()
        dispatcher.execute_action.return_value = UnifiedResultEnvelopeVO(success=False, message="Render engine not available", tracking_id="tid-3", error_category="execution_error")
        args = FakeArgs(output="/tmp/render.png", resolution_x=1920, resolution_y=1080, filepath="/tmp/test.blend")
        result = handle(args, dispatcher=dispatcher)
        assert result.success is False

    def test_no_dispatcher(self):
        from modules.cli.src.surface_render_command import handle

        args = FakeArgs(output="/tmp/render.png", resolution_x=1920, resolution_y=1080)
        result = handle(args, dispatcher=None)
        assert result.success is False
        assert result.category == "configuration_error"


class TestMainEntry:
    def test_unknown_command_suggestion(self):
        from modules.cli.src.root_cli_main_entry import main

        exit_code = main(["int"], launcher=mock.Mock(), dispatcher=mock.Mock())
        assert exit_code == 2

    def test_help_exit_code(self):
        from modules.cli.src.root_cli_main_entry import main

        exit_code = main([], launcher=mock.Mock(), dispatcher=mock.Mock())
        assert exit_code == 2

    def test_init_via_main_success(self):
        from modules.cli.src.root_cli_main_entry import main

        launcher = mock.Mock()
        launcher.launch.return_value = LaunchOutcomeVO(success=True, process_id=1234)
        exit_code = main(["init", "--filepath", "/tmp/test.blend", "--mode", "headless"], launcher=launcher)
        assert exit_code == 0

    def test_init_via_main_failure(self):
        from modules.cli.src.root_cli_main_entry import main

        launcher = mock.Mock()
        launcher.launch.return_value = LaunchOutcomeVO(success=False, error="timeout")
        exit_code = main(["init", "--filepath", "/tmp/test.blend", "--mode", "headless"], launcher=launcher)
        assert exit_code != 0

    def test_exit_code_mapping(self):
        from modules.cli.src.root_cli_main_entry import _exit_code

        assert _exit_code({"success": True}) == 0
        assert _exit_code({"success": False, "category": "validation_error"}) == 2
        assert _exit_code({"success": False, "category": "connection"}) == 3
        assert _exit_code({"success": False, "category": "unexpected"}) == 4
