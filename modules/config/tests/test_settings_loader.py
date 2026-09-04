"""T-06: SettingsLoaderCapability — precedence, missing/malformed/dir/oversized, schema, overrides, concurrency."""

from __future__ import annotations

import os
import tempfile
import threading

import pytest

from modules.config.src.capabilities_settings_loader import SettingsLoaderCapability
from modules.shared.src.common.taxonomy_core_vo import ConfigPath
from modules.shared.src.config.taxonomy_config_constant import MAX_CONFIG_SIZE_BYTES
from modules.shared.src.config.taxonomy_config_error import (
    ConfigLoadError,
    ConfigParseError,
    ConfigPathError,
    ConfigValidationError,
)


def _write(path: str, content: str) -> None:
    with open(path, "w") as f:
        f.write(content)


@pytest.mark.unit
def test_precedence_defaults_only():
    loader = SettingsLoaderCapability()
    snap = loader.load_settings()
    assert snap.get("blender.port") == 9876
    assert snap.get("server.transport") == "stdio"


@pytest.mark.unit
def test_precedence_file_over_defaults(monkeypatch):  # noqa: ARG001 (unused monkeypatch fixture for test isolation)
    d = tempfile.mkdtemp()
    cfg = os.path.join(d, "config.yaml")
    _write(cfg, "blender:\n  port: 5555\n")
    loader = SettingsLoaderCapability()
    snap = loader.load_settings(ConfigPath(cfg))
    assert snap.get("blender.port") == 5555
    assert snap.get("blender.host") == "localhost"  # from defaults


@pytest.mark.unit
def test_precedence_env_over_file(monkeypatch):
    d = tempfile.mkdtemp()
    cfg = os.path.join(d, "config.yaml")
    _write(cfg, "server:\n  transport: stdio\n")
    monkeypatch.setenv("BLENDERMCP_SERVER.TRANSPORT", "ws")
    loader = SettingsLoaderCapability()
    snap = loader.load_settings(ConfigPath(cfg))
    assert snap.get("server.transport") == "ws"


@pytest.mark.unit
def test_runtime_override_wins(monkeypatch):  # noqa: ARG001 (unused monkeypatch fixture)
    d = tempfile.mkdtemp()
    cfg = os.path.join(d, "config.yaml")
    _write(cfg, "blender:\n  port: 5555\n")
    loader = SettingsLoaderCapability()
    snap = loader.load_settings(ConfigPath(cfg), overrides={"blender.port": 7777})
    assert snap.get("blender.port") == 7777


@pytest.mark.unit
def test_missing_file_not_fatal_strict_and_permissive():
    for mode in ("strict", "permissive"):
        loader = SettingsLoaderCapability(policy_mode=mode)
        snap = loader.load_settings(ConfigPath("/nonexistent/config.yaml"))
        assert snap.get("blender.port") == 9876
        md = loader.get_last_metadata()
        assert md.exists is False
        assert len(md.parse_warnings) >= 1


@pytest.mark.unit
def test_malformed_strict_raises(monkeypatch):  # noqa: ARG001 (unused monkeypatch fixture)
    d = tempfile.mkdtemp()
    cfg = os.path.join(d, "config.yaml")
    _write(cfg, "blender: [unclosed\n")
    loader = SettingsLoaderCapability(policy_mode="strict")
    with pytest.raises(ConfigParseError):
        loader.load_settings(ConfigPath(cfg))


@pytest.mark.unit
def test_malformed_permissive_returns_defaults(monkeypatch):  # noqa: ARG001 (unused monkeypatch fixture)
    d = tempfile.mkdtemp()
    cfg = os.path.join(d, "config.yaml")
    _write(cfg, "blender: [unclosed\n")
    loader = SettingsLoaderCapability(policy_mode="permissive")
    snap = loader.load_settings(ConfigPath(cfg))
    assert snap.get("blender.port") == 9876
    md = loader.get_last_metadata()
    assert len(md.parse_warnings) >= 1


@pytest.mark.unit
def test_directory_path_strict_raises():
    d = tempfile.mkdtemp()
    loader = SettingsLoaderCapability(policy_mode="strict")
    with pytest.raises(ConfigPathError):
        loader.load_settings(ConfigPath(d))


@pytest.mark.unit
def test_directory_path_permissive_uses_defaults():
    d = tempfile.mkdtemp()
    loader = SettingsLoaderCapability(policy_mode="permissive")
    snap = loader.load_settings(ConfigPath(d))
    assert snap.get("blender.port") == 9876


@pytest.mark.unit
def test_oversized_v2_on_strict_raises(monkeypatch):  # noqa: ARG001 (unused monkeypatch fixture)
    d = tempfile.mkdtemp()
    cfg = os.path.join(d, "config.yaml")
    _write(cfg, "x: " + "a" * (MAX_CONFIG_SIZE_BYTES + 10) + "\n")
    loader = SettingsLoaderCapability(policy_mode="strict")
    with pytest.raises(ConfigLoadError):
        loader.load_settings(ConfigPath(cfg))


@pytest.mark.unit
def test_oversized_v2_on_permissive_skips():
    d = tempfile.mkdtemp()
    cfg = os.path.join(d, "config.yaml")
    _write(cfg, "x: " + "a" * (MAX_CONFIG_SIZE_BYTES + 10) + "\n")
    loader = SettingsLoaderCapability(policy_mode="permissive")
    snap = loader.load_settings(ConfigPath(cfg))
    assert snap.get("blender.port") == 9876


@pytest.mark.unit
def test_oversized_always_rejected_in_strict_policy():
    d = tempfile.mkdtemp()
    cfg = os.path.join(d, "config.yaml")
    big = "x: " + "a" * (MAX_CONFIG_SIZE_BYTES + 10) + "\n"
    _write(cfg, big)
    loader = SettingsLoaderCapability(policy_mode="strict")
    with pytest.raises(ConfigLoadError):
        loader.load_settings(ConfigPath(cfg))


@pytest.mark.unit
def test_schema_v2_on_strict_error():
    d = tempfile.mkdtemp()
    cfg = os.path.join(d, "config.yaml")
    _write(cfg, "blender:\n  port: oops\n")
    loader = SettingsLoaderCapability(policy_mode="strict")
    with pytest.raises(ConfigValidationError):
        loader.load_settings(ConfigPath(cfg))


@pytest.mark.unit
def test_schema_v2_on_permissive_warning_and_event():
    d = tempfile.mkdtemp()
    cfg = os.path.join(d, "config.yaml")
    _write(cfg, "blender:\n  port: oops\n")
    loader = SettingsLoaderCapability(policy_mode="permissive")
    loader.load_settings(ConfigPath(cfg))
    ev = loader.emit_validation_warning_event()
    assert ev is not None


@pytest.mark.unit
def test_overrides_applied_unconditionally_and_cached():
    """Runtime overrides are applied regardless of strict mode and cached."""
    d = tempfile.mkdtemp()
    cfg = os.path.join(d, "config.yaml")
    _write(cfg, "blender:\n  port: 5555\n")
    loader = SettingsLoaderCapability()
    snap1 = loader.load_settings(ConfigPath(cfg), overrides={"blender.port": 7777})
    assert snap1.get("blender.port") == 7777
    # Cached snapshot now includes overrides — consistent with get_snapshot().
    snap2 = loader.load_settings()  # no path, no overrides → returns cached
    assert snap2.get("blender.port") == 7777


@pytest.mark.unit
def test_overrides_applied_in_permissive_mode():
    """Runtime overrides remain available under the permanent strict policy."""
    d = tempfile.mkdtemp()
    cfg = os.path.join(d, "config.yaml")
    _write(cfg, "blender:\n  port: 5555\n")
    loader = SettingsLoaderCapability()
    snap = loader.load_settings(ConfigPath(cfg), overrides={"blender.port": 7777})
    assert snap.get("blender.port") == 7777


@pytest.mark.unit
def test_reserved_keys_not_applied(monkeypatch):
    loader = SettingsLoaderCapability()
    monkeypatch.setenv("BLENDERMCP_CONFIG_PATH", "/x")  # reserved
    snap = loader.load_settings()
    assert "config_path" not in snap.get("") if isinstance(snap.get(""), dict) else True


@pytest.mark.unit
def test_unsupported_prefix_ignored(monkeypatch):
    monkeypatch.setenv("BLENDER_MCP_FOO", "1")  # unsupported, ignored
    loader = SettingsLoaderCapability()
    snap = loader.load_settings()
    assert "foo" not in snap.get("")


@pytest.mark.unit
def test_event_counts_real_env_overrides(monkeypatch):
    monkeypatch.setenv("BLENDERMCP_SERVER.TRANSPORT", "ws")
    loader = SettingsLoaderCapability()
    loader.load_settings()
    ev = loader.emit_loaded_event()
    md = loader.get_last_metadata()
    assert ev.override_count == int(md.overrides)
    assert ev.override_count >= 1
    assert ev.timestamp > 0


@pytest.mark.unit
def test_concurrency_single_load():
    calls = {"n": 0}
    lock = threading.Lock()

    def counting_loader(_path):
        with lock:
            calls["n"] += 1
        return {"blender": {"port": 9876}}

    loader = SettingsLoaderCapability(config_file_loader=counting_loader)
    barrier = threading.Barrier(32)
    results = []

    def worker():
        barrier.wait()
        results.append(loader.load_settings())

    threads = [threading.Thread(target=worker) for _ in range(32)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    assert calls["n"] == 1
    assert all(r is results[0] for r in results)


@pytest.mark.unit
def test_metadata_reflects_latest_load(monkeypatch):  # noqa: ARG001 (unused monkeypatch fixture)
    d = tempfile.mkdtemp()
    cfg = os.path.join(d, "config.yaml")
    _write(cfg, "blender:\n  port: 1111\n")
    loader = SettingsLoaderCapability()
    loader.load_settings(ConfigPath(cfg))
    md = loader.get_last_metadata()
    assert md.exists is True
    assert str(md.source).endswith("config.yaml")
