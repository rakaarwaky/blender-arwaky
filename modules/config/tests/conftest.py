"""Shared test fixtures for the config feature test suite.

The project's top-level ``modules.shared.src.__init__`` is currently broken
(missing ``mcp`` subpackage) and cannot be imported. To keep the config test
suite runnable in isolation, we inject lightweight ``mcp`` namespace modules
into ``sys.modules`` (built purely from path strings, without importing
``modules.shared.src``) so the aggregate re-export resolves.
"""

from __future__ import annotations

import importlib.util
import sys
import types
from pathlib import Path

# Ensure repo root (which contains the ``modules`` package) is importable.
ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

# Shim the broken ``modules.shared.src.mcp`` namespace BEFORE importing shared.
# Built from path strings only — we must NOT import modules.shared.src yet,
# because its __init__ triggers the broken ``.mcp`` import.
_SHARED_SRC_NAME = "modules.shared.src"
_MCP_MODULE_NAME = "modules.shared.src.mcp"
_BOOTSTRAP_MODULE_NAME = "modules.shared.src.mcp.contract_mcp_bootstrap_protocol"
if _MCP_MODULE_NAME not in sys.modules:
    shared_init = ROOT / "modules" / "shared" / "src" / "__init__.py"
    assert shared_init.exists(), "modules.shared.src.__init__ not found"
    spec = importlib.util.spec_from_file_location(_SHARED_SRC_NAME, str(shared_init))
    assert spec is not None and spec.submodule_search_locations is not None
    shared_loc = list(spec.submodule_search_locations)[0]

    mcp_pkg = types.ModuleType(_MCP_MODULE_NAME)
    mcp_pkg.__path__ = [str(Path(shared_loc) / "mcp")]
    sys.modules[_MCP_MODULE_NAME] = mcp_pkg

    bootstrap = types.ModuleType(_BOOTSTRAP_MODULE_NAME)
    bootstrap.ServerBootstrapManagerAggregate = object  # shim placeholder
    sys.modules[_BOOTSTRAP_MODULE_NAME] = bootstrap
