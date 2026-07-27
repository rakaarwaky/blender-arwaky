#!/usr/bin/env bash
set -euo pipefail

ROOT="/home/raka/mcp-arwaky/blender-arwaky"
STOPFILE="$ROOT/.agents/loop/STOP"
LOGDIR="$ROOT/.agents/loop"
RUNLOG="$LOGDIR/run.log"
WRAPPERLOG="$LOGDIR/wrapper.log"

mkdir -p "$LOGDIR"

cd "$ROOT"

export QWEN_CODE_UNATTENDED_RETRY=1
export QWEN_CODE_CRON_MAX_AGE_DAYS=0

PROMPT='
Continue the Blender Arwaky autonomous engineering loop.

Project root:
/home/raka/mcp-arwaky/blender-arwaky/

Rules:
- Never modify FRD.
- Never add scope.
- Always align with FRD and ARCHITECTURE.md.
- Use Spec-Driven Development, Skill-Driven Development, and Test-Driven Development.
- Production-ready only.
- Replace dummy/stub/placeholder/TODO code with real tested implementation when required by FRD.
- Never trust completion.
- If no obvious implementation work remains, do regression, security, performance, architecture, documentation, and production-readiness audits.
- Update .agents/loop/STATE.md, TODO.md, DONE.md, QUESTIONS.md, ASSUMPTIONS.md, AUDIT.md, HEARTBEAT.md.
- If .agents/loop/STOP exists, print ARWAKY LOOP STOPPED BY USER and do nothing else.
- Otherwise, pick the next highest-priority FRD-aligned production-readiness gap and work on it.
- Do not ask for permission to continue.
- End this run with a short heartbeat and NEXT_ACTION.
'

while [[ ! -f "$STOPFILE" ]]; do
  echo "[$(date)] Starting qwen headless loop" >> "$WRAPPERLOG"

  qwen --continue \
    -p "$PROMPT" \
    --approval-mode auto \
    --output-format stream-json \
    >> "$RUNLOG" 2>&1 || true

  echo "[$(date)] qwen exited, restarting in 10s" >> "$WRAPPERLOG"
  sleep 10
done

echo "[$(date)] STOP file detected, wrapper exiting" >> "$WRAPPERLOG"
