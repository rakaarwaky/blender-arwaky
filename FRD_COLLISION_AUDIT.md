# FRD Collision Audit

## Date: 2026-07-25

### 1. ID Collisions (All modules use FR-001..N)

Every module uses sequential FR-XXX IDs starting from 001. This causes ambiguity when referencing features across modules.

**Fix**: Prefix IDs with module abbreviation (e.g., `OBJ-001`, `SRV-001`, `AST-001`).

### 2. Feature Name Collisions

| Module A | Feature | Module B | Feature | Overlap |
|----------|---------|----------|---------|---------|
| object | FR-009: Blender Socket Connection | server | FR-001: Manage Blender Socket Connection | HIGH — same TCP connection |
| object | FR-008: Import/Export 3D Models | asset | FR-002: Fetch and Import Asset | HIGH — both import into Blender |
| render | FR-005: Multi-Provider Asset Search | asset | FR-001: Search Assets Across Providers | HIGH — same search |
| render | FR-006: Asset Provider Integration | asset | FR-003/004/005/006 | HIGH — provider adapters |
| cli | FR-003: Capture Screenshot | render | FR-001: Get Viewport Screenshot | MEDIUM — same operation |
| cli | FR-004: Render Image | render | FR-002: Render Image | HIGH — same operation |
| cli | FR-002: Launch Blender | server | FR-001: Manage Blender Socket Connection | MEDIUM — server lifecycle |
| scene | FR-005: Setup Expert Orchestrator | render | FR-007/008: Expert Orchestrators | MEDIUM — orchestration overlap |
| mcp | Duplicate entries (appears twice) | — | — | FILE ISSUE |

### 3. Recommended Ownership

| Feature | Owner Module | Rationale |
|---------|--------------|-----------|
| Blender TCP connection | **server** | Server owns socket lifecycle |
| Blender code execution | **server** | Server executes via socket |
| Asset search/download | **asset** | Asset owns provider integration |
| Import into Blender | **object** | Object owns scene placement |
| Viewport screenshot | **render** | Render owns camera/viewport |
| Render image | **render** | Render owns rendering |
| Launch/close Blender | **cli** | CLI manages Blender process |
| Scene setup/cleanup | **scene** | Scene owns environment |
| MCP tools | **mcp** | MCP owns tool registration |
| Config loading | **config** | Config owns settings |
| Telemetry | **telemetry** | Telemetry owns events |
| Job tracking | **job** | Job owns state management |

### 4. Files to Fix

- [ ] `modules/object/FRD.md` — Remove FR-009 (socket → server), FR-008 (import → clarify scope)
- [ ] `modules/render/FRD.md` — Remove FR-005/006 (asset search → asset), FR-007/008 (orchestrators → shared)
- [ ] `modules/scene/FRD.md` — Remove FR-005 (orchestrator → shared)
- [ ] `modules/cli/FRD.md` — Remove FR-003/004 (screenshot/render → render), clarify FR-002
- [ ] `modules/mcp/FRD.md` — Remove duplicate file content
- [ ] All FRDs — Prefix IDs with module abbreviation
