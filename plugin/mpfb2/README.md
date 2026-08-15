# MPFB 2 Provider

This directory is the optional MPFB 2 provider for Blender Arwaky. It is outside `modules/` because it contains provider-specific integration code rather than AES core code.

The provider currently implements the shared plugin operation contract, manifest metadata, compatibility checks, optional installation state, capability allow-listing, and bounded results. It does not copy MPFB 2 source code or assets and does not register MCP tools or CLI shortcuts.

Live Blender discovery and the first real MPFB 2 operation require a later integration wave with MPFB 2 installed and enabled in a disposable Blender environment.
