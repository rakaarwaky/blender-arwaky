# FRD Collision Audit

## Date: 2026-07-25

### Status: FIXED

### 1. ID Collisions — FIXED

All FRD IDs now prefixed with module abbreviation:
- AST-001..006 (asset)
- CLI-001..005 (cli)
- CFG-001..005 (config)
- JOB-001..005 (job)
- MCP-001..006 (mcp)
- OBJ-001..007 (object)
- RND-001..004 (render)
- SCN-001..004 (scene)
- SHR-001..007 (shared)
- TLM-001..004 (telemetry)

### 2. Feature Name Collisions — FIXED

| Collision | Resolution |
|-----------|------------|
| object/FR-009: Blender Socket Connection ↔ server/FR-001 | Removed from object, kept in server |
| object/FR-008: Import/Export ↔ asset/FR-002 | Removed from object, import belongs to asset |
| render/FR-005: Multi-Provider Asset Search ↔ asset/FR-001 | Removed from render, search belongs to asset |
| render/FR-006: Asset Provider Integration ↔ asset | Removed from render, providers belong to asset |
| cli/FR-003: Capture Screenshot ↔ render/FR-001 | Removed from cli, screenshot belongs to render |
| cli/FR-004: Render Image ↔ render/FR-002 | Removed from cli, render belongs to render |
| scene/FR-005: Setup Expert Orchestrator ↔ render/FR-007/008 | Removed from scene, orchestrators belong to agent layer |
| render/FR-007/008: Expert Orchestrators | Removed from render, belongs to agent layer |

### 3. Module Ownership Summary

| Feature | Owner | Module |
|---------|-------|--------|
| Blender TCP connection | server | modules/server/ |
| Blender code execution | server | modules/server/ |
| Asset search/download | asset | modules/asset/ |
| Import into Blender | asset | modules/asset/ |
| Object manipulation | object | modules/object/ |
| Viewport screenshot | render | modules/render/ |
| Render image | render | modules/render/ |
| Camera/HDRI setup | render | modules/render/ |
| Scene info/cleanup | scene | modules/scene/ |
| MCP tools | mcp | modules/mcp/ |
| CLI process management | cli | modules/cli/ |
| Config loading | config | modules/config/ |
| Telemetry events | telemetry | modules/telemetry/ |
| Job tracking | job | modules/job/ |
| Taxonomy/contracts | shared | modules/shared/ |
