from __future__ import annotations

import pytest

from modules.config.src.root_config_container import ConfigContainer
from modules.shared.src.config.taxonomy_config_error import ConfigValidationError
from modules.shared.src.common.taxonomy_core_vo import ConfigPath


def test_set_config_persists_typed_value_atomically(tmp_path, monkeypatch) -> None:
    config_path = tmp_path / "config.yaml"
    monkeypatch.setenv("BLENDERMCP_CONFIG_PATH", str(config_path))

    aggregate = ConfigContainer().build()
    snapshot = aggregate.set_config(ConfigPath("blender.port"), 9999)

    assert snapshot.get("blender.port") == 9999  # nosec B101
    assert config_path.exists()  # nosec B101
    assert "9999" in config_path.read_text(encoding="utf-8")  # nosec B101
    assert not list(tmp_path.glob("*.tmp"))  # nosec B101

    reloaded = ConfigContainer().build()
    assert reloaded.get("blender.port") == 9999  # nosec B101


def test_set_config_rejects_wrong_schema_type(tmp_path, monkeypatch) -> None:
    monkeypatch.setenv("BLENDERMCP_CONFIG_PATH", str(tmp_path / "config.yaml"))
    aggregate = ConfigContainer().build()

    with pytest.raises(ConfigValidationError):
        aggregate.set_config(ConfigPath("blender.port"), "not-an-int")


def test_set_config_rejects_secret_like_keys(tmp_path, monkeypatch) -> None:
    monkeypatch.setenv("BLENDERMCP_CONFIG_PATH", str(tmp_path / "config.yaml"))
    aggregate = ConfigContainer().build()

    with pytest.raises(ConfigValidationError, match="Secret-like"):
        aggregate.set_config(ConfigPath("server.api_key"), "super-secret")


def test_config_redacts_secret_values(tmp_path, monkeypatch) -> None:
    config_path = tmp_path / "config.yaml"
    config_path.write_text("server:\n  token: super-secret\n", encoding="utf-8")
    monkeypatch.setenv("BLENDERMCP_CONFIG_PATH", str(config_path))
    aggregate = ConfigContainer().build()

    redacted = aggregate.redact_dict(aggregate.get_snapshot().to_dict())
    assert redacted["server"]["token"] == "***REDACTED***"  # nosec B101
    assert "super-secret" not in str(redacted)  # nosec B101
