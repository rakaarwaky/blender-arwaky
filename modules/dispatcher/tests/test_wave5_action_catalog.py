from __future__ import annotations

from modules.dispatcher.src.utility_action_catalog_bootstrap import iter_action_metadata
from modules.shared.src.dispatcher.taxonomy_dispatcher_constant import DISPATCHER_ACTION_SCHEMAS

WAVE5_ACTIONS = {
    "inspect_armature": "rigging",
    "set_pose_bone_transform": "rigging",
    "configure_bone_constraint": "rigging",
    "configure_shape_key": "rigging",
    "get_deformation_state": "rigging",
}


def test_wave5_actions_are_canonical_and_owned_by_rigging() -> None:
    metadata = {item.action_name: item for item in iter_action_metadata()}

    assert set(WAVE5_ACTIONS).issubset(metadata)  # nosec B101
    for action_name, owner in WAVE5_ACTIONS.items():
        assert metadata[action_name].owning_feature_ref == owner  # nosec B101
        assert action_name in DISPATCHER_ACTION_SCHEMAS[owner]  # nosec B101


def test_wave5_read_models_are_read_only() -> None:
    metadata = {item.action_name: item for item in iter_action_metadata()}

    for action_name in ("inspect_armature", "get_deformation_state"):
        assert metadata[action_name].read_only_flag is True  # nosec B101
        assert metadata[action_name].idempotency_flag is True  # nosec B101
        assert metadata[action_name].scene_mutation_flag is False  # nosec B101


def test_wave5_constraints_and_shape_keys_have_bounded_contracts() -> None:
    rigging = DISPATCHER_ACTION_SCHEMAS["rigging"]

    constraint = rigging["configure_bone_constraint"]["parameters"]
    assert constraint["armature_name"]["required"] is True  # nosec B101
    assert constraint["bone_name"]["required"] is True  # nosec B101
    assert "COPY_ROTATION" in constraint["constraint_type"]["enum"]  # nosec B101

    shape_key = rigging["configure_shape_key"]["parameters"]
    assert shape_key["object_name"]["required"] is True  # nosec B101
    assert shape_key["shape_key_name"]["required"] is True  # nosec B101
    assert shape_key["enabled"]["required"] is True  # nosec B101
