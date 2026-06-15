---
name: Feature Request
about: Suggest a new feature for Blender Arwaky
title: "[FEAT] "
labels: enhancement
assignees: ''
---

## Feature Description

A clear and concise description of the feature you'd like to see.

## Motivation / Use Case

**What problem does this solve?**

Describe the use case, workflow, or scenario where this feature would help.

## Proposed Solution

How should this work? Describe the user-facing behavior.

### Example API / Command

```python
# If adding a new MCP tool or action
execute_command(
    action="your_new_action",
    args={"param": "value"}
)
```

## Alternatives Considered

What other approaches did you consider? Why is this one better?

## Affected Components

Which layers / modules would this touch?

- [ ] `taxonomy/` (data structures, VOs)
- [ ] `contract/` (ports, protocols)
- [ ] `infrastructure/` (adapters, API clients)
- [ ] `capabilities/` (use cases)
- [ ] `agent/` (orchestrators)
- [ ] `surfaces/` (MCP tools, CLI)
- [ ] `blender_mcp_addon/` (Blender addon)
- [ ] Documentation (README, SKILL.md, AGENT.md)

## Willingness to Contribute

- [ ] I'd like to implement this myself
- [ ] I'd be open to a PR from the maintainers
- [ ] I just want the feature, I can't implement it

## Additional Context

Add any other context, screenshots, or examples about the feature request.
