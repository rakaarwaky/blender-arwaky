# BlenderArwaky — Testing Guide

## Quick Start

```bash
cd /path/to/blender-arwaky
uv run pytest
```

---

## Test Structure

```
modules/<feature>/tests/
  test_*.py       # Tests colocated with the owning feature module

Markers remain available for targeted suites: unit, integration, functional, addon, and slow.
```

## Running Tests

### Full suite with coverage

```bash
uv run pytest
```

### Specific test file

```bash
uv run pytest modules/dispatcher/tests/test_dispatcher_catalog_registration.py -v
```

### Specific test function

```bash
uv run pytest modules/mcp/tests/test_issue198_runtime.py -v
```

### With verbose output

```bash
uv run pytest -v --tb=short
```

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
2. MCP server started: `uv run blender-mcp`

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
    args={"view_angle": "TOP", "shading_mode": "WIREFRAME"}
)
# Expect: screenshot PNG bytes
```

---

## Linting

```bash
# Ruff linter
uv run ruff check modules blender_mcp_addon scripts

# Auto-fix
uv run ruff check modules blender_mcp_addon scripts --fix
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

1. Add a `test_*.py` file under the owning feature's `modules/<feature>/tests/` directory
2. Use `test_` prefix for function/file names
3. Mock external dependencies (API calls, Blender socket)
4. Add to appropriate `@pytest.mark` category
5. Verify coverage: `uv run pytest --cov=modules --cov=blender_mcp_addon`

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
