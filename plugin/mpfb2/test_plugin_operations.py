import pytest

from plugin.mpfb2.plugin_operations import (
    Mpfb2CreateCharacterRequest,
    Mpfb2RandomizeCharacterRequest,
    Mpfb2RemoveCharacterRequest,
    map_create_character,
    map_randomize_character,
    map_remove_character,
)


def test_create_character_maps_to_fixed_mpfb2_wire_action() -> None:
    command = map_create_character(Mpfb2CreateCharacterRequest(name="DemoHuman"))
    assert command == {
        "type": "create_character",
        "params": {"plugin_id": "mpfb2", "name": "DemoHuman"},
    }


def test_create_character_rejects_control_characters() -> None:
    with pytest.raises(ValueError, match="control character"):
        map_create_character(Mpfb2CreateCharacterRequest(name="bad\nname"))


def test_create_character_uses_default_name() -> None:
    command = map_create_character(Mpfb2CreateCharacterRequest(name="   "))
    assert command["params"]["name"] == "MPFB_Human"


def test_randomize_character_maps_seed() -> None:
    command = map_randomize_character(Mpfb2RandomizeCharacterRequest(name="Random", seed=42))
    assert command == {
        "type": "randomize_character",
        "params": {"plugin_id": "mpfb2", "name": "Random", "seed": 42},
    }


def test_randomize_character_rejects_negative_or_boolean_seed() -> None:
    with pytest.raises(ValueError, match="seed"):
        map_randomize_character(Mpfb2RandomizeCharacterRequest(seed=-1))
    with pytest.raises(ValueError, match="seed"):
        map_randomize_character(Mpfb2RandomizeCharacterRequest(seed=True))


def test_remove_character_requires_confirmation() -> None:
    with pytest.raises(ValueError, match="confirm"):
        map_remove_character(Mpfb2RemoveCharacterRequest(object_name="Human", confirm=False))


def test_remove_character_maps_exact_selector() -> None:
    command = map_remove_character(Mpfb2RemoveCharacterRequest(object_name="Human", confirm=True))
    assert command == {
        "type": "remove_character",
        "params": {"plugin_id": "mpfb2", "object_name": "Human", "confirm": True},
    }


def test_remove_character_rejects_control_characters() -> None:
    with pytest.raises(ValueError, match="control characters"):
        map_remove_character(Mpfb2RemoveCharacterRequest(object_name="bad\nobject", confirm=True))
