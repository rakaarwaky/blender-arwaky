from __future__ import annotations

from typing import Any

from modules.plugin.src.registry_plugin_catalog import PluginCatalog
from modules.plugin.src.schema_plugin_manifest import PluginCapability, PluginManifest
from modules.plugin.src.schema_plugin_result import PluginHealth, PluginResult
from modules.plugin.src.service_plugin_adapter import PluginAdapter
from modules.plugin.src.service_plugin_capability import PluginCapabilityService
from modules.plugin.src.service_plugin_discovery import PluginDiscoveryService


class FakeProvider:
    def __init__(self, plugin_id: str = "fake") -> None:
        self.manifest = PluginManifest(
            plugin_id=plugin_id,
            name="Fake Provider",
            version="1.0.0",
            provider_type="test",
            blender_min_version="4.2",
            entry_point="test:create_provider",
            capabilities=(PluginCapability("fake.create", parameters=("name",)),),
        )

    def get_manifest(self) -> PluginManifest:
        return self.manifest

    def discover(self, context: dict[str, Any] | None = None) -> bool:
        return bool((context or {}).get("available", True))

    def get_capabilities(self) -> tuple[PluginCapability, ...]:
        return self.manifest.capabilities

    def execute(self, action: str, params: dict[str, Any]) -> PluginResult:
        return PluginResult(
            success=True,
            plugin_id=self.manifest.plugin_id,
            action=action,
            data=params,
        )

    def health_check(self) -> PluginHealth:
        return PluginHealth(
            plugin_id=self.manifest.plugin_id,
            installed=True,
            active=True,
            compatible=True,
            available_capabilities=frozenset({"fake.create"}),
        )


def test_catalog_registers_and_lists_declared_capabilities() -> None:
    catalog = PluginCatalog()
    catalog.register(FakeProvider())

    assert catalog.list_plugin_ids() == ("fake",)
    assert [item.capability_id for item in catalog.list_capabilities()] == ["fake.create"]


def test_catalog_rejects_duplicate_plugin_ids() -> None:
    catalog = PluginCatalog()
    catalog.register(FakeProvider())

    try:
        catalog.register(FakeProvider())
    except ValueError as error:
        assert str(error) == "plugin already registered: fake"
    else:
        raise AssertionError("duplicate plugin registration must fail")


def test_catalog_blocks_undeclared_actions() -> None:
    catalog = PluginCatalog()
    catalog.register(FakeProvider())

    result = catalog.execute("fake", "fake.delete", {})

    assert result.success is False
    assert result.category == "capability_unsupported"


def test_adapter_blocks_undeclared_actions() -> None:
    result = PluginAdapter(FakeProvider()).execute("fake.delete", {})

    assert result.success is False
    assert result.category == "capability_unsupported"


def test_discovery_checks_availability_and_minimum_version() -> None:
    provider = FakeProvider()
    service = PluginDiscoveryService()

    available = service.discover(provider, "4.3")

    class UnavailableProvider:
        def get_manifest(self) -> PluginManifest:
            return provider.get_manifest()

        def discover(self, context: dict[str, Any] | None = None) -> bool:
            del context
            return False

    unavailable = service.discover(UnavailableProvider(), "4.3")
    incompatible = service.discover(provider, "4.1")

    assert available.available is True
    assert available.compatible is True
    assert unavailable.available is False
    assert incompatible.compatible is False


def test_capability_service_reads_catalog() -> None:
    catalog = PluginCatalog()
    catalog.register(FakeProvider())

    assert PluginCapabilityService(catalog).has_capability("fake.create") is True
    assert PluginCapabilityService(catalog).has_capability("fake.delete") is False
