from __future__ import annotations

from modules.plugin.src.contract_plugin_operation_protocol import PluginOperationProtocol
from modules.plugin.src.root_plugin_container import PluginContainer
from modules.plugin.src.taxonomy_plugin_vo import (
    BlenderVersion,
    PluginActionName,
    PluginCapabilityId,
    PluginCapabilityList,
    PluginDiscoveryVO,
    PluginExecutionVO,
    PluginHealthVO,
    PluginId,
    PluginMessage,
    PluginParameterMap,
)


class FakePluginOperation(PluginOperationProtocol):
    """Contract double for plugin feature wiring tests."""

    def __init__(self, plugin_id: PluginId) -> None:
        self._plugin_id = plugin_id

    def discover(self, blender_version: BlenderVersion) -> PluginDiscoveryVO:
        return PluginDiscoveryVO(
            plugin_id=self._plugin_id,
            installed=True,
            active=True,
            compatible=str(blender_version) >= "4.2",
            message=PluginMessage("discovered"),
        )

    def health_check(self) -> PluginHealthVO:
        return PluginHealthVO(
            plugin_id=self._plugin_id,
            installed=True,
            active=True,
            compatible=True,
            message=PluginMessage("healthy"),
        )

    def capabilities(self) -> PluginCapabilityList:
        return PluginCapabilityList((PluginCapabilityId("character.create"),))

    def execute(
        self,
        action: PluginActionName,
        params: PluginParameterMap,
    ) -> PluginExecutionVO:
        del params
        return PluginExecutionVO(
            plugin_id=self._plugin_id,
            action=action,
            success=True,
            message=PluginMessage("executed"),
        )


def test_container_registers_provider_and_exposes_capability() -> None:
    container = PluginContainer()
    container.register_provider(PluginId("fake"), FakePluginOperation(PluginId("fake")))

    aggregate = container.aggregate()

    assert aggregate.capabilities() == (PluginCapabilityId("character.create"),)
    assert aggregate.discover(BlenderVersion("4.2")) == (PluginId("fake"),)


def test_container_executes_declared_capability() -> None:
    container = PluginContainer()
    container.register_provider(PluginId("fake"), FakePluginOperation(PluginId("fake")))

    result = container.aggregate().execute(
        PluginActionName("character.create"),
        PluginParameterMap({"base": "default"}),
    )

    assert result.success is True
    assert result.plugin_id == PluginId("fake")


def test_container_rejects_unknown_capability() -> None:
    container = PluginContainer()
    container.register_provider(PluginId("fake"), FakePluginOperation(PluginId("fake")))

    result = container.aggregate().execute(
        PluginActionName("character.delete"),
        PluginParameterMap({}),
    )

    assert result.success is False
    assert result.message == PluginMessage("plugin capability is not registered")
