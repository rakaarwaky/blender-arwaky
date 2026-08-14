"""T-05: stateless utility helpers (parse_env_value, overrides, yaml, schema, path)."""

from __future__ import annotations

import os
import tempfile

import pytest

from modules.shared.src.config.taxonomy_config_error import ConfigParseError
from modules.shared.src.config.utility_config_helpers import (
    apply_env_overrides,
    deep_merge_dicts,
    load_yaml_safe,
    parse_env_value,
    parse_settings_path,
    resolve_default_config_path,
    set_nested_value,
    validate_settings_schema,
)

# ─── parse_env_value (scalar-only, Q7) ───────────────────────


@pytest.mark.unit
@pytest.mark.parametrize(
    "raw,expected",
    [
        ("true", True),
        ("42", 42),
        ("3.14", 3.14),
        ("null", None),
        ('["a"]', '["a"]'),  # Q7 regression: list-looking stays string
    ],
)
def test_parse_env_value_scalar(raw, expected):
    assert parse_env_value(raw) == expected


# ─── apply_env_overrides ─────────────────────────────────────

@pytest.mark.unit
def test_apply_env_overrides_basic():
    config = {"blender": {"host": "localhost"}}
    environ = {
        "BLENDERMCP_BLENDER.PORT": "9999",
        "BLENDERMCP_SERVER.TRANSPORT": "ws",
        "BLENDERMCP_CONFIG_PATH": "/x",  # reserved, skipped
        "BLENDER_MCP_OLD": "1",  # legacy, not matched
    }
    result, count = apply_env_overrides(
        config, environ, "BLENDERMCP_", ("BLENDERMCP_CONFIG_PATH",)
    )
    assert result["blender"]["port"] == 9999
    assert result["server"]["transport"] == "ws"
    assert "config_path" not in result
    assert count == 2


@pytest.mark.unit
def test_apply_env_overrides_deterministic_and_no_mutation():
    base = {"a": 1}
    e1 = dict(sorted({"BLENDERMCP_X": "1", "BLENDERMCP_Y": "2"}.items()))
    e2 = dict(sorted({"BLENDERMCP_Y": "2", "BLENDERMCP_X": "1"}.items()))
    r1, _ = apply_env_overrides(base, e1, "BLENDERMCP_", ())
    r2, _ = apply_env_overrides(base, e2, "BLENDERMCP_", ())
    assert r1 == r2
    # inputs not mutated
    assert base == {"a": 1}


@pytest.mark.unit
def test_apply_env_overrides_introduces_new_keys():
    config: dict = {}
    result, count = apply_env_overrides(
        config, {"BLENDERMCP_NEW.KEY": "v"}, "BLENDERMCP_", ()
    )
    assert result["new"]["key"] == "v"
    assert count == 1


# ─── load_yaml_safe ──────────────────────────────────────────

@pytest.mark.unit
def test_load_yaml_safe_valid():
    d = tempfile.mkdtemp()
    p = os.path.join(d, "config.yaml")
    with open(p, "w") as f:
        f.write("blender:\n  port: 1234\n")
    assert load_yaml_safe(p) == {"blender": {"port": 1234}}


@pytest.mark.unit
def test_load_yaml_safe_empty():
    d = tempfile.mkdtemp()
    p = os.path.join(d, "config.yaml")
    open(p, "w").close()
    assert load_yaml_safe(p) == {}


@pytest.mark.unit
def test_load_yaml_safe_malformed():
    d = tempfile.mkdtemp()
    p = os.path.join(d, "config.yaml")
    with open(p, "w") as f:
        f.write("blender: [unclosed\n")
    with pytest.raises(ConfigParseError):
        load_yaml_safe(p)


@pytest.mark.unit
def test_load_yaml_safe_root_not_dict():
    d = tempfile.mkdtemp()
    p = os.path.join(d, "config.yaml")
    with open(p, "w") as f:
        f.write("- just\n- a\n- list\n")
    with pytest.raises(ConfigParseError):
        load_yaml_safe(p)


@pytest.mark.unit
def test_load_yaml_safe_bom():
    d = tempfile.mkdtemp()
    p = os.path.join(d, "config.yaml")
    with open(p, "wb") as f:
        f.write(b"\xef\xbb\xbfblender:\n  port: 1\n")
    assert load_yaml_safe(p) == {"blender": {"port": 1}}


@pytest.mark.unit
def test_load_yaml_safe_utf16_raises():
    d = tempfile.mkdtemp()
    p = os.path.join(d, "config.yaml")
    with open(p, "wb") as f:
        f.write("blender:\n  port: 1\n".encode("utf-16"))
    with pytest.raises(ConfigParseError):
        load_yaml_safe(p)


# ─── validate_settings_schema ───────────────────────────────

@pytest.mark.unit
def test_schema_unknown_key_warning():
    errors, warnings = validate_settings_schema(
        {"unknown": 1}, {"unknown": {"type": "int", "required": False}}
    )
    # 'unknown' IS in schema here; test real unknown:
    errors, warnings = validate_settings_schema({"foo": 1}, {})
    assert any("foo" in w for w in warnings)


@pytest.mark.unit
def test_schema_port_string_error():
    schema = {"blender": {"type": "dict", "required": False, "children": {"port": {"type": "int", "required": False}}}}
    errors, _ = validate_settings_schema({"blender": {"port": "x"}}, schema)
    assert any("expected int" in e for e in errors)


@pytest.mark.unit
def test_schema_bool_excluded_from_int():
    schema = {"blender": {"type": "dict", "required": False, "children": {"port": {"type": "int", "required": False}}}}
    errors, _ = validate_settings_schema({"blender": {"port": True}}, schema)
    assert any("expected int" in e for e in errors)


@pytest.mark.unit
def test_schema_clean_passes():
    schema = {"blender": {"type": "dict", "required": False, "children": {"port": {"type": "int", "required": False}}}}
    errors, warnings = validate_settings_schema({"blender": {"port": 9876}}, schema)
    assert errors == ()
    assert warnings == ()


# ─── parse_settings_path ─────────────────────────────────────

@pytest.mark.unit
def test_parse_settings_path_basic():
    assert parse_settings_path("a.b", False) == ("a", "b")
    assert parse_settings_path("a.b", True) == ("a", "b")


@pytest.mark.unit
def test_parse_settings_path_escape_on():
    assert parse_settings_path("a\\.b", True) == ("a.b",)


@pytest.mark.unit
def test_parse_settings_path_escape_off_literal_split():
    assert parse_settings_path("a\\.b", False) == ("a\\", "b")


@pytest.mark.unit
def test_parse_settings_path_empty():
    assert parse_settings_path("", True) == ()


# ─── deep_merge / set_nested ─────────────────────────────────

@pytest.mark.unit
def test_deep_merge_dicts():
    base = {"a": {"b": 1}, "x": 1}
    override = {"a": {"c": 2}, "x": 9}
    merged = deep_merge_dicts(base, override)
    assert merged == {"a": {"b": 1, "c": 2}, "x": 9}
    assert base == {"a": {"b": 1}, "x": 1}  # unchanged


@pytest.mark.unit
def test_deep_merge_list_replacement():
    merged = deep_merge_dicts({"a": [1, 2]}, {"a": [3]})
    assert merged["a"] == [3]


@pytest.mark.unit
def test_set_nested_value_creates_intermediates():
    target: dict = {}
    set_nested_value(target, ("a", "b", "c"), 5)
    assert target == {"a": {"b": {"c": 5}}}


# ─── resolve_default_config_path ─────────────────────────────

@pytest.mark.unit
def test_resolve_default_config_path_explicit(monkeypatch):
    monkeypatch.delenv("BLENDERMCP_CONFIG_PATH", raising=False)
    assert resolve_default_config_path("/tmp/my.yaml") == "/tmp/my.yaml"


@pytest.mark.unit
def test_resolve_default_config_path_env(monkeypatch):
    monkeypatch.setenv("BLENDERMCP_CONFIG_PATH", "/env/config.yaml")
    assert resolve_default_config_path(None) == "/env/config.yaml"


@pytest.mark.unit
def test_resolve_default_config_path_cwd(monkeypatch):
    monkeypatch.delenv("BLENDERMCP_CONFIG_PATH", raising=False)
    assert resolve_default_config_path(None).endswith("config.yaml")


@pytest.mark.unit
def test_resolve_default_config_path_xdg(monkeypatch, tmp_path):
    monkeypatch.delenv("BLENDERMCP_CONFIG_PATH", raising=False)
    xdg = tmp_path / "config"
    xdg.mkdir()
    monkeypatch.setenv("XDG_CONFIG_HOME", str(xdg))
    target = xdg / "blender-arwaky" / "config.yaml"
    target.parent.mkdir(parents=True)
    target.write_text("server:\n  transport: sse\n")
    monkeypatch.chdir(tmp_path)
    assert resolve_default_config_path(None) == str(target)


@pytest.mark.unit
def test_resolve_default_config_path_fallback_when_xdg_missing(monkeypatch, tmp_path):
    monkeypatch.delenv("BLENDERMCP_CONFIG_PATH", raising=False)
    xdg = tmp_path / "empty-config"
    xdg.mkdir()
    monkeypatch.setenv("XDG_CONFIG_HOME", str(xdg))
    cwd_cfg = tmp_path / "config.yaml"
    cwd_cfg.write_text("server:\n  transport: sse\n")
    monkeypatch.chdir(tmp_path)
    assert resolve_default_config_path(None) == str(cwd_cfg)
