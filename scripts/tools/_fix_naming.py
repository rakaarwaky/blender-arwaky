"""Fix all AES101 + AES102 naming violations by renaming files + updating imports."""
import os
import re
import shutil

PROJECT = '/home/raka/mcp-arwaky/blender-arwaky'

# old_basename -> new_basename (relative to modules/)
RENAME_MAP = {
    # AES101: <3 words
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

    # AES102-only: bad suffix
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

MODULES_DIR = os.path.join(PROJECT, 'modules')
BLENDER_ADDON_DIR = os.path.join(PROJECT, 'blender_mcp_addon')

def old_to_new_module(old_rel):
    old_stem = old_rel.replace('.py', '').replace('/', '.')
    new_rel = RENAME_MAP[old_rel]
    new_stem = new_rel.replace('.py', '').replace('/', '.')
    return old_stem, new_stem

def update_file_imports(filepath, changes):
    with open(filepath) as f:
        content = f.read()
    original = content
    for old_stem, new_stem in changes:
        # from modules.xxx.old_name import YY
        content = re.sub(
            r'(from\s+)' + re.escape(old_stem) + r'(\b)',
            r'\1' + new_stem + r'\2',
            content
        )
        # import modules.xxx.old_name
        content = re.sub(
            r'(import\s+)' + re.escape(old_stem) + r'(\b)',
            r'\1' + new_stem + r'\2',
            content
        )
    if content != original:
        with open(filepath, 'w') as f:
            f.write(content)
        return True
    return False

def main():
    # Step 1: Build import changes mapping
    import_changes = {}
    for old_rel, _new_rel in RENAME_MAP.items():
        old_stem, new_stem = old_to_new_module(old_rel)
        import_changes[old_stem] = new_stem

    # Step 2: Rename files
    for old_rel, new_rel in RENAME_MAP.items():
        old_path = os.path.join(MODULES_DIR, old_rel)
        new_path = os.path.join(MODULES_DIR, new_rel)
        if not os.path.exists(old_path):
            print(f"  MISSING: {old_rel}")
            continue
        os.makedirs(os.path.dirname(new_path), exist_ok=True)
        shutil.move(old_path, new_path)
        print(f"  RENAMED: {old_rel} -> {new_rel}")

    # Step 3: Update all imports in the project (modules/ and blender_mcp_addon/)
    all_stems = list(import_changes.keys())
    updated = 0
    for root, _dirs, files in os.walk(PROJECT):
        parts = root.split(os.sep)
        if '.git' in parts or '__pycache__' in parts or '.venv' in parts or '__init__' in parts:
            continue
        for f in files:
            if not f.endswith('.py'):
                continue
            fp = os.path.join(root, f)
            changes = []
            for old_stem in all_stems:
                new_stem = import_changes[old_stem]
                changes.append((old_stem, new_stem))
            if update_file_imports(fp, changes):
                updated += 1
                rel = os.path.relpath(fp, PROJECT)
                print(f"  UPDATED: {rel}")

    print(f"\nDone. Renamed {len(RENAME_MAP)} files, updated {updated} files with import fixes.")

if __name__ == '__main__':
    main()
