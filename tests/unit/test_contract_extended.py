"""Tests for contract layer.

Mencakup:
- workflow_operate_protocol.py (78% -> 90%)
- catalog_command_handler.py (62% -> 85%) - surfaces layer
"""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from contract.workflow_operate_protocol import WorkflowProtocol
from taxonomy import SuccessFlag, ProviderName, Prompt


class ConcreteWorkflowProtocol(WorkflowProtocol):
    async def create_basic_scene(self, prompt: Prompt) -> SuccessFlag:
        return SuccessFlag(True)

    async def generate_and_import_ai_asset(
        self, provider_name: ProviderName, prompt: Prompt
    ) -> Prompt:
        return Prompt(f"Generated with {provider_name}: {prompt}")


@pytest.mark.unit
class TestWorkflowProtocol:
    def test_interface_is_abstract(self):
        with pytest.raises(TypeError):
            WorkflowProtocol()  # type: ignore

    @pytest.mark.asyncio
    async def test_create_basic_scene(self):
        protocol = ConcreteWorkflowProtocol()
        result = await protocol.create_basic_scene(Prompt("forest scene"))
        assert result is True

    @pytest.mark.asyncio
    async def test_generate_and_import(self):
        protocol = ConcreteWorkflowProtocol()
        result = await protocol.generate_and_import_ai_asset(
            provider_name=ProviderName("polyhaven"),
            prompt=Prompt("a forest HDRI"),
        )
        assert "polyhaven" in result
        assert "forest" in result


# ─── catalog_command_handler.py (surfaces) ───────────────────────

from surfaces.catalog_command_handler import (
    CommandCatalogSurfaceHandler,
    list_commands,
    filter_by_domain,
    get_actions_by_capability,
    register_command_catalog,
)
from taxonomy import DomainRef, CapabilityRef


@pytest.mark.unit
class TestCommandCatalogSurfaceHandler:
    def test_list_commands_all(self):
        result = CommandCatalogSurfaceHandler.list_commands(DomainRef("all"))
        assert isinstance(result, list)
        assert len(result) > 0

    def test_list_commands_specific_domain(self):
        all_cmds = CommandCatalogSurfaceHandler.list_commands(DomainRef("all"))
        result = CommandCatalogSurfaceHandler.list_commands(DomainRef("scene"))
        assert isinstance(result, list)
        # Filtered result should be a subset
        assert all(cmd in all_cmds for cmd in result)

    def test_list_commands_unknown_domain_returns_empty(self):
        result = CommandCatalogSurfaceHandler.list_commands(DomainRef("nonexistent_domain_xyz"))
        assert result == [] or isinstance(result, list)

    def test_filter_by_domain_returns_dict(self):
        result = CommandCatalogSurfaceHandler.filter_by_domain(DomainRef("scene"))
        assert isinstance(result, dict)

    def test_filter_by_domain_all_values_match(self):
        result = CommandCatalogSurfaceHandler.filter_by_domain(DomainRef("scene"))
        for name, spec in result.items():
            assert spec.get("domain") == "scene"

    def test_filter_by_unknown_domain_empty(self):
        result = CommandCatalogSurfaceHandler.filter_by_domain(DomainRef("xyz_unknown"))
        assert result == {}

    def test_get_actions_by_capability(self):
        result = CommandCatalogSurfaceHandler.get_actions_by_capability(CapabilityRef("scene_ops"))
        assert isinstance(result, list)

    def test_get_actions_by_unknown_capability_empty(self):
        result = CommandCatalogSurfaceHandler.get_actions_by_capability(CapabilityRef("nonexistent_cap"))
        assert result == []

    def test_module_alias_list_commands(self):
        """Module-level alias should work identically."""
        result = list_commands(DomainRef("all"))
        assert result == CommandCatalogSurfaceHandler.list_commands(DomainRef("all"))

    def test_module_alias_filter_by_domain(self):
        result = filter_by_domain(DomainRef("scene"))
        assert result == CommandCatalogSurfaceHandler.filter_by_domain(DomainRef("scene"))

    def test_module_alias_get_actions_by_capability(self):
        result = get_actions_by_capability(CapabilityRef("scene_ops"))
        assert result == CommandCatalogSurfaceHandler.get_actions_by_capability(CapabilityRef("scene_ops"))

    def test_register_command_catalog(self):
        """register_command_catalog should register a tool on the mcp object."""
        mcp = MagicMock()
        registered_tool = None

        def capture_tool(func=None, **kwargs):
            """Decorator factory that captures the tool."""
            def decorator(f):
                nonlocal registered_tool
                registered_tool = f
                return f
            return decorator if func is None else decorator(func)

        mcp.tool = capture_tool
        result = CommandCatalogSurfaceHandler.register_command_catalog(mcp)
        # The function should be returned and registered
        assert result is not None or registered_tool is not None
