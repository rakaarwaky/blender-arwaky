# Wave 6 Open-Source Rigging Provider Research Notes

## Initial findings

| Candidate | Evidence observed | Initial assessment |
|---|---|---|
| Rigify | Blender 5.2 LTS Manual lists it as automatic rigging from building-block components, GPL, bundled with Blender; current manual updated 2026-08-16 | Strongest default candidate for Arwaky because it is bundled, GPL, version-aligned, and avoids a separate addon download lifecycle |
| CloudRig | Official Blender Extensions page lists CloudRig 2.2.27 on 2026-08-11, Blender Studio maintainer, Blender 5.0, GPLv3-or-later; official repo shows active commits and production-oriented metarig workflow | Strong production/pipeline candidate, but separate extension and more Blender Studio-specific |
| BlenRig 6 | Official GitHub repository shows GPL-3.0, 163 stars, 983 commits, Blender 4.0+ release notes, biped auto-rigging/skinning, feature-film quality rig and advanced facial system | Strong deformation-quality candidate, but smaller ecosystem and less direct Blender 5.2 official integration evidence |

## Key official sources

1. https://docs.blender.org/manual/en/latest/addons/rigify/index.html — Blender 5.2 LTS Rigify manual.
2. https://developer.blender.org/docs/features/animation/rigify/ — Blender Developer Documentation for Rigify.
3. https://extensions.blender.org/add-ons/cloudrig/ — Blender Extensions CloudRig page.
4. https://projects.blender.org/Mets/CloudRig — CloudRig source repository.
5. https://github.com/jpbouza/BlenRig — BlenRig source repository.

## Provisional conclusion

For Arwaky's default open-source rigging provider, Rigify is provisionally number one because it is bundled with Blender 5.2, GPL-licensed, documented by Blender, and has no separate plugin download dependency. CloudRig is the strongest production-oriented alternative, while BlenRig 6 is the strongest candidate when deformation quality and facial rig features are weighted above ecosystem and version integration.

## Additional verified observations

CloudRig's official Blender Extensions page lists version 2.2.27 dated 2026-08-11, Blender Studio as maintainer, Blender 5.0 support, GPLv3-or-later, and Rigging category. Its description says it generates helper bones, constraints, and drivers from a metarig; the official source repository shows 3,132 commits and active changes in August 2026.

BlenRig's official GitHub page describes BlenRig 6 Beta as an auto-rigging and skinning system with a feature-film-quality rig, advanced facial system, deformation cage/lattices, and automatic weight-transfer meshes. The repository is GPL-3.0, has 163 stars and 983 commits, but its stated latest release notes are for Blender 4.0/4.4 and it currently supports biped characters only.

The Blender 5.2 LTS manual describes Rigify as automatic rigging from building-block components, GPL licensed, bundled with Blender. Its workflow uses metarigs and generated controls, making it the lowest-dependency option for Arwaky.
