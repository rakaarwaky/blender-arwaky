from __future__ import annotations

from modules.dispatcher.src.utility_action_catalog_bootstrap import iter_action_metadata
from modules.shared.src.dispatcher.taxonomy_dispatcher_constant import DISPATCHER_ACTION_SCHEMAS

WAVE1_ANIMATION_ACTIONS = {
    "get_animation_state": ("animation", True),
    "list_object_keyframes": ("animation", True),
    "list_animation_actions": ("animation", True),
    "inspect_rigify_controls": ("animation", True),
    "import_animation_file": ("animation", False),
    "link_action_to_armature": ("animation", False),
}


def test_wave1_animation_actions_are_canonical_and_owned() -> None:
    metadata = {item.action_name: item for item in iter_action_metadata()}

    assert set(WAVE1_ANIMATION_ACTIONS).issubset(metadata)  # nosec B101
    for action_name, (owner, _) in WAVE1_ANIMATION_ACTIONS.items():
        assert metadata[action_name].owning_feature_ref == owner  # nosec B101
        assert action_name in DISPATCHER_ACTION_SCHEMAS[owner]  # nosec B101


def test_wave1_animation_read_models_are_read_only() -> None:
    metadata = {item.action_name: item for item in iter_action_metadata()}

    for action_name, (_, read_only) in WAVE1_ANIMATION_ACTIONS.items():
        if read_only:
            assert metadata[action_name].read_only_flag is True  # nosec B101
            assert metadata[action_name].idempotency_flag is True  # nosec B101


def test_wave1_animation_mutations_are_scene_mutations() -> None:
    metadata = {item.action_name: item for item in iter_action_metadata()}

    for action_name, (_, read_only) in WAVE1_ANIMATION_ACTIONS.items():
        if not read_only:
            assert metadata[action_name].read_only_flag is False  # nosec B101
            assert metadata[action_name].scene_mutation_flag is True  # nosec B101
