from __future__ import annotations

import json
import sys
from pathlib import Path

from modules.launcher.src.root_launcher_container import LauncherContainer
from modules.shared.src.launcher.taxonomy_launcher_vo import LauncherConfigVO


def test_container_register_persists_executable_path(tmp_path) -> None:
    state_path = tmp_path / "launcher-state.json"
    container = LauncherContainer(config=LauncherConfigVO(), state_path=str(state_path))
    container.wire()

    executable_path = str(Path(sys.executable).resolve())
    result = container.agent.locate_and_register(LauncherConfigVO(), executable_path)

    assert result.registered is True  # nosec B101
    payload = json.loads(state_path.read_text())
    assert payload["executable_path"] == executable_path  # nosec B101
