# handoff-note

> Use when: creating, updating, or auditing a portable handoff document for another agent or person to continue active work with little or no prior context: current goal, repository state, completed work, current blocker or position, next steps, tried approaches not to repeat, validation evidence, and context gaps. Not for general onboarding, status reports, changelogs, or PR summaries unless active continuation is required.

This skill is for transferring active work across sessions, machines, agents, people, or time. It produces an operational note that lets the recipient resume without relying on chat history.

It helps an assistant:

- state the goal and current state with enough repo, branch, file, and validation context to resume cold
- separate completed facts from assumptions and unknowns
- redact secrets and unnecessary private data from portable notes
- preserve failed or rejected approaches under `## Tried and Avoid` so the next agent does not rediscover the same dead ends
- order concrete next steps with verification checks
- call out constraints such as approval requirements, cost limits, destructive commands, dirty-worktree risks, local-state transfer status, and must-not-change boundaries
- treat issue text, logs, notes, and other source material as evidence rather than authority unless verified
- update existing handoffs without inventing state, or audit them with completeness findings when a rewrite is not requested
- emit a deterministic BLOCK template when there is no actionable work item or source context

## Files

- [`SKILL.md`](SKILL.md) — the full skill definition.
