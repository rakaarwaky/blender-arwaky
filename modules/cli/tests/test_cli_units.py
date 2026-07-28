"""Unit tests for the import-safe CLI module utilities.

These tests cover the stdlib-only, dependency-free helpers in
``modules/cli/src`` (registry state, socket framing, process helpers).
They establish a pytest baseline for the CLI module without depending on
the (currently absent) ``modules.shared`` contract/dependency layer that
the FRD-aligned capability/agent/container code requires.

NOTE: The legacy monolith files (``surface_cli_main``/``surface_cli_commands``
and their broken intra-module imports) are intentionally NOT exercised here;
they violate the CLI FRD scope and are tracked as findings in the review
plan/report.
"""

import os
import struct
import sys
from unittest import mock

import pytest

SRC = os.path.join(os.path.dirname(__file__), "..", "src")
if SRC not in sys.path:
    sys.path.insert(0, SRC)

import surface_cli_blender_manager as bm_mod  # noqa: E402
import surface_cli_registry as registry_mod  # noqa: E402
import surface_cli_socket_client as socket_mod  # noqa: E402


# ── Registry ────────────────────────────────────────────────────────────────
def test_registry_roundtrip(tmp_path):
    registry_mod.Registry.reset()
    path = str(tmp_path / "registry.json")
    reg = registry_mod.Registry(path)
    assert reg.is_active() is False

    reg.set_active("/tmp/scene.blend", 1234, 9876)
    assert reg.is_active() is True
    assert reg.get_active() == "/tmp/scene.blend"
    assert reg.get_pid() == 1234
    assert reg.get_port() == 9876

    # A fresh instance must reload persisted state from disk.
    reg2 = registry_mod.Registry(path)
    assert reg2.get_active() == "/tmp/scene.blend"
    assert reg2.get_pid() == 1234
    assert reg2.get_port() == 9876

    reg.clear()
    assert reg.is_active() is False
    registry_mod.Registry.reset()


def test_registry_assert_active(tmp_path):
    registry_mod.Registry.reset()
    reg = registry_mod.Registry(str(tmp_path / "r.json"))

    # No active instance -> error returned for an arbitrary entity.
    assert reg.assert_active("/tmp/x.blend") != ""
    # Matching active instance -> empty (no error).
    reg.set_active("/tmp/x.blend", 1, 2)
    assert reg.assert_active("/tmp/x.blend") == ""
    # Non-matching entity -> error.
    assert reg.assert_active("/tmp/other.blend") != ""
    registry_mod.Registry.reset()


def test_registry_assert_no_active(tmp_path):
    registry_mod.Registry.reset()
    reg = registry_mod.Registry(str(tmp_path / "r.json"))
    assert reg.assert_no_active() == ""
    reg.set_active("/tmp/x.blend", 1, 2)
    assert reg.assert_no_active() != ""
    registry_mod.Registry.reset()


# ── Socket framing ───────────────────────────────────────────────────────────
def test_socket_receive_response_framed():
    client = socket_mod.BlenderSocketClient(port=9876)
    payload = b'{"type": "ok", "result": {"x": 1}}'
    header = struct.pack("!I", len(payload))
    fake = mock.Mock()
    fake.recv = mock.Mock(side_effect=[header, payload])
    client._sock = fake

    out = client._receive_response()
    assert out == {"type": "ok", "result": {"x": 1}}


def test_socket_receive_oversize_rejected():
    client = socket_mod.BlenderSocketClient(port=9876)
    big_header = struct.pack("!I", socket_mod.MAX_MESSAGE_SIZE + 1)
    fake = mock.Mock()
    fake.recv = mock.Mock(return_value=big_header)
    client._sock = fake

    with pytest.raises(ValueError):
        client._receive_response()


def test_socket_send_command_requires_connection():
    client = socket_mod.BlenderSocketClient(port=9876)
    with pytest.raises(ConnectionError):
        client.send_command("ping", {})


# ── Process helpers ────────────────────────────────────────────────────────
def test_is_running_false_for_absent_pid():
    assert bm_mod.is_running(999999) is False


def test_kill_blender_false_for_absent_pid():
    assert bm_mod.kill_blender(999999) is False


def test_find_blender_raises_when_missing(monkeypatch):
    monkeypatch.delenv("BLENDER_EXECUTABLE", raising=False)
    with pytest.raises(FileNotFoundError):
        bm_mod.find_blender()
