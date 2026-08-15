# BlenderArwaky — AGENT.md

> See [ARCHITECTURE.md](ARCHITECTURE.md) for full AES architecture specification, layer rules, and component roles.

## Project Overview

BlenderArwaky connects **Blender 3D** to AI agents over the Model Context Protocol (MCP). Python 3.10+, FastMCP, Blender 5.1+, AES Architecture

---

## Quick Commands


| Command                                      | Purpose                                    |
| ---------------------------------------------- | -------------------------------------------- |
| `uv run blender-mcp`                         | Start MCP Server                           |
| `uv run blender-arwaky`                      | Run CLI Mode                               |
| `uv run pytest`                              | Run Test Suite                             |
| `bash scripts/ci.sh`                         | Run all local quality and build gates      |
| `lint-arwaky-cli scan .`                     | Run AES Architecture Linter (`lac scan .`) |
| `uv run ruff check modules blender_mcp_addon scripts` | Run Python Code Linter               |

---

## Workspace Structure

- `modules/` Blender MCP + CLI
- `blender_mcp_addon/` — Blender addon (TCP server)
