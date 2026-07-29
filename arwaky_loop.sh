#!/usr/bin/env bash
set -euo pipefail

ROOT="/home/raka/mcp-arwaky/blender-arwaky"
LOOPDIR="$ROOT/.agents/loop"
STOPFILE="$LOOPDIR/STOP"
PROMPT_FILE="$LOOPDIR/arwaky-loop-prompt.txt"
RUNLOG="$LOOPDIR/run.log"
WRAPPERLOG="$LOOPDIR/wrapper.log"
LOCKFILE="$LOOPDIR/arwaky_loop.lock"
PIDFILE="$LOOPDIR/arwaky_loop.pid"

mkdir -p "$LOOPDIR"

# Prevent multiple wrapper instances
exec 9>"$LOCKFILE"
if ! flock -n 9; then
  echo "[$(date)] Another arwaky_loop.sh is already running" >> "$WRAPPERLOG"
  exit 1
fi

echo $$ > "$PIDFILE"

cd "$ROOT"

export QWEN_CODE_UNATTENDED_RETRY=1
export QWEN_CODE_CRON_MAX_AGE_DAYS=0

if [[ ! -f "$PROMPT_FILE" ]]; then
  echo "[$(date)] ERROR: prompt file not found: $PROMPT_FILE" >> "$WRAPPERLOG"
  exit 1
fi

PROMPT="$(cat "$PROMPT_FILE")"

echo "[$(date)] arwaky_loop.sh started" >> "$WRAPPERLOG"

while [[ ! -f "$STOPFILE" ]]; do
  START_TS=$(date +%s)

  echo "[$(date)] Starting qwen headless loop" >> "$WRAPPERLOG"

  qwen --continue \
    -p "$PROMPT" \
    --approval-mode auto \
    --output-format stream-json \
    >> "$RUNLOG" 2>&1 || true

  END_TS=$(date +%s)
  DURATION=$((END_TS - START_TS))

  echo "[$(date)] qwen exited after ${DURATION}s" >> "$WRAPPERLOG"

  # If qwen exits too fast, avoid crash-loop spam
  if [[ "$DURATION" -lt 30 ]]; then
    echo "[$(date)] qwen exited too fast, sleeping 60s" >> "$WRAPPERLOG"
    sleep 60
  else
    sleep 10
  fi
done

echo "[$(date)] STOP file detected, wrapper exiting" >> "$WRAPPERLOG"
rm -f "$PIDFILE"
