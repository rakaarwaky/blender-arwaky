from modules.plugin.src.taxonomy_plugin_vo import BlenderVersion, PluginActionName, PluginParameterMap
from plugin.rigify.plugin_entry import (
    RIGIFY_CAPABILITIES,
    RIGIFY_UNSUPPORTED_CAPABILITIES,
    RigifyPluginOperation,
    create_runtime_provider,
)
from plugin.rigify.plugin_runtime_facts import probe_blender_runtime


def test_rigify_absent_provider_is_optional() -> None:
    provider = RigifyPluginOperation(installed=False, active=False)

    discovery = provider.discover(BlenderVersion("5.2"))

    assert discovery.installed is False
    assert discovery.active is False
    assert provider.capabilities() == RIGIFY_CAPABILITIES


def test_rigify_active_provider_declares_rigging_capabilities() -> None:
    provider = RigifyPluginOperation(installed=True, active=True)

    discovery = provider.discover(BlenderVersion("5.2"))

    assert discovery.compatible is True
    assert provider.capabilities() == RIGIFY_CAPABILITIES


def test_rigify_exposes_non_character_boundary() -> None:
    provider = RigifyPluginOperation(installed=True, active=True)

    assert provider.unsupported_capabilities() == RIGIFY_UNSUPPORTED_CAPABILITIES
    assert {"character", "asset_generation"}.isdisjoint(
        {str(capability) for capability in provider.capabilities()}
    )


def test_rigify_rejects_undeclared_operation() -> None:
    provider = RigifyPluginOperation(installed=True, active=True)

    result = provider.execute(
        PluginActionName("character.create"),
        PluginParameterMap({}),
    )

    assert result.success is False
    assert result.message == "unsupported"


def test_runtime_probe_reads_enabled_rigify_addon() -> None:
    class FakeAddons:
        def keys(self) -> tuple[str, ...]:
            return ("rigify", "other_addon")

    class FakePreferences:
        addons = FakeAddons()

    class FakeContext:
        preferences = FakePreferences()

    class FakeApp:
        version = (5, 2, 0)

    class FakeBlender:
        app = FakeApp()
        context = FakeContext()

    facts = probe_blender_runtime(FakeBlender())
    provider = create_runtime_provider(FakeBlender())

    assert facts.installed is True
    assert facts.active is True
    assert provider.discover(facts.blender_version).compatible is True


def test_runtime_probe_reads_rigify_public_operator() -> None:
    class FakeObjectNamespace:
        def armature_human_metarig_add(self) -> None:
            return None

    class FakeOps:
        object = FakeObjectNamespace()

    class FakeApp:
        version = (5, 2, 0)

    class FakeBlender:
        app = FakeApp()
        ops = FakeOps()

    facts = probe_blender_runtime(FakeBlender())

    assert facts.installed is True
    assert facts.active is True
    assert facts.blender_version == "5.2.0"


def test_runtime_probe_without_blender_is_unavailable() -> None:
    facts = probe_blender_runtime(object())

    assert facts.installed is False
    assert facts.active is False


def test_rigify_reports_incompatible_blender() -> None:
    provider = RigifyPluginOperation(installed=True, active=True)

    discovery = provider.discover(BlenderVersion("4.5"))

    assert discovery.compatible is False
    assert discovery.message == "incompatible"


def test_inspect_armature_request_maps_to_canonical_command() -> None:
    from plugin.rigify.plugin_operations import RigifyInspectArmatureRequest, map_inspect_armature

    command = map_inspect_armature(RigifyInspectArmatureRequest("Rigify_Rig", 25))

    assert command == {
        "type": "inspect_armature",
        "params": {"object_name": "Rigify_Rig", "limit": 25},
    }


def test_inspect_armature_request_rejects_unbounded_limit() -> None:
    from plugin.rigify.plugin_operations import RigifyInspectArmatureRequest

    try:
        RigifyInspectArmatureRequest("Rigify_Rig", 1001)
    except ValueError as error:
        assert "limit" in str(error)
    else:
        raise AssertionError("expected invalid inspect_armature limit to be rejected")


def test_pose_bone_transform_request_maps_to_canonical_command() -> None:
    from plugin.rigify.plugin_operations import (
        RigifyPoseBoneTransformRequest,
        map_set_pose_bone_transform,
    )

    command = map_set_pose_bone_transform(
        RigifyPoseBoneTransformRequest(
            armature_name="metarig",
            bone_name="upper_arm.L",
            location=[0.1, 0.0, 0.0],
            rotation_euler=[0.0, 0.5, 0.0],
            scale=[1.0, 1.0, 1.0],
        )
    )

    assert command["type"] == "set_pose_bone_transform"
    assert command["params"]["bone_name"] == "upper_arm.L"
    assert command["params"]["rotation_euler"] == [0.0, 0.5, 0.0]


def test_pose_bone_transform_request_rejects_empty_transform() -> None:
    from plugin.rigify.plugin_operations import RigifyPoseBoneTransformRequest

    try:
        RigifyPoseBoneTransformRequest("metarig", "upper_arm.L")
    except ValueError as error:
        assert "at least one" in str(error)
    else:
        raise AssertionError("expected empty pose transform to be rejected")


def test_pose_bone_transform_request_rejects_non_finite_vector() -> None:
    from plugin.rigify.plugin_operations import RigifyPoseBoneTransformRequest

    try:
        RigifyPoseBoneTransformRequest("metarig", "upper_arm.L", location=[0.0, float("nan"), 0.0])
    except ValueError as error:
        assert "finite" in str(error)
    else:
        raise AssertionError("expected non-finite pose transform to be rejected")


def test_bone_constraint_request_maps_to_canonical_command() -> None:
    from plugin.rigify.plugin_operations import (
        RigifyBoneConstraintRequest,
        map_configure_bone_constraint,
    )

    command = map_configure_bone_constraint(
        RigifyBoneConstraintRequest(
            armature_name="metarig",
            bone_name="upper_arm.L",
            constraint_type="copy_rotation",
            enabled=True,
            constraint_name="Arwaky_CopyRotation",
            target_object="TargetRig",
            subtarget="upper_arm.R",
        )
    )

    assert command["type"] == "configure_bone_constraint"
    assert command["params"]["constraint_type"] == "COPY_ROTATION"
    assert command["params"]["target_object"] == "TargetRig"


def test_bone_constraint_request_rejects_unallowlisted_type() -> None:
    from plugin.rigify.plugin_operations import RigifyBoneConstraintRequest

    try:
        RigifyBoneConstraintRequest("metarig", "upper_arm.L", "IK", True)
    except ValueError as error:
        assert "unsupported constraint type" in str(error)
    else:
        raise AssertionError("expected unsupported constraint type to be rejected")


def test_bone_constraint_request_rejects_non_boolean_enabled() -> None:
    from plugin.rigify.plugin_operations import RigifyBoneConstraintRequest

    try:
        RigifyBoneConstraintRequest("metarig", "upper_arm.L", "COPY_ROTATION", "true")
    except ValueError as error:
        assert "enabled" in str(error)
    else:
        raise AssertionError("expected non-boolean enabled value to be rejected")


def test_deformation_state_request_maps_to_canonical_command() -> None:
    from plugin.rigify.plugin_operations import (
        RigifyDeformationStateRequest,
        map_get_deformation_state,
    )

    command = map_get_deformation_state(RigifyDeformationStateRequest("MPFB_Human"))

    assert command == {
        "type": "get_deformation_state",
        "params": {"object_name": "MPFB_Human"},
    }


def test_deformation_state_request_rejects_empty_object_name() -> None:
    from plugin.rigify.plugin_operations import RigifyDeformationStateRequest

    try:
        RigifyDeformationStateRequest("   ")
    except ValueError as error:
        assert "object_name" in str(error)
    else:
        raise AssertionError("expected empty object name to be rejected")


def test_shape_key_request_maps_to_canonical_command() -> None:
    from plugin.rigify.plugin_operations import RigifyShapeKeyRequest, map_configure_shape_key

    command = map_configure_shape_key(
        RigifyShapeKeyRequest(
            object_name="MPFB_Human",
            shape_key_name="Smile",
            enabled=True,
            value=0.75,
            slider_min=0.0,
            slider_max=1.0,
        )
    )

    assert command["type"] == "configure_shape_key"
    assert command["params"]["shape_key_name"] == "Smile"
    assert command["params"]["value"] == 0.75


def test_shape_key_request_rejects_value_outside_slider_range() -> None:
    from plugin.rigify.plugin_operations import RigifyShapeKeyRequest

    try:
        RigifyShapeKeyRequest("MPFB_Human", "Smile", True, value=2.0, slider_min=0.0, slider_max=1.0)
    except ValueError as error:
        assert "slider limits" in str(error)
    else:
        raise AssertionError("expected shape key value outside slider range to be rejected")


def test_shape_key_request_rejects_inverted_slider_range() -> None:
    from plugin.rigify.plugin_operations import RigifyShapeKeyRequest

    try:
        RigifyShapeKeyRequest("MPFB_Human", "Smile", True, value=0.0, slider_min=1.0, slider_max=0.0)
    except ValueError as error:
        assert "slider_min" in str(error)
    else:
        raise AssertionError("expected inverted slider range to be rejected")


def test_shape_key_request_rejects_non_boolean_enabled() -> None:
    from plugin.rigify.plugin_operations import RigifyShapeKeyRequest

    try:
        RigifyShapeKeyRequest("MPFB_Human", "Smile", "true")
    except ValueError as error:
        assert "enabled" in str(error)
    else:
        raise AssertionError("expected non-boolean enabled value to be rejected")


def test_character_binding_request_maps_to_canonical_command() -> None:
    from plugin.rigify.plugin_operations import (
        RigifyCharacterBindingRequest,
        map_bind_character_to_rig,
    )

    command = map_bind_character_to_rig(
        RigifyCharacterBindingRequest(
            character_object_name="MPFB_Human",
            armature_name="metarig",
            modifier_name="Rigify_Armature",
            replace_existing=True,
        )
    )

    assert command == {
        "type": "bind_character_to_rig",
        "params": {
            "character_object_name": "MPFB_Human",
            "armature_name": "metarig",
            "modifier_name": "Rigify_Armature",
            "replace_existing": True,
        },
    }


def test_character_binding_request_uses_default_modifier_name() -> None:
    from plugin.rigify.plugin_operations import (
        RigifyCharacterBindingRequest,
        map_bind_character_to_rig,
    )

    command = map_bind_character_to_rig(RigifyCharacterBindingRequest("MPFB_Human", "metarig"))

    assert command["params"]["modifier_name"] == "Rigify_Armature"


def test_character_binding_request_rejects_non_boolean_replace_flag() -> None:
    from plugin.rigify.plugin_operations import RigifyCharacterBindingRequest

    try:
        RigifyCharacterBindingRequest("MPFB_Human", "metarig", replace_existing="true")
    except ValueError as error:
        assert "replace_existing" in str(error)
    else:
        raise AssertionError("expected non-boolean replace flag to be rejected")
