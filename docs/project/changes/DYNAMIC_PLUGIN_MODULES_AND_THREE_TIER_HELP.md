# Dynamic Plugin Modules and Three-Tier CLI Help

## Implemented direction

Arwaky now has a hierarchical CLI surface:

```text
blender-arwaky --help
blender-arwaky <module> --help
blender-arwaky <module> <tool> --help
blender-arwaky <module> <tool> [flags]
```

The module-scoped form is the primary consumer-facing form. A compatibility namespace remains available:

```text
blender-arwaky action <canonical-action> [flags]
```

The compatibility namespace is explicit because a flat action name can collide with a module name. The native `render` action is the current example: `blender-arwaky render --help` means the `render` module; the action is invoked as `blender-arwaky action render ...`.

## Plugin lifecycle visibility

Plugin state is normalized as `unavailable`, `installed`, `enabled`, or `incompatible`. Only `enabled` means installed, active, and compatible. The plugin orchestrator now provides `enabled_plugin_ids()` and `enabled_capabilities()` so discovery can expose only executable provider capabilities.

| Provider state | Appears as active module | Appears in active tool discovery | Execution |
|---|---:|---:|---|
| `unavailable` | No | No | Blocked/not executable |
| `installed` | No | No | Blocked until enabled |
| `enabled` | Yes | Yes | Eligible for routing |
| `incompatible` | No | No | Blocked with compatibility state |

Core modules remain available when an optional provider is absent or unhealthy. Provider capability collisions remain rejected by the registry.

## Current code changes

| Area | Change |
|---|---|
| `modules/root_cli_main_entry.py` | Added reusable action parser, nested module/tool parsers, explicit `action` compatibility namespace, and legacy normalization for unambiguous flat commands |
| `modules/plugin/src/agent_plugin_orchestrator.py` | Added enabled-only provider and capability views |
| CLI tests | Added module/tool help, nested routing, and compatibility namespace coverage |
| Plugin tests | Added enabled/disabled capability visibility coverage |
| `modules/cli/FRD.md` | Updated command grammar, collision rule, and plugin lifecycle visibility policy |

## Important boundary

The parser can always expose core module help from the canonical catalog. Optional provider modules must be populated from runtime health/discovery, not from the mere presence of a source directory. A plugin source tree or cached package is not enough to make a module visible. The provider must report `enabled` before its module and capabilities enter active discovery.

For MCP, the same rule should be applied to scoped `help` and `list_commands`: inactive provider actions must not be returned in the active context. The server should refresh discovery after plugin install, enable, disable, remove, or health-state changes.

## Verification

The focused plugin and CLI suite passes with 30 tests. Full repository gates remain required before merge.
