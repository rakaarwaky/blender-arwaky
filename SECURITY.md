# Security Policy

## Supported Versions

The following versions of **Blender Arwaky** receive security updates:

| Version | Supported          |
|---------|--------------------|
| 1.6.x   | :white_check_mark: |
| < 1.6   | :x:                |

We follow semantic versioning. Security fixes will be backported to the
latest minor release branch.

## Reporting a Vulnerability

If you discover a security vulnerability in Blender Arwaky, **please report
it privately** rather than opening a public issue.

### How to report

Send an email to: **security@blenderarwaky.local**

Please include:

- A clear description of the vulnerability
- Steps to reproduce the issue
- The affected version(s)
- Potential impact and exploitation scenario
- Any known mitigations or workarounds

### What to expect

- **Acknowledgment** within 48 hours of your report
- **Initial assessment** within 7 days
- **Status updates** at least every 14 days until resolution
- A **CVE** will be requested for confirmed vulnerabilities (if applicable)
- **Credit** in the security advisory (unless you prefer to remain anonymous)

### Scope

The following are in scope for security reports:

- **MCP server** (`src/`) — Python code, dependency vulnerabilities
- **Blender addon** (`blender_mcp_addon/`) — code that runs inside Blender
- **Build & release pipeline** — `.github/workflows/`, `scripts/`
- **Configuration & data flow** — `config.yaml`, env var handling
- **Telemetry** — data collection, storage, opt-in/out mechanisms

### Out of scope

- The Blender application itself (report to blender.org)
- Third-party API providers (Poly Haven, Sketchfab, Hyper3D, Hunyuan3D)
  — report to the respective provider
- Issues in development dependencies not shipped with the package
- Denial-of-service attacks that require local code execution

## Security Best Practices

When using Blender Arwaky:

1. **API keys** — never commit API keys to the repository. Use `.env.blendermcp`
   (gitignored) or set them via environment variables.
2. **Telemetry** — telemetry is **opt-in** and disabled by default. You can
   toggle consent in the Blender addon's preferences panel.
3. **Network exposure** — the Blender addon TCP server defaults to
   `localhost:9876`. Do not expose this port to the public internet.
4. **Updates** — keep Blender Arwaky up-to-date. Subscribe to releases on
   GitHub to be notified of security patches.
5. **Code execution** — the `execute_blender_code` action runs arbitrary
   Python in Blender's `bpy` context. Only invoke it with trusted prompts
   or sanitized code.

## Security Features

Blender Arwaky includes the following security-conscious design choices:

- **No hardcoded secrets** in source code (verified by `bandit` in CI)
- **Env-var-based configuration** for all sensitive values
- **Opt-in telemetry** with anonymous UUID, no PII collected
- **No outbound network** except to explicitly configured providers
- **Sandboxed code execution** limited to Blender's `bpy` API
- **CI security scanning** via `bandit` and GitHub Dependabot
- **Signed releases** with GitHub attestations
- **Pinned dependency versions** in `pyproject.toml` with lower bounds

## Acknowledgments

We thank the following individuals for responsibly disclosing security
issues (none reported at this time).
