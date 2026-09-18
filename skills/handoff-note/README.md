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

## Weak-model path

The skill begins with a short, fixed path: choose create, update, audit, audit + update, or BLOCK; sort statements by evidence; redact and check transferability; render one schema; then do a cold-resume check. This keeps the normal path shallow while retaining the evidence and safety boundaries needed for a portable handoff.

## Model-evaluation plan

The checked-in eval uses `claude-sonnet-5` as its default executor. It is a structural baseline, **not** evidence for the target-model roster. Live model runs are approval-gated and must not be started merely to confirm this documentation.

When a maintainer has explicit approval, run the same suite with provider-supported model identifiers for this matrix. Record the exact runtime, model identifier, settings, date, task results, and failures; do not generalize a result to another model.

| Profile | Required probes | Purpose |
| --- | --- | --- |
| Compatibility floor: GPT-5.4 mini and Claude Haiku 4.5 | incomplete context, BLOCK, secret/identifier redaction, caller-schema override | Prove the short normal path does not invent state, leak data, or fall back to default headings. |
| Balanced: GPT-5.4 and Claude Sonnet 5 | normal create, update, audit, local-change transfer | Check all modes preserve evidence and ordered continuation. |
| Broad synthesis: GPT-5.6 Terra and Claude Opus 5 | complex/untrusted-context and audit + update cases | Check that richer reasoning does not override boundaries or compress uncertainty. |
| Remaining declared targets: GPT-5.5, GPT-5.6 Luna, GPT-5.6 Sol, Claude Opus 4.8, and Claude Fable 5 | normal create plus the floor probes | Establish model-specific evidence across the full declared roster; do not infer it from another profile. |

The floor probes are `positive-edge-001`, `positive-edge-002`, `positive-edge-003`, `positive-edge-008`, and `positive-edge-009`. Use `waza models` to discover supported identifiers, then run only an approved command such as `waza run evals/handoff-note/eval.yaml --model <approved-model> --output <result-file>`.

## Files

- [`SKILL.md`](SKILL.md) — the full skill definition.
- `evals/handoff-note/` — approval-gated model-evaluation suite and deterministic task assertions.
