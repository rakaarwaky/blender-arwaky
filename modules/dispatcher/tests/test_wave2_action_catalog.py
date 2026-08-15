from __future__ import annotations

from modules.dispatcher.src.utility_action_catalog_bootstrap import iter_action_metadata
from modules.shared.src.dispatcher.taxonomy_dispatcher_constant import DISPATCHER_ACTION_SCHEMAS

WAVE2_OWNERS = {
    "inspect_geometry_node_group": "geometry_nodes",
    "create_geometry_node_group": "geometry_nodes",
    "set_geometry_node_link": "geometry_nodes",
    "set_geometry_node_modifier": "geometry_nodes",
    "get_animation_state": "animation",
    "insert_object_keyframe": "animation",
    "set_timeline_range": "animation",
    "list_object_keyframes": "animation",
    "get_mesh_statistics": "mesh",
    "validate_mesh": "mesh",
    "perform_mesh_edit_operation": "mesh",
    "ensure_mesh_uv_layer": "mesh",
}


def test_wave2_actions_are_canonical_and_owned() -> None:
    metadata = {item.action_name: item for item in iter_action_metadata()}

    assert set(WAVE2_OWNERS).issubset(metadata)  # nosec B101
    for action_name, owner in WAVE2_OWNERS.items():
        assert metadata[action_name].owning_feature_ref == owner  # nosec B101
        assert action_name in DISPATCHER_ACTION_SCHEMAS[owner]  # nosec B101


def test_wave2_read_models_are_discovered_as_read_only() -> None:
    metadata = {item.action_name: item for item in iter_action_metadata()}

    for action_name in (
        "inspect_geometry_node_group",
        "get_animation_state",
        "list_object_keyframes",
        "get_mesh_statistics",
        "validate_mesh",
    ):
        assert metadata[action_name].read_only_flag is True  # nosec B101
        assert metadata[action_name].idempotency_flag is True  # nosec B101


def test_wave2_mutations_are_not_misclassified_as_read_only() -> None:
    metadata = {item.action_name: item for item in iter_action_metadata()}

    for action_name in (
        "create_geometry_node_group",
        "set_geometry_node_link",
        "set_geometry_node_modifier",
        "insert_object_keyframe",
        "set_timeline_range",
        "perform_mesh_edit_operation",
        "ensure_mesh_uv_layer",
    ):
        assert metadata[action_name].read_only_flag is False  # nosec B101
        assert metadata[action_name].scene_mutation_flag is True  # nosec B101
