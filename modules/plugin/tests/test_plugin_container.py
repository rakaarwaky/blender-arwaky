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
    PluginLifecycleState,
    PluginMessage,
    PluginParameterMap,
)


class FakePluginOperation(PluginOperationProtocol):
    """Contract double for plugin feature wiring tests."""

    def __init__(
        self,
        plugin_id: PluginId,
        *,
        active: bool = True,
        compatible: bool = True,
        capabilities: tuple[str, ...] = ("character.create",),
    ) -> None:
        self._plugin_id = plugin_id
        self._active = active
        self._compatible = compatible
        self._capabilities = capabilities

    def discover(self, blender_version: BlenderVersion) -> PluginDiscoveryVO:
        return PluginDiscoveryVO(
            plugin_id=self._plugin_id,
            installed=True,
            active=self._active,
            compatible=self._compatible and str(blender_version) >= "4.2",
            message=PluginMessage("discovered"),
        )

    def health_check(self) -> PluginHealthVO:
        return PluginHealthVO(
            plugin_id=self._plugin_id,
            installed=True,
            active=self._active,
            compatible=self._compatible,
            message=PluginMessage("healthy"),
        )

    def capabilities(self) -> PluginCapabilityList:
        return PluginCapabilityList(tuple(PluginCapabilityId(item) for item in self._capabilities))

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


def test_registry_rejects_capability_collision() -> None:
    container = PluginContainer()
    first = container.register_provider(PluginId("first"), FakePluginOperation(PluginId("first")))
    second = container.register_provider(PluginId("second"), FakePluginOperation(PluginId("second")))

    assert first.registered is True  # nosec B101
    assert second.registered is False  # nosec B101
    assert second.message == PluginMessage("plugin capability collision: character.create")  # nosec B101


def test_registry_rejects_duplicate_capability_declaration() -> None:
    container = PluginContainer()
    result = container.register_provider(
        PluginId("duplicate"),
        FakePluginOperation(PluginId("duplicate"), capabilities=("character.create", "character.create")),
    )

    assert result.registered is False  # nosec B101
    assert result.message == PluginMessage("plugin declares a duplicate capability")  # nosec B101


def test_container_normalizes_provider_lifecycle_state() -> None:
    container = PluginContainer()
    container.register_provider(
        PluginId("fake"),
        FakePluginOperation(PluginId("fake"), active=False),
    )

    health = container.aggregate().health_check()

    assert health[0].state is PluginLifecycleState.INSTALLED  # nosec B101


def test_container_blocks_execution_for_disabled_provider() -> None:
    container = PluginContainer()
    container.register_provider(
        PluginId("fake"),
        FakePluginOperation(PluginId("fake"), active=False),
    )

    result = container.aggregate().execute(
        PluginActionName("character.create"),
        PluginParameterMap({}),
    )

    assert result.success is False
    assert result.message == PluginMessage("plugin is not executable in lifecycle state installed")  # nosec B101


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


def test_container_hides_capabilities_for_disabled_provider() -> None:
    container = PluginContainer()
    container.register_provider(
        PluginId("fake"),
        FakePluginOperation(PluginId("fake"), active=False),
    )

    aggregate = container.aggregate()

    assert aggregate.enabled_plugin_ids() == ()  # nosec B101
    assert aggregate.enabled_capabilities() == ()  # nosec B101


def test_container_exposes_capabilities_for_enabled_provider() -> None:
    container = PluginContainer()
    container.register_provider(PluginId("fake"), FakePluginOperation(PluginId("fake")))

    aggregate = container.aggregate()

    assert aggregate.enabled_plugin_ids() == (PluginId("fake"),)  # nosec B101
    assert aggregate.enabled_capabilities() == (PluginCapabilityId("character.create"),)  # nosec B101
