from __future__ import annotations

from modules.dispatcher.src.utility_action_catalog_bootstrap import iter_action_metadata
from modules.shared.src.dispatcher.taxonomy_dispatcher_constant import DISPATCHER_ACTION_SCHEMAS

WAVE1_OWNERS = {
    "list_scene_objects": "scene",
    "get_object_hierarchy": "scene",
    "undo": "scene",
    "redo": "scene",
    "create_material": "object",
    "set_material_properties": "object",
    "set_material_texture": "object",
    "set_render_settings": "render",
    "submit_task": "job",
    "list_tasks": "job",
    "get_capacity_status": "job",
}


def test_wave1_actions_are_canonical_and_owned() -> None:
    metadata = {item.action_name: item for item in iter_action_metadata()}

    assert set(WAVE1_OWNERS).issubset(metadata)  # nosec B101
    for action_name, owner in WAVE1_OWNERS.items():
        assert metadata[action_name].owning_feature_ref == owner  # nosec B101
        assert action_name in DISPATCHER_ACTION_SCHEMAS[owner]  # nosec B101


def test_wave1_read_models_are_discovered_as_read_only() -> None:
    metadata = {item.action_name: item for item in iter_action_metadata()}

    for action_name in ("list_scene_objects", "get_object_hierarchy", "list_tasks", "get_capacity_status"):
        assert metadata[action_name].read_only_flag is True  # nosec B101
        assert metadata[action_name].idempotency_flag is True  # nosec B101


def test_wave1_mutations_are_not_misclassified_as_read_only() -> None:
    metadata = {item.action_name: item for item in iter_action_metadata()}

    for action_name in (
        "undo",
        "redo",
        "create_material",
        "set_material_properties",
        "set_material_texture",
        "set_render_settings",
        "submit_task",
    ):
        assert metadata[action_name].read_only_flag is False  # nosec B101
        assert metadata[action_name].scene_mutation_flag is True  # nosec B101
