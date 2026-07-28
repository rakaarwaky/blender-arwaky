import os

MODULES = '/home/raka/mcp-arwaky/blender-arwaky/modules'

RENAME_MAP = {
    'asset/src/agent_orchestrator.py': 'asset/src/agent_asset_orchestrator.py',
    'cli/src/agent_orchestrator.py': 'cli/src/agent_cli_orchestrator.py',
    'dispatcher/src/agent_orchestrator.py': 'dispatcher/src/agent_dispatcher_orchestrator.py',
    'gateway/src/capabilities_connection.py': 'gateway/src/capabilities_gateway_connection.py',
    'gateway/src/capabilities_transport.py': 'gateway/src/capabilities_gateway_transport.py',
    'launcher/src/agent_orchestrator.py': 'launcher/src/agent_launcher_operate_orchestrator.py',
    'mcp/src/agent_orchestrator.py': 'mcp/src/agent_mcp_orchestrator.py',
    'mcp/src/bootstrap.py': 'mcp/src/capabilities_server_bootstrap.py',
    'mcp/src/capabilities_health.py': 'mcp/src/capabilities_health_checker.py',
    'mcp/src/capabilities_lifecycle.py': 'mcp/src/capabilities_lifecycle_processor.py',
    'mcp/src/capabilities_startup.py': 'mcp/src/capabilities_startup_processor.py',
    'mcp/src/container.py': 'mcp/src/root_mcp_container.py',
    'mcp/src/prompts.py': 'mcp/src/utility_prompt_provider.py',
    'render/src/agent_orchestrator.py': 'render/src/agent_render_orchestrator.py',
    'scene/src/agent_orchestrator.py': 'scene/src/agent_scene_orchestrator.py',
    'shared/src/asset/utility/utility_polyhaven.py': 'shared/src/asset/utility/utility_polyhaven_client.py',
    'shared/src/asset/utility/utility_sketchfab.py': 'shared/src/asset/utility/utility_sketchfab_client.py',
    'shared/src/gateway/utility/utility_id.py': 'shared/src/gateway/utility/utility_id_generator.py',
    'shared/src/gateway/utility/utility_io.py': 'shared/src/gateway/utility/utility_io_handler.py',
    'shared/src/gateway/utility/utility_message.py': 'shared/src/gateway/utility/utility_message_codec.py',
    'shared/src/gateway/utility/utility_schema.py': 'shared/src/gateway/utility/utility_schema_validator.py',
    'shared/src/gateway/utility/utility_string.py': 'shared/src/gateway/utility/utility_string_formatter.py',
    'shared/src/gateway/utility/utility_time.py': 'shared/src/gateway/utility/utility_time_formatter.py',
    'shared/src/gateway/utility/utility_validator.py': 'shared/src/gateway/utility/utility_gateway_validator.py',
    'shared/src/telemetry/contract_telemetry.py': 'shared/src/telemetry/contract_telemetry_protocol.py',
    'telemetry/src/agent_orchestrator.py': 'telemetry/src/agent_telemetry_orchestrator.py',
    'cli/src/capabilities_cli_error.py': 'cli/src/capabilities_cli_error_formatter.py',
    'cli/src/surface_cli_blender_manager.py': 'cli/src/surface_cli_blender_controller.py',
    'cli/src/surface_cli_commands.py': 'cli/src/surface_cli_commands_list_action.py',
    'cli/src/surface_cli_main.py': 'cli/src/surface_cli_main_controller.py',
    'cli/src/surface_cli_registry.py': 'cli/src/surface_cli_registry_controller.py',
    'cli/src/surface_cli_socket_client.py': 'cli/src/surface_cli_socket_controller.py',
    'mcp/src/surface_command_execute.py': 'mcp/src/surface_execute_command.py',
    'mcp/src/surface_commands_list.py': 'mcp/src/surface_commands_list_action.py',
    'mcp/src/surface_health_check.py': 'mcp/src/surface_health_command.py',
    'mcp/src/surface_mcp_cli_wrapper.py': 'mcp/src/surface_mcp_cli_command.py',
    'mcp/src/surface_prompt_register.py': 'mcp/src/surface_prompt_register_action.py',
    'mcp/src/surface_server_instance.py': 'mcp/src/surface_server_instance_controller.py',
    'mcp/src/surface_server_start.py': 'mcp/src/surface_server_start_command.py',
    'mcp/src/surface_skill_read.py': 'mcp/src/surface_skill_read_action.py',
    'mcp/src/surface_tool_registry.py': 'mcp/src/surface_tool_registry_controller.py',
    'shared/src/common/contract_command_catalog.py': 'shared/src/common/contract_command_catalog_protocol.py',
    'shared/src/render/contract_viewport_capture.py': 'shared/src/render/contract_viewport_capture_protocol.py',
    'shared/src/scene/contract_scene_inspection.py': 'shared/src/scene/contract_scene_inspection_protocol.py',
    'shared/src/telemetry/contract_telemetry_classification.py': 'shared/src/telemetry/contract_telemetry_classification_protocol.py',
    'shared/src/telemetry/contract_telemetry_enrichment.py': 'shared/src/telemetry/contract_telemetry_enrichment_protocol.py',
    'shared/src/telemetry/contract_telemetry_recording.py': 'shared/src/telemetry/contract_telemetry_recording_protocol.py',
    'shared/src/telemetry/contract_telemetry_session_management.py': 'shared/src/telemetry/contract_telemetry_session_management_protocol.py',
}

conflicts = []
missing = []
for old_rel, new_rel in RENAME_MAP.items():
    old_path = os.path.join(MODULES, old_rel)
    new_path = os.path.join(MODULES, new_rel)
    if not os.path.exists(old_path):
        missing.append(old_rel)
    if old_rel != new_rel and os.path.exists(new_path):
        conflicts.append(new_rel)

if conflicts:
    print(f"CONFLICTS (target already exists):")
    for c in conflicts:
        print(f"  {c}")
if missing:
    print(f"MISSING source files:")
    for m in missing:
        print(f"  {m}")
if not conflicts and not missing:
    print("PRE-FLIGHT OK — all files exist and no conflicts")
