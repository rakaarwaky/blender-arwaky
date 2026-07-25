# BlenderArwaky

**Connect Blender to AI agents through the Model Context Protocol.**

BlenderArwaky bridges [Blender 3D](https://www.blender.org/) with any MCP-compatible client — Claude Desktop, Cursor, Continue.dev, or custom agents. Control scenes, import assets, render, and execute Blender Python through 4 universal MCP tools.

[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Blender 3.0+](https://img.shields.io/badge/Blender-3.0%2B-orange.svg)](https://www.blender.org/)

---

## Features

- **4 Universal MCP Tools** — Minimal surface, maximum power via command catalog dispatch
- **15+ Actions** — Scene ops, object manipulation, rendering, import/export, code execution
- **2 Asset Providers** — Poly Haven (HDRI/textures/models), Sketchfab
- **AI-Optimized Screenshots** — View presets, shading modes, overlay control, object focus
- **Blender Addon** — TCP server with auto-start and UI panel
- **Clean Architecture** — AES 7-layer architecture with full dependency inversion

---

## Quick Start

### Prerequisites

- **Blender 3.0+** (tested on 5.1)
- **Python 3.10+**

### Install

```bash
git clone https://github.com/rakaarwaky/blender-arwaky.git
cd blender-arwaky
uv sync
```

### Install Blender Addon

1. Blender → Edit → Preferences → Add-ons
2. Install `blender_mcp_addon/` directory
3. Enable **"Interface: Blender Arwaky"**

### Start MCP Server

```bash
uv run python -m surfaces.mcp_server_entry
```

### Configure MCP Client

```json
{
  "mcpServers": {
    "blender-arwaky": {
      "command": "uv",
      "args": ["--directory", "/path/to/blender-arwaky", "run", "blender-arwaky"]
    }
  }
}
```

---

## Configuration

```yaml
blender:
  executable_path: "/path/to/blender"
  host: "localhost"
  port: 9876

server:
  transport: "stdio"    # or "sse"
  log_dir: "log"
```

| Env Var | Description |
|---------|-------------|
| `BLENDERMCP_CONFIG_PATH` | Override config.yaml path |
| `BLENDER_HOST` | Override Blender host |
| `BLENDER_PORT` | Override Blender port |

---

## Project Structure

```
blender-arwaky/
├── modules/
│   └── shared/
│       └── src/            # Shared taxonomy modules (taxonomy_<concern>_<role>.py)
├── src/
│   ├── surfaces/          # MCP tools & entry points
│   ├── agent/             # DI container & orchestrators
│   ├── capabilities/      # Business logic & adapters
│   ├── contract/          # Protocols & aggregate interfaces
│   └── taxonomy/          # Barrel re-exports of domain models
├── blender_mcp_addon/     # Blender addon (TCP server)
├── tests/                 # Unit, integration, functional tests
└── docs/                  # Documentation (AGENT, SKILL, TEST)
```

---

## Testing & Architecture Quality Gates

```bash
uv run pytest              # Full suite (455+ tests)
uv run pytest -m unit      # Unit tests only
lint-arwaky-cli scan .     # AES architecture compliance scan (or `lac scan .`)
uv run ruff check src/     # Code style & linting
```

---

## Documentation

- [ARCHITECTURE.md](ARCHITECTURE.md) — System architecture & AES 7-layer specification
- [SKILL.md](SKILL.md) — Agent usage reference (tools, commands, workflows)
- [AGENT.md](AGENT.md) — Quick developer reference
- [TEST.md](TEST.md) — Testing guide

---

## License

[MIT License](LICENSE) — Originally by Siddharth Ahuja, extended by Raka Arwaky.
