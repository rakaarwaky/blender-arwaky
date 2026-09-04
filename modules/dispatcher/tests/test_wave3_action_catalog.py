from __future__ import annotations

from modules.dispatcher.src.utility_action_catalog_bootstrap import iter_action_metadata
from modules.shared.src.dispatcher.taxonomy_dispatcher_constant import DISPATCHER_ACTION_SCHEMAS

WAVE3_OWNERS = {
    "inspect_compositor_nodes": "compositor",
    "configure_compositor": "compositor",
    "create_compositor_node": "compositor",
    "set_compositor_link": "compositor",
    "inspect_sequence_editor": "vse",
    "create_sequence_strip": "vse",
    "remove_sequence_strip": "vse",
    "render_sequence": "vse",
    "get_physics_state": "physics",
    "configure_rigid_body": "physics",
    "configure_cloth_simulation": "physics",
    "bake_physics_simulation": "physics",
    "clear_physics_bake": "physics",
}


def test_wave3_actions_are_canonical_and_owned() -> None:
    metadata = {item.action_name: item for item in iter_action_metadata()}

    assert set(WAVE3_OWNERS).issubset(metadata)  # nosec B101
    for action_name, owner in WAVE3_OWNERS.items():
        assert metadata[action_name].owning_feature_ref == owner  # nosec B101
        assert action_name in DISPATCHER_ACTION_SCHEMAS[owner]  # nosec B101


def test_wave3_read_models_are_read_only() -> None:
    metadata = {item.action_name: item for item in iter_action_metadata()}

    for action_name in ("inspect_compositor_nodes", "inspect_sequence_editor", "get_physics_state"):
        assert metadata[action_name].read_only_flag is True  # nosec B101
        assert metadata[action_name].idempotency_flag is True  # nosec B101


def test_wave3_long_running_actions_use_shared_job_metadata() -> None:
    metadata = {item.action_name: item for item in iter_action_metadata()}

    for action_name in ("render_sequence", "bake_physics_simulation"):
        assert metadata[action_name].background_eligibility_flag is True  # nosec B101
        assert metadata[action_name].long_running_flag is True  # nosec B101
        assert metadata[action_name].default_timeout == 300.0  # nosec B101


def test_wave3_destructive_actions_require_dispatcher_confirmation() -> None:
    metadata = {item.action_name: item for item in iter_action_metadata()}

    for action_name in ("remove_sequence_strip", "bake_physics_simulation", "clear_physics_bake"):
        assert metadata[action_name].destructive_flag is True  # nosec B101
        assert metadata[action_name].scene_mutation_flag is True  # nosec B101
