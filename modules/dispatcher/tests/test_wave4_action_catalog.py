from __future__ import annotations

from modules.dispatcher.src.utility_action_catalog_bootstrap import iter_action_metadata
from modules.shared.src.dispatcher.taxonomy_dispatcher_constant import DISPATCHER_ACTION_SCHEMAS

WAVE4_ACTIONS = {
    "get_simulation_state": "physics",
    "get_simulation_cache_status": "physics",
    "configure_particle_system": "physics",
    "configure_force_field": "physics",
    "configure_fluid_domain": "physics",
}


def test_wave4_actions_are_canonical_and_owned_by_physics() -> None:
    metadata = {item.action_name: item for item in iter_action_metadata()}

    assert set(WAVE4_ACTIONS).issubset(metadata)  # nosec B101
    for action_name, owner in WAVE4_ACTIONS.items():
        assert metadata[action_name].owning_feature_ref == owner  # nosec B101
        assert action_name in DISPATCHER_ACTION_SCHEMAS[owner]  # nosec B101


def test_wave4_read_models_are_read_only() -> None:
    metadata = {item.action_name: item for item in iter_action_metadata()}

    for action_name in ("get_simulation_state", "get_simulation_cache_status"):
        assert metadata[action_name].read_only_flag is True  # nosec B101
        assert metadata[action_name].idempotency_flag is True  # nosec B101
        assert metadata[action_name].scene_mutation_flag is False  # nosec B101


def test_wave4_mutations_have_required_parameters() -> None:
    physics = DISPATCHER_ACTION_SCHEMAS["physics"]

    particle = physics["configure_particle_system"]["parameters"]
    assert particle["object_name"]["required"] is True  # nosec B101
    assert particle["enabled"]["required"] is True  # nosec B101
    assert "NEWTON" in particle["physics_type"]["enum"]  # nosec B101

    force_field = physics["configure_force_field"]["parameters"]
    assert force_field["object_name"]["required"] is True  # nosec B101
    assert "TURBULENCE" in force_field["field_type"]["enum"]  # nosec B101

    fluid = physics["configure_fluid_domain"]["parameters"]
    assert "LIQUID" in fluid["domain_type"]["enum"]  # nosec B101
    assert "FINAL" in fluid["cache_type"]["enum"]  # nosec B101
