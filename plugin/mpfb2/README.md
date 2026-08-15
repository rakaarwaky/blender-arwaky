# MPFB 2 Provider

This directory is the optional MPFB 2 provider for Blender Arwaky. It is outside `modules/` because it contains provider-specific integration code rather than AES core code.

The provider currently implements the shared plugin operation contract, manifest metadata, compatibility checks, optional installation state, capability allow-listing, and bounded results. It does not copy MPFB 2 source code or assets and does not register MCP tools or CLI shortcuts.

Runtime discovery now reads only public Blender runtime attributes (`bpy.app.version` and the enabled add-on registry). It does not import MPFB2 internals. A live smoke test on the available Blender 4.0.2 environment correctly reported MPFB2 as unavailable because the add-on was not installed and Blender is below the provider's 4.2 baseline.

The first real MPFB 2 operation still requires a later integration wave with MPFB 2 installed and enabled in a disposable Blender environment.
