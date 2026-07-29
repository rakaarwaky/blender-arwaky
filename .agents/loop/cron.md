# Cron Setup Guide — 4-Phase AES Pipeline

## Overview

The AES pipeline is split into **4 separate cron jobs**, each running **15 minutes apart**:


| Cron # | Role                | Cron Expression | Output Files                                              |
| -------- | --------------------- | ----------------- | ----------------------------------------------------------- |
| #1     | Architect           | `0 * * * *`     | `todo-<feature>-architect-YYYY-MM-DD-HHmmss.md`           |
| #2     | Business Analyst    | `15 * * * *`    | `todo-<feature>-business-analyst-YYYY-MM-DD-HHmmss.md`    |
| #3     | Tech Lead           | `30 * * * *`    | `todo-<feature>-tech-lead-YYYY-MM-DD-HHmmss.md`           |
| #4     | Fullstack Developer | `45 * * * *`    | `done-<feature>-fullstack-developer-YYYY-MM-DD-HHmmss.md` |

## How to Setup

Use **CronCreate** tool 4 times. Each cron fires a prompt that tells the agent to read its corresponding file and execute it as the role's task.

### Cron #1 — Architect

```
cron: "0 * * * *"
prompt: "Read .agents/loop/architect-prompt.md and execute it as the Architect role. Identify the oldest unprocessed feature (by report timestamp), create an architectural plan in .agents/plans/todo-<feature-name>-architect-YYYY-MM-DD-HHmmss.md"
recurring: true
durable: true
```

### Cron #2 — Business Analyst

```
cron: "15 * * * *"
prompt: "Read .agents/loop/business-analyst-prompt.md and execute it as the Business Analyst role. Identify the oldest unprocessed feature (by report timestamp), create a business analysis plan in .agents/plans/todo-<feature-name>-business-analyst-YYYY-MM-DD-HHmmss.md"
recurring: true
durable: true
```

### Cron #3 — Tech Lead

```
cron: "30 * * * *"
prompt: "Read .agents/loop/tech-lead-prompt.md and execute it as the Tech Lead role. Identify the oldest unprocessed feature (by report timestamp), create a code quality plan in .agents/plans/todo-<feature-name>-tech-lead-YYYY-MM-DD-HHmmss.md"
recurring: true
durable: true
```

### Cron #4 — Fullstack Developer

```
cron: "45 * * * *"
prompt: "Read .agents/loop/fullstack-developer-prompt.md and execute it as the Fullstack Developer role. Aggregate all plans from Architect, Business Analyst, and Tech Lead. Execute all 3 plans, delete them, generate a single consolidated report in .agents/reports/done-<feature-name>-fullstack-developer-YYYY-MM-DD-HHmmss.md"
recurring: true
durable: true
```

## Stopping the Pipeline

Create a STOP file:

```bash
touch .agents/loop/STOP
```

Each role checks for this file and exits cleanly if found.
