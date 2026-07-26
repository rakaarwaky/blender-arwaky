"""T-08: SettingsMetadataCapability — supplier wiring, None supplier, to_safe_dict."""

from __future__ import annotations

import pytest

from modules.shared.src.common.taxonomy_core_vo import ConfigMetadata
from modules.config.src.capabilities_settings_metadata import SettingsMetadataCapability


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
