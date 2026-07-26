"""T-04: SettingsSnapshot segment traversal, escaping delegation, list regression."""

from __future__ import annotations

import pytest

from modules.shared.src.config.taxonomy_config_vo import SettingsSnapshot


def _snap():
    return SettingsSnapshot(
        _data={
            "a": {"b": {"c": 1}},
            "list": [10, 20, 30],
            "val": "x",
        }
    )


@pytest.mark.unit
def test_nested_get():
    s = _snap()
    assert s.get("a.b.c") == 1
    assert s.get("val") == "x"


@pytest.mark.unit
def test_list_index_get():
    s = _snap()
    assert s.get("list.1") == 20


@pytest.mark.unit
def test_out_of_range_returns_default_regression():
    s = _snap()
    # previously a bug: out-of-range index continued traversal with default as node
    assert s.get("list.99") is None
    assert s.get("list.99", "def") == "def"
    assert s.has("list.99") is False


@pytest.mark.unit
def test_list_index_as_node_not_traversed_as_dict():
    # list element is int, not a dict; further segments must not match
    s = _snap()
    assert s.get("list.0.c") is None
    assert s.has("list.0.c") is False


@pytest.mark.unit
def test_empty_path_returns_full_deepcopy():
    s = _snap()
    full = s.get("")
    assert full == s.to_dict()
    assert full is not s.to_dict()  # fresh deep copy each call
    full["a"]["b"]["c"] = 999
    assert s.get("a.b.c") == 1  # mutation of returned dict does not affect snapshot


@pytest.mark.unit
def test_has_parity():
    s = _snap()
    assert s.has("a.b.c")
    assert not s.has("a.b.missing")
    assert not s.has("a.b.c.deep")


@pytest.mark.unit
def test_get_segments_and_has_segments():
    s = _snap()
    assert s.get_segments(("a", "b", "c")) == 1
    assert s.has_segments(("a", "b")) is True
    assert s.has_segments(("nope",)) is False


@pytest.mark.unit
def test_returned_dict_is_deepcopy():
    s = SettingsSnapshot(_data={"nested": {"k": 1}})
    got = s.get("nested")
    got["k"] = 2
    assert s.get("nested")["k"] == 1