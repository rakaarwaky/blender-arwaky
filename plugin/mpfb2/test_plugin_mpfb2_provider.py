from __future__ import annotations

from modules.plugin.src.taxonomy_plugin_vo import (
    BlenderVersion,
    PluginActionName,
    PluginParameterMap,
)
from plugin.mpfb2.plugin_entry import Mpfb2PluginOperation


def test_mpfb2_absent_provider_is_optional() -> None:
    provider = Mpfb2PluginOperation(installed=False, active=False)

    discovery = provider.discover(BlenderVersion("4.2"))

    assert discovery.installed is False
    assert discovery.active is False
    assert provider.capabilities() == ()


def test_mpfb2_active_provider_declares_capability() -> None:
    provider = Mpfb2PluginOperation(installed=True, active=True)

    discovery = provider.discover(BlenderVersion("4.2"))

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


def test_mpfb2_reports_incompatible_blender() -> None:
    provider = Mpfb2PluginOperation(installed=True, active=True)

    discovery = provider.discover(BlenderVersion("4.1"))

    assert discovery.compatible is False
    assert discovery.message == "incompatible"
