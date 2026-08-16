from __future__ import annotations

from modules.plugin.src.taxonomy_plugin_vo import (
    BlenderVersion,
    PluginActionName,
    PluginParameterMap,
)
from plugin.mpfb2.plugin_entry import Mpfb2PluginOperation, create_runtime_provider
from plugin.mpfb2.plugin_runtime_facts import probe_blender_runtime


def test_mpfb2_absent_provider_is_optional() -> None:
    provider = Mpfb2PluginOperation(installed=False, active=False)

    discovery = provider.discover(BlenderVersion("5.2"))

    assert discovery.installed is False
    assert discovery.active is False
    assert provider.capabilities() == ()


def test_mpfb2_active_provider_declares_capability() -> None:
    provider = Mpfb2PluginOperation(installed=True, active=True)

    discovery = provider.discover(BlenderVersion("5.2"))

    assert discovery.compatible is True
    assert provider.capabilities() == ("character.create",)


def test_mpfb2_rejects_unsupported_operation() -> None:
    provider = Mpfb2PluginOperation(installed=True, active=True)

    result = provider.execute(
        PluginActionName("character.delete"),
        PluginParameterMap({}),
    )

    assert result.success is False
    assert result.message == "unsupported"


def test_runtime_probe_reads_enabled_mpfb2_addon() -> None:
    class FakeAddons:
        def keys(self) -> tuple[str, ...]:
            return ("mpfb", "other_addon")

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


def test_runtime_probe_reads_modern_extension_operator() -> None:
    class FakeOpsNamespace:
        def create_human(self) -> None:
            return None

    class FakeOps:
        mpfb = FakeOpsNamespace()

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


def test_mpfb2_reports_incompatible_blender() -> None:
    provider = Mpfb2PluginOperation(installed=True, active=True)

    discovery = provider.discover(BlenderVersion("4.5"))

    assert discovery.compatible is False
    assert discovery.message == "incompatible"
