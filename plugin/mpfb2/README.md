# MPFB 2 Plugin Provider

This directory contains the optional MPFB 2 provider for Blender Arwaky. It is intentionally outside `modules/` because it is provider-specific extension code rather than AES core code.

The provider currently defines the global plugin contract, manifest metadata, one planned `character.create` capability, and bounded not-implemented behavior. It does not copy MPFB 2 source code, bundle MPFB 2 assets, import the external add-on at module import time, or accept arbitrary Blender Python.

The next integration wave will add runtime detection inside Blender, compatibility probing, operation mapping, result normalization, and an integration smoke test with MPFB 2 installed and enabled.
