# MPFB2 Runtime Discovery Findings

Date: 2026-08-15

## Official sources

- Repository: https://github.com/makehumancommunity/mpfb2
- Getting started: https://static.makehumancommunity.org/mpfb/docs/getting_started.html
- Blender Extensions listing: https://extensions.blender.org/add-ons/mpfb/

## Findings

1. MPFB2 is a Blender add-on distributed through the Blender Extensions platform and as an add-on ZIP.
2. MPFB2 2.x requires Blender 4.2 or newer.
3. The official documentation describes installation through Blender Preferences > Extensions and says the add-on creates an MPFB tab in the N-panel when available.
4. The public feature surface includes human creation, parametric body modeling, automatic rigging, Rigify support, IK/FK, procedural skin and eye materials, and an asset library.
5. The official public pages do not specify a stable Python import module or a stable internal operator API for external integrations.
6. The safe first integration is therefore an environment probe and capability/health boundary. It must not assume a module name, import private MPFB internals, or execute an operation until a concrete supported API is verified.
7. The provider must remain optional. Missing, inactive, or incompatible MPFB2 must return a normalized state and must not prevent Blender Arwaky startup.
8. The official extension listing reports MPFB 2.0.17, Blender 4.2 LTS and newer compatibility, and GPLv3-or-later licensing. Licensing must be reviewed before any bundling or redistribution; this plan does not bundle MPFB2 source or assets.

## Integration consequence

The next implementation step should add a provider-neutral probe hook under the `plugin/mpfb2` boundary. The probe should accept runtime facts from the Blender host or a controlled adapter, normalize the state into existing taxonomy VOs, and leave actual MPFB2 operation mapping disabled until a stable supported API is identified and tested in Blender.
