#!/usr/bin/env bash
# Local CI script — runs the same checks as GitHub Actions
set -euo pipefail

cd "$(dirname "$0")/.."

echo "=== BlenderArwaky Local CI ==="
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

passed=0
failed=0

run_check() {
    local name="$1"
    shift
    echo -e "${YELLOW}▸ ${name}${NC}"
    if "$@"; then
        echo -e "${GREEN}  ✓ passed${NC}"
        ((passed++))
    else
        echo -e "${RED}  ✗ failed${NC}"
        ((failed++))
    fi
    echo ""
}

# 1. Ruff lint
run_check "Ruff lint" uv run ruff check src/ blender_mcp_addon/

# 2. Ruff format
run_check "Ruff format" uv run ruff format --check src/ blender_mcp_addon/

# 3. Tests
run_check "Tests" uv run pytest tests/ -q --tb=short

# Summary
echo "=== Summary ==="
echo -e "${GREEN}Passed: ${passed}${NC}"
if [ "$failed" -gt 0 ]; then
    echo -e "${RED}Failed: ${failed}${NC}"
    exit 1
else
    echo -e "${GREEN}All checks passed!${NC}"
fi
