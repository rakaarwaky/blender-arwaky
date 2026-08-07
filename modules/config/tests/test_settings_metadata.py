"""T-08: SettingsMetadataCapability — supplier wiring, None supplier, to_safe_dict, secret leak."""

from __future__ import annotations

import pytest

from modules.config.src.capabilities_settings_metadata import SettingsMetadataCapability
from modules.shared.src.common.taxonomy_core_vo import ConfigMetadata
from modules.shared.src.config.taxonomy_config_constant import SENSITIVE_KEY_PATTERNS


@pytest.mark.unit
def test_none_supplier_returns_empty():
    cap = SettingsMetadataCapability()
    assert cap.get_metadata() == ConfigMetadata()


@pytest.mark.unit
def test_supplier_called_reflects_reload():
    state = {"n": 0}

    def supplier():
        state["n"] += 1
        return ConfigMetadata(overrides=state["n"])

    cap = SettingsMetadataCapability(metadata_supplier=supplier)
    assert cap.get_metadata().overrides == 1
    assert cap.get_metadata().overrides == 2  # supplier called per request


@pytest.mark.unit
def test_to_safe_dict_keys():
    md = ConfigMetadata(source="p", exists=True, overrides=3)
    d = SettingsMetadataCapability().to_safe_dict(md)
    assert set(d.keys()) == {
        "source",
        "exists",
        "overrides",
        "parse_warnings",
        "validation_warnings",
    }
    assert d["overrides"] == 3


@pytest.mark.unit
def test_no_secret_values_in_safe_dict():
    md = ConfigMetadata(source="config.yaml", overrides=0)
    d = SettingsMetadataCapability().to_safe_dict(md)
    # structural: only counts + source path, never raw values
    assert "password" not in str(d)


@pytest.mark.unit
def test_safe_dict_no_sensitive_pattern_leakage():
    """to_safe_dict output must not contain any literal sensitive key pattern
    from SENSITIVE_KEY_PATTERNS — verifying all patterns, not just 'password'."""
    md = ConfigMetadata(source="config.yaml", exists=True, overrides=3)
    d = SettingsMetadataCapability().to_safe_dict(md)
    serialized = str(d).lower()
    for pattern in SENSITIVE_KEY_PATTERNS:
        assert pattern.lower() not in serialized, (
            f"Sensitive pattern '{pattern}' leaked in safe_dict output: {d}"
        )
