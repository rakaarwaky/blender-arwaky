"""Utility: Config helper functions.

Stateless, domain-agnostic standalone functions extracted from capabilities.
No class, no protocol impl, pure functions only.
Only depends on Taxonomy + stdlib + yaml.
"""

from __future__ import annotations

import copy
import os
from pathlib import Path
from typing import Any, Mapping

import yaml

from modules.shared.src.common.taxonomy_core_vo import ConfigPath
from modules.shared.src.config.taxonomy_config_constant import (
    DEFAULT_CONFIG_FILENAME,
    RESERVED_ENV_KEYS,
)
from modules.shared.src.config.taxonomy_config_error import ConfigParseError


def parse_env_value(value: str) -> Any:
    """Parse environment value as typed scalar (scalar-only per Q7).

    boolean-like → bool, integer-like → int, float-like → float,
    null-like → None, otherwise → str. Lists/mappings are intentionally
    NOT parsed — they remain strings (Q7).
    """
    if value.lower() in ("true", "yes", "on"):
        return True
    if value.lower() in ("false", "no", "off"):
        return False
    try:
        return int(value)
    except ValueError:
        pass
    try:
        return float(value)
    except ValueError:
        pass
    if value.lower() in ("null", "none", ""):
        return None
    return value


def search_project_root(markers: tuple[str, ...]) -> Path | None:
    """Search upward from cwd for recognized project markers.

    Returns first parent containing any marker, or None.
    """
    current = Path.cwd().resolve()
    for parent in [current, *current.parents]:
        for marker in markers:
            candidate = parent / marker
            try:
                if candidate.exists():
                    return parent
            except OSError:
                continue
    return None


def resolve_default_config_path(explicit: ConfigPath | None = None) -> ConfigPath:
    """Resolve the config file path.

    Priority: explicit → env BLENDERMCPCONFIGPATH → cwd/config.yaml.
    """
    if explicit:
        return ConfigPath(str(explicit))
    env_path = os.environ.get("BLENDERMCPCONFIGPATH")
    if env_path:
        return ConfigPath(str(env_path))
    return ConfigPath(str(Path.cwd() / DEFAULT_CONFIG_FILENAME))


def load_yaml_safe(path: ConfigPath) -> dict[str, Any]:
    """Read a YAML file safely.

    Decode 'utf-8-sig' (BOM tolerated). UnicodeDecodeError → ConfigParseError.
    yaml.YAMLError → ConfigParseError. None → {}. Non-dict root → ConfigParseError.
    """
    raw = Path(str(path)).read_bytes()
    try:
        text = raw.decode("utf-8-sig")
    except UnicodeDecodeError as exc:
        raise ConfigParseError(f"Settings file is not valid UTF-8: {path}") from exc

    try:
        data = yaml.safe_load(text)
    except yaml.YAMLError as exc:
        raise ConfigParseError(f"Failed to parse settings YAML: {exc}") from exc

    if data is None:
        return {}
    if not isinstance(data, dict):
        raise ConfigParseError(f"Settings root must be a mapping, got {type(data).__name__}: {path}")
    return data


def deep_merge_dicts(base: dict[str, Any], override: dict[str, Any]) -> dict[str, Any]:
    """Recursively merge ``override`` into a copy of ``base``.

    Dict + dict recurses; override wins otherwise. Inputs never mutated.
    """
    result: dict[str, Any] = copy.deepcopy(base)
    for key, value in override.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = deep_merge_dicts(result[key], value)
        else:
            result[key] = copy.deepcopy(value)
    return result


def set_nested_value(target: dict[str, Any], segments: tuple[str, ...], value: Any) -> None:
    """Set ``value`` at dotted ``segments`` inside ``target`` in place.

    Creates intermediate dicts for missing/non-dict nodes.
    """
    if not segments:
        return
    node = target
    for segment in segments[:-1]:
        existing = node.get(segment)
        if not isinstance(existing, dict):
            existing = {}
            node[segment] = existing
        node = existing
    node[segments[-1]] = copy.deepcopy(value)


def apply_env_overrides(
    config: dict[str, Any],
    environ: Mapping[str, str],
    prefix: str,
    reserved: tuple[str, ...],
) -> tuple[dict[str, Any], int]:
    """Apply environment variable overrides with nested key convention.

    Iterates sorted(environ.items()) for determinism. Skips reserved keys and
    keys whose remainder after prefix is empty. Lowercases remainder, splits on
    '.', creates intermediates (env may introduce new keys). Returns
    (newdict, applied_count). Inputs not mutated.
    """
    result = copy.deepcopy(config)
    applied = 0

    for key in sorted(environ.keys()):
        if key in reserved:
            continue
        if not key.startswith(prefix):
            continue
        remainder = key[len(prefix):]
        if not remainder:
            continue
        remainder = remainder.lower()
        segments = tuple(remainder.split("."))
        set_nested_value(result, segments, parse_env_value(environ[key]))
        applied += 1

    return result, applied


def validate_settings_schema(
    data: dict[str, Any],
    schema: dict[str, Any],
) -> tuple[tuple[str, ...], tuple[str, ...]]:
    """Validate ``data`` against a Python-native schema.

    Returns (errors, warnings). ``int`` type excludes bool.
    """
    errors: list[str] = []
    warnings: list[str] = []

    def walk(node: Any, node_schema: dict[str, Any], path: str) -> None:
        node_type = node_schema.get("type", "any")
        required = node_schema.get("required", False)

        if node is None:
            if required:
                errors.append(f"{path}: missing required value")
            return

        if node_type == "dict":
            if not isinstance(node, dict):
                errors.append(f"{path}: expected dict, got {type(node).__name__}")
                return
            children = node_schema.get("children", {})
            for child_key, child_node in node.items():
                child_schema = children.get(child_key)
                if child_schema is None:
                    warnings.append(f"{path}.{child_key}: unknown key")
                    continue
                walk(child_node, child_schema, f"{path}.{child_key}")
            return

        if node_type == "int":
            if isinstance(node, bool) or not isinstance(node, int):
                errors.append(f"{path}: expected int, got {type(node).__name__}")
            return

        if node_type == "str":
            if not isinstance(node, str):
                errors.append(f"{path}: expected str, got {type(node).__name__}")
            return

        if node_type == "float":
            if isinstance(node, bool) or not isinstance(node, (int, float)):
                errors.append(f"{path}: expected float, got {type(node).__name__}")
            return

        if node_type == "bool":
            if not isinstance(node, bool):
                errors.append(f"{path}: expected bool, got {type(node).__name__}")
            return

        if node_type == "list":
            if not isinstance(node, list):
                errors.append(f"{path}: expected list, got {type(node).__name__}")
            return

        # "any" or unknown: no type check
        return

    for key, value in data.items():
        key_schema = schema.get(key)
        if key_schema is None:
            warnings.append(f"{key}: unknown key")
            continue
        walk(value, key_schema, key)

    return tuple(errors), tuple(warnings)


def parse_settings_path(path: str, escape_enabled: bool) -> tuple[str, ...]:
    """Split a dotted path into segments.

    When ``escape_enabled``, '\\.' yields a literal '.' inside a segment.
    Empty path → (). Trailing/leading/repeated separators produce empty
    segments which resolve as missing keys (returns default).
    """
    if not path:
        return ()

    if not escape_enabled:
        return tuple(path.split("."))

    segments: list[str] = []
    current = ""
    i = 0
    while i < len(path):
        ch = path[i]
        if ch == "\\" and i + 1 < len(path) and path[i + 1] == ".":
            current += "."
            i += 2
            continue
        if ch == ".":
            segments.append(current)
            current = ""
            i += 1
            continue
        current += ch
        i += 1
    segments.append(current)
    return tuple(segments)
