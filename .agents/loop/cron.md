# Cron Setup Guide — 4-Phase AES Pipeline

## Overview

The AES pipeline is split into **4 separate cron jobs**, each running **15 minutes apart**:

| Cron # | Role | Cron Expression | Time (example) | Prompt File |
|--------|------|-----------------|----------------|-------------|
| #1 | Architect | `0 5 * * *` | 05:00 | `.agents/loop/architect-prompt.md` |
| #2 | Business Analyst | `15 5 * * *` | 05:15 | `.agents/loop/business-analyst-prompt.md` |
| #3 | Tech Lead | `30 5 * * *` | 05:30 | `.agents/loop/tech-lead-prompt.md` |
| #4 | Fullstack Developer | `45 5 * * *` | 05:45 | `.agents/loop/fullstack-developer-prompt.md` |

## How to Setup

Use **CronCreate** tool 4 times. Each cron fires a prompt that tells the agent to read its corresponding file and execute it as the role's task.

### Cron #1 — Architect (05:00)

```
cron: "0 5 * * *"
prompt: "Read .agents/loop/architect-prompt.md and execute it as the Architect role. Identify the oldest unprocessed feature (by report timestamp), create an architectural plan in .agents/plans/todo-<feature-name>-architect-<timestamp>.md"
recurring: true
durable: true
```

### Cron #2 — Business Analyst (05:15)

```
cron: "15 5 * * *"
prompt: "Read .agents/loop/business-analyst-prompt.md and execute it as the Business Analyst role. Identify the oldest unprocessed feature (by report timestamp), create a business analysis plan in .agents/plans/todo-<feature-name>-business-analyst-<timestamp>.md"
recurring: true
durable: true
```

### Cron #3 — Tech Lead (05:30)

```
cron: "30 5 * * *"
prompt: "Read .agents/loop/tech-lead-prompt.md and execute it as the Tech Lead role. Identify the oldest unprocessed feature (by report timestamp), create a code quality plan in .agents/plans/todo-<feature-name>-tech-lead-<timestamp>.md"
recurring: true
durable: true
```

### Cron #4 — Fullstack Developer (05:45)

```
cron: "45 5 * * *"
prompt: "Read .agents/loop/fullstack-developer-prompt.md and execute it as the Fullstack Developer role. Aggregate all plans from Architect, Business Analyst, and Tech Lead. Execute all 3 plans, delete them, generate a single consolidated report in .agents/reports/done-<feature-name>-fullstack-developer-<timestamp>.md"
recurring: true
durable: true
```

## Feature Selection Priority (All Planner Roles)

Each planner role (Architect, Business Analyst, Tech Lead) follows this priority:

1. Look for unprocessed features under `modules/`, `crates/`, or `packages/`
2. Pick one feature that has an FRD.md but **no report** in `.agents/reports/`
3. If all features have reports, pick the **oldest feature by report timestamp** and run again

## How It Works

1. **05:00** — Architect creates `*-architect-*.md` plan
2. **05:15** — Business Analyst creates `*-business-analyst-*.md` plan
3. **05:30** — Tech Lead creates `*-tech-lead-*.md` plan
4. **05:45** — Fullstack Developer reads all 3 plans, executes them, deletes them, generates 1 consolidated report

This cycle repeats every day. Each phase respects the 15-minute gap so plans are created before execution.

## Stopping the Pipeline

Create a STOP file:
```bash
touch .agents/loop/STOP
```

Each role checks for this file and exits cleanly if found.
