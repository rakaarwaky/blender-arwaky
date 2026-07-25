# BlenderArwaky — AGENT.md

> See [ARCHITECTURE.md](ARCHITECTURE.md) for full AES architecture specification, layer rules, and component roles.

## Project Overview

BlenderArwaky connects **Blender 3D** to AI agents over the Model Context Protocol (MCP).

- **Stack:** Python 3.10+, FastMCP, Blender 5.1+, AES Architecture
- **Entry Points:** `surfaces.mcp_server_entry` (MCP server) and `surfaces.cli_main_entry` (CLI mode)

---

## Quick Commands


| Command                                      | Purpose                                    |
| ---------------------------------------------- | -------------------------------------------- |
| `uv run python -m surfaces.mcp_server_entry` | Start MCP Server                           |
| `uv run python -m surfaces.cli_main_entry`   | Run CLI Mode                               |
| `uv run pytest`                              | Run Test Suite                             |
| `lint-arwaky-cli scan .`                     | Run AES Architecture Linter (`lac scan .`) |
| `uv run ruff check src/`                     | Run Python Code Linter                     |

---

## Workspace Structure

- `modules/shared/src/` — Shared taxonomy domain modules (`taxonomy_<concern>_<role>.py`)
- `blender_mcp_addon/` — Blender addon (TCP server)
