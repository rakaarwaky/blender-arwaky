# Cron Setup Guide — 6-Phase AES Pipeline

## Overview

The AES pipeline is split into **6 separate cron jobs**, each running **10 minutes apart**:

## How to Setup

Use **CronCreate** tool 6 times. Each cron fires a prompt that tells the agent to read its corresponding file and execute it as the role's task.

### Cron #1 — Architect

```
cron: "0 * * * *"
prompt: "Read .agents/loop/architect-prompt.md and execute it as the Architect role."
recurring: true
durable: true
```

### Cron #2 — Fullstack Developer

```
cron: "10 * * * *"
prompt: "Read .agents/loop/fullstack-developer-prompt.md and execute it as the Fullstack Developer role"
recurring: true
durable: true
```

### Cron #3 — Business Analyst

```
cron: "20 * * * *"
prompt: "Read .agents/loop/business-analyst-prompt.md and execute it as the Business Analyst role.
recurring: true
durable: true
```

### Cron #4 — Fullstack Developer

```
cron: "30 * * * *"
prompt: "Read .agents/loop/fullstack-developer-prompt.md and execute it as the Fullstack Developer role"
recurring: true
durable: true
```

### Cron #5 — Tech Lead

```
cron: "40 * * * *"
prompt: "Read .agents/loop/tech-lead-prompt.md and execute it as the Tech Lead role. 
recurring: true
durable: true
```

### Cron #6 — Fullstack Developer

```
cron: "50 * * * *"
prompt: "Read .agents/loop/fullstack-developer-prompt.md and execute it as the Fullstack Developer role"
recurring: true
durable: true
```

## Stopping the Pipeline

Create a STOP file:

```bash
touch .agents/loop/STOP
```

Each cron checks for this file and exits cleanly if found.
