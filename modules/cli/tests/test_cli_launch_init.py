"""Unit tests for surface_init_command and surface_launch_command."""

from __future__ import annotations

import argparse
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from modules.cli.src import surface_init_command, surface_launch_command
from modules.shared.src.cli.capabilities_cli_registry import Registry


@pytest.fixture(autouse=True)
def clean_registry():
    Registry.reset()
    reg_file = Path("registry.json")
    if reg_file.exists():
        reg_file.unlink(missing_ok=True)
    yield
    Registry.reset()
    if reg_file.exists():
        reg_file.unlink(missing_ok=True)


def test_init_creates_workspace_directories_and_skills(tmp_path: Path):
    args = argparse.Namespace(target_dir=str(tmp_path), force=False, filepath=None)
    res = surface_init_command.handle(args)

    assert res["success"] is True
    assert (tmp_path / ".agents" / "skills" / "blender-arwaky" / "SKILL.md").exists()
    assert (tmp_path / "renders").exists()
    assert (tmp_path / "assets").exists()


def test_init_with_filepath_delegates_to_launch(tmp_path: Path):
    scene = tmp_path / "scene.blend"
    scene.touch()
    args = argparse.Namespace(filepath=str(scene), mode="headless", port=9876)

    with patch("modules.cli.src.surface_launch_command.launch_blender") as mock_launch:
        mock_res = MagicMock()
        mock_res.success = True
        mock_res.data = {"pid": 5678}
        mock_res.message = "Launched mock"
        mock_launch.return_value = mock_res

        res = surface_init_command.handle(args)
        assert res["success"] is True
        assert res["pid"] == 5678
        mock_launch.assert_called_once()


def test_launch_requires_filepath():
    args = argparse.Namespace(filepath=None, mode="headless", port=9876)
    res = surface_launch_command.handle(args)

    assert res["success"] is False
    assert res["category"] == "validation_error"


def test_launch_starts_blender_and_records_registry(tmp_path: Path):
    scene_file = tmp_path / "test.blend"
    scene_file.touch()

    args = argparse.Namespace(filepath=str(scene_file), mode="headless", port=9999)

    with patch("modules.cli.src.surface_launch_command.launch_blender") as mock_launch:
        mock_res = MagicMock()
        mock_res.success = True
        mock_res.data = {"pid": 4321}
        mock_res.message = "Started successfully"
        mock_launch.return_value = mock_res

        res = surface_launch_command.handle(args)
        assert res["success"] is True
        assert res["pid"] == 4321
        assert res["port"] == 9999

        reg = Registry()
        assert reg.is_active() is True
        assert reg.get_active() == str(scene_file.resolve())
