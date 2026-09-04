"""T-07: SettingsRetrieverCapability — policy mode, escaped separator, typed getters."""

from __future__ import annotations

import pytest

from modules.config.src.capabilities_settings_retriever import SettingsRetrieverCapability
from modules.shared.src.config.taxonomy_config_error import ConfigTypeError
from modules.shared.src.config.taxonomy_config_vo import SettingsSnapshot


def _retriever(mode="strict"):
    return SettingsRetrieverCapability(policy_mode=mode)


def _snap():
    return SettingsSnapshot(
        _data={"a": {"b": 1}, "port": 9876, "flag": True, "name": "x", "floaty": 3.5, "dotted": {"a.b": 1}}
    )


@pytest.mark.unit
def test_missing_key_never_raises_either_mode():
    r = _retriever("strict")
    assert r.get_int(_snap(), "nope") == 0
    r2 = _retriever("permissive")
    assert r2.get_int(_snap(), "nope") == 0


@pytest.mark.unit
def test_mismatch_strict_raises():
    r = _retriever("strict")
    with pytest.raises(ConfigTypeError):
        r.get_int(_snap(), "name")  # name is str


@pytest.mark.unit
def test_mismatch_permissive_returns_default():
    r = _retriever("permissive")
    assert r.get_int(_snap(), "name") == 0


@pytest.mark.unit
def test_bool_not_accepted_by_get_int():
    r = _retriever("strict")
    with pytest.raises(ConfigTypeError):
        r.get_int(_snap(), "flag")


@pytest.mark.unit
def test_get_float_coerces_int():
    r = _retriever("strict")
    assert r.get_float(_snap(), "port") == 9876.0


@pytest.mark.unit
def test_get_string_returns_value():
    r = _retriever("strict")
    assert r.get_string(_snap(), "name") == "x"


@pytest.mark.unit
def test_escaped_dot_is_always_supported():
    snap = SettingsSnapshot(_data={"a.b": 1})
    r = _retriever("strict")
    assert r.get_value(snap, "a\\.b") == 1


@pytest.mark.unit
def test_dotted_path_still_splits_unescaped_separator():
    r = _retriever("strict")
    assert r.get_value(_snap(), "a.b") == 1


@pytest.mark.unit
def test_all_four_getters_modes():
    snap = _snap()
    for mode in ("strict", "permissive"):
        r = _retriever(mode)
        assert r.get_string(snap, "name") == "x"
        assert r.get_int(snap, "port") == 9876
        assert r.get_bool(snap, "flag") is True
        assert r.get_float(snap, "floaty") == 3.5
