---
description: Autonomous FRD-aligned production-readiness loop for Blender Arwaky
---

You are running a continuous autonomous engineering loop for Blender Arwaky.

Project root:
/home/raka/mcp-arwaky/blender-arwaky/

FRD references:
/home/raka/mcp-arwaky/blender-arwaky/modules/asset/FRD.md
/home/raka/mcp-arwaky/blender-arwaky/modules/cli/FRD.md
/home/raka/mcp-arwaky/blender-arwaky/modules/config/FRD.md
/home/raka/mcp-arwaky/blender-arwaky/modules/diagnostics/FRD.md
/home/raka/mcp-arwaky/blender-arwaky/modules/dispatcher/FRD.md
/home/raka/mcp-arwaky/blender-arwaky/modules/gateway/FRD.md
/home/raka/mcp-arwaky/blender-arwaky/modules/job/FRD.md
/home/raka/mcp-arwaky/blender-arwaky/modules/launcher/FRD.md
/home/raka/mcp-arwaky/blender-arwaky/modules/mcp/FRD.md
/home/raka/mcp-arwaky/blender-arwaky/modules/object/FRD.md
/home/raka/mcp-arwaky/blender-arwaky/modules/scene/FRD.md
/home/raka/mcp-arwaky/blender-arwaky/modules/render/FRD.md
/home/raka/mcp-arwaky/blender-arwaky/modules/security/FRD.md
/home/raka/mcp-arwaky/blender-arwaky/modules/telemetry/FRD.md

Architecture:
/home/raka/mcp-arwaky/blender-arwaky/ARCHITECTURE.md

Agent skills:
/home/raka/mcp-arwaky/blender-arwaky/.agents/skills/

Agent rules:
/home/raka/mcp-arwaky/blender-arwaky/.agents/rules/

Loop state directory:
/home/raka/mcp-arwaky/blender-arwaky/.agents/loop/

STOP FILE:
If /home/raka/mcp-arwaky/blender-arwaky/.agents/loop/STOP exists, do only this:
1. Print: ARWAKY LOOP STOPPED BY USER
2. Do not modify code.
3. Do not run tests.
4. Do not continue.
5. End immediately.

If STOP file does not exist, continue the autonomous engineering loop.

NON-NEGOTIABLE RULES:
1. Never modify any FRD.
2. Never add scope outside FRD.
3. Never invent new features.
4. Always align with FRD and ARCHITECTURE.md.
5. Use Spec-Driven Development.
6. Use Skill-Driven Development.
7. Use Test-Driven Development.
8. Production-ready only.
9. Replace dummy/stub/placeholder/TODO code with real tested implementation when required by FRD.
10. Never trust completion. Always look for remaining gaps.
11. Do not ask the user for permission to continue.
12. Continue until the STOP file exists or the user explicitly stops the session.

WORK METHOD:
Each cycle must do:

1. Read loop state:
   - .agents/loop/STATE.md
   - .agents/loop/TODO.md
   - .agents/loop/DONE.md
   - .agents/loop/QUESTIONS.md
   - .agents/loop/ASSUMPTIONS.md
   - .agents/loop/AUDIT.md
   - .agents/loop/HEARTBEAT.md

2. Select one highest-priority target:
   Priority order:
   1. Failing tests.
   2. Broken functionality.
   3. FRD requirement not fully implemented.
   4. Dummy/stub/placeholder function that must become real.
   5. Security issue.
   6. Potential bug.
   7. Performance issue.
   8. Missing regression test.
   9. Missing error handling.
   10. Missing diagnostics/telemetry required by FRD.
   11. Documentation mismatch.
   12. Maintainability/refactoring risk.
   13. Hardening and edge-case coverage.

3. Before changing code, answer:
   - Which FRD file is involved?
   - Which requirement is involved?
   - Is this strictly inside FRD scope?
   - Does this align with ARCHITECTURE.md?
   - Does this follow .agents/rules/?
   - Does this reuse .agents/skills/?

4. Use TDD:
   - Write failing test first.
   - Implement minimal correct code.
   - Run tests.
   - Refactor only if tests remain green.

5. After implementation, run skeptical audit:
   - Is this truly aligned with FRD?
   - Did I accidentally add scope?
   - Is there any hidden performance issue?
   - Is there any potential bug?
   - Is there any unimplemented function?
   - Is there any dummy function pretending to work?
   - Is there any missing validation?
   - Is there any unsafe error path?
   - Is there any missing logging/telemetry/diagnostics?
   - Is there any security weakness?
   - Is there any missing edge case?
   - Is there any missing test?
   - Is this production-ready?

6. If no obvious implementation work remains, do audit work:
   - full regression sweep,
   - cross-module integration audit,
   - security audit,
   - performance audit,
   - error-handling audit,
   - telemetry/diagnostics audit,
   - documentation consistency audit,
   - architecture boundary audit,
   - test coverage gap audit,
   - dependency risk audit,
   - production failure scenario simulation.

7. Update loop state files:
   - STATE.md: current cycle and current focus
   - TODO.md: next concrete actions
   - DONE.md: completed work
   - QUESTIONS.md: FRD ambiguities
   - ASSUMPTIONS.md: chosen safe assumptions
   - AUDIT.md: skeptical findings
   - HEARTBEAT.md: timestamped heartbeat

8. Output a short heartbeat:

CYCLE:
TARGET MODULE:
FRD REFERENCE:
SCOPE CHECK:
CHANGE SUMMARY:
TESTS ADDED/UPDATED:
TEST RESULT:
RISKS FOUND:
DUMMY/STUB FOUND:
SECURITY NOTES:
PERFORMANCE NOTES:
REMAINING DOUBTS:
NEXT ACTION:
STATUS: CONTINUE

Never declare final completion.
Never stop unless STOP file exists or user explicitly stops the session.
