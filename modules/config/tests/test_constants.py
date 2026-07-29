"""T-01/T-02: constants, defaults, schema, and frozen ConfigMetadata VO."""

from __future__ import annotations

from dataclasses import FrozenInstanceError

import pytest

from modules.shared.src.common.taxonomy_core_vo import ConfigMetadata
from modules.shared.src.config import (
    DEFAULT_POLICY_MODE,
    DEFAULT_SETTINGS,
    ENV_PREFIX_PRODUCT,
    EVENT_RING_BUFFER_SIZE,
    POLICY_MODE_PERMISSIVE,
    POLICY_MODE_STRICT,
    PROJECT_MARKERS,
    RESERVED_ENV_KEYS,
    SETTINGS_SCHEMA,
    WORKSPACE_ROOT_ENV,
)


@pytest.mark.unit
def test_defaults_match_readme_sample():
    assert DEFAULT_SETTINGS["blender"]["port"] == 9876
    assert DEFAULT_SETTINGS["server"]["transport"] == "stdio"
    assert DEFAULT_SETTINGS["blender"]["host"] == "localhost"


@pytest.mark.unit
def test_breaking_legacy_removed():
    with pytest.raises(ImportError):
        from modules.shared.src.config.taxonomy_config_constant import ENV_PREFIX_LEGACY  # noqa: F401


@pytest.mark.unit
def test_project_markers_order_manifest_before_vcs():
    assert PROJECT_MARKERS.index("pyproject.toml") < PROJECT_MARKERS.index(".git")


@pytest.mark.unit
def test_policy_mode_constants():
    assert POLICY_MODE_STRICT == "strict"
    assert POLICY_MODE_PERMISSIVE == "permissive"
    assert DEFAULT_POLICY_MODE == "strict"


@pytest.mark.unit
def test_env_names_and_reserved():
    assert ENV_PREFIX_PRODUCT == "BLENDERMCP_"
    assert WORKSPACE_ROOT_ENV == "BLENDERMCP_ROOT"
    assert "BLENDERMCP_CONFIG_PATH" in RESERVED_ENV_KEYS
    assert EVENT_RING_BUFFER_SIZE == 50


@pytest.mark.unit
def test_schema_minimal_shape():
    assert SETTINGS_SCHEMA["blender"]["type"] == "dict"
    assert SETTINGS_SCHEMA["blender"]["children"]["port"]["type"] == "int"
    assert SETTINGS_SCHEMA["server"]["children"]["transport"]["type"] == "str"


@pytest.mark.unit
def test_config_metadata_frozen_and_hashable():
    md = ConfigMetadata(source="x", exists=True)
    with pytest.raises(FrozenInstanceError):
        md.exists = False  # type: ignore[misc]
    # hashable
    assert hash(md) is not None


@pytest.mark.unit
def test_config_metadata_to_dict_shape():
    md = ConfigMetadata(
        source="config.yaml",
        exists=True,
        overrides=2,
        parse_warnings=("w1",),
        validation_warnings=("w2",),
    )
    d = md.to_dict()
    assert d == {
        "source": "config.yaml",
        "exists": True,
        "overrides": 2,
        "parse_warnings": ["w1"],
        "validation_warnings": ["w2"],
    }


@pytest.mark.unit
def test_config_metadata_default_empty_tuples():
    md = ConfigMetadata()
    assert md.parse_warnings == ()
    assert md.validation_warnings == ()
