# syntax=docker/dockerfile:1.7
# Blender Arwaky MCP Server — containerized deployment
#
# Build:   docker build -t blender-arwaky .
# Run:     docker run -i --rm blender-arwaky
# Config:  Mount your config.yaml:  -v $(pwd)/config.yaml:/app/config.yaml:ro
#          Set env:                  -e BLENDERMCP_CONFIG_PATH=/app/config.yaml
#                                    -e BLENDER_HOST=host.docker.internal
#
# This image runs the MCP server (stdio transport). It does NOT include
# Blender itself — the Blender addon runs in your local Blender and
# connects to the MCP server over network.

# ─── Stage 1: Build ─────────────────────────────────────────────────────────
FROM python:3.12-slim AS builder

# uv for fast, deterministic installs
COPY --from=ghcr.io/astral-sh/uv:0.11.0 /uv /uvx /usr/local/bin/

WORKDIR /build

# Install build deps
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy project files
COPY pyproject.toml uv.lock README.md ./
COPY src ./src
COPY config.example.yaml ./config.example.yaml 2>/dev/null || true

# Install dependencies (no dev deps in production image)
RUN uv sync --no-dev --no-install-project && \
    uv pip install --no-deps .

# ─── Stage 2: Runtime ───────────────────────────────────────────────────────
FROM python:3.12-slim AS runtime

# Labels for image metadata
LABEL org.opencontainers.image.title="Blender Arwaky"
LABEL org.opencontainers.image.description="MCP server for Blender 3D — AI agent integration"
LABEL org.opencontainers.image.source="https://github.com/rakaarwaky/blender-arwaky"
LABEL org.opencontainers.image.licenses="MIT"
LABEL org.opencontainers.image.authors="Raka Arwaky"

# Install uv in runtime for any post-install hooks
COPY --from=ghcr.io/astral-sh/uv:0.11.0 /uv /uvx /usr/local/bin/

# Create non-root user
RUN groupadd --system --gid 1000 arwaky && \
    useradd --system --uid 1000 --gid arwaky --create-home --shell /bin/bash arwaky

WORKDIR /app

# Copy installed packages from builder
COPY --from=builder --chown=arwaky:arwaky /build/.venv /app/.venv
COPY --from=builder --chown=arwaky:arwaky /build/src /app/src
COPY --from=builder --chown=arwaky:arwaky /build/pyproject.toml /app/
COPY --from=builder --chown=arwaky:arwaky /build/README.md /app/
COPY --from=builder --chown=arwaky:arwaky /build/CHANGELOG.md /app/
COPY --from=builder --chown=arwaky:arwaky /build/SECURITY.md /app/

# Make sure the venv is on PATH
ENV PATH="/app/.venv/bin:$PATH" \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONFAULTHANDLER=1 \
    BLENDER_HOST=host.docker.internal \
    BLENDER_PORT=9876

USER arwaky

# Health check (optional — only useful for SSE transport)
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD python -c "import blender_arwaky" || exit 1

# Default command runs the MCP server (stdio transport for MCP clients)
ENTRYPOINT ["blender-arwaky"]

# Expose port for SSE transport (optional — stdio is the default)
EXPOSE 9877
