# BlenderArwaky — Testing Guide

## Quick Start

```bash
cd /path/to/blender-arwaky
uv run pytest
```

455+ tests across unit, integration, and functional categories.

---

## Test Structure

```
tests/
  unit/           # Pure logic, data models, mocked interfaces
  integration/    # Layer interactions, DI wiring, service integration
  functional/     # End-to-end command flows within project boundaries
```

---

## Coverage Targets

| Layer | Target | Notes |
|-------|--------|-------|
| `taxonomy/` | 100% | Pure data — must be fully covered |
| `contract/` | 90% | Interface definitions |
| `capabilities/` | 90% | Business logic |
| `agent/` | 80% | Orchestration (where applicable) |
| `surfaces/` | 85% | Handlers |
| **Overall** | **85%** | minimum |

---

## Running Tests

### Full suite with coverage

```bash
uv run pytest
```

### Specific test file

```bash
uv run pytest tests/unit/test_command_catalog.py -v
```

### Specific test function

```bash
uv run pytest tests/integration/test_tool_registry.py::test_register_tools -v
```

### With verbose output

```bash
uv run pytest -v --tb=short
```

### Exclude slow tests

```bash
uv run pytest -m "not slow"
```

### Run by marker

```bash
uv run pytest -m unit       # only unit tests
uv run pytest -m "not slow" # skip slow tests
```

---

## Test Categories

### Unit Tests (`pytest -m unit`)

- Pure functions, data models, value objects
- No external dependencies (mocked)
- Fast: <10ms per test
- Examples: catalog parsing, config loading, serialization

### Integration Tests (`pytest -m integration`)

- Layer interactions: handler → capability → infrastructure
- Mock API calls, real DI container
- Medium: <500ms per test
- Examples: execute_command flow, DI wiring, socket message parsing

### Functional Tests (`pytest -m functional`)

- End-to-end within boundaries (no external services)
- Full command execution pipeline
- Slower: <2s per test
- Examples: create_primitive → scene update cycle

---

## Manual End-to-End Test

### Prerequisites

1. Blender running with addon enabled (server on port 9876)
2. MCP server started: `uv run python -m surfaces.mcp_server_entry`

### Test Steps

**Step 1: Health Check**
```python
health_check()
# Expect: blender_connected=true, tool_count=5
```

**Step 2: Scene Discovery**
```python
execute_command(action="get_scene_info")
# Expect: JSON with scene_name, object_count, frame info
```

**Step 3: Create Object**
```python
execute_command(
    action="create_primitive",
    args={"primitive_type": "SPHERE", "location": [0, 0, 0]}
)
# Expect: success message with object name
```

**Step 4: AI-Optimized Screenshot**
```python
execute_command(
    action="get_viewport_screenshot",
    args={"view_angle": "TOP", "shading": "WIREFRAME"}
)
# Expect: screenshot PNG bytes
```

---

## Linting

```bash
# Ruff linter
uv run ruff check src/ blender_mcp_addon/

# Auto-fix
uv run ruff check src/ --fix
```

---

## Common Test Failures

### ImportError: circular import

**Cause:** Module imports from barrel (`__init__.py`) that imports back.
**Fix:** Import directly from source file, not from barrel.

### Blender connection tests fail

**Cause:** No Blender running with addon.
**Fix:** Mark with `@pytest.mark.integration` and skip if no Blender.

### Coverage drops

**Cause:** New code without tests.
**Fix:** Write tests for new code before merging. Run `--cov-report=html`
and open `htmlcov/index.html` to see uncovered lines.

---

## Writing New Tests

1. Add test file in `tests/unit/`, `tests/integration/`, or `tests/functional/`
2. Use `test_` prefix for function/file names
3. Mock external dependencies (API calls, Blender socket)
4. Add to appropriate `@pytest.mark` category
5. Verify coverage: `uv run pytest --cov=<module> tests/`

**Template:**

```python
"""Tests for <module_name>."""
import pytest


def test_<function_name>():
    """<description of what's being tested>."""
    # Arrange
    # Act
    # Assert
```
