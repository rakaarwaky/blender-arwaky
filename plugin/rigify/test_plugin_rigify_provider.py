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
