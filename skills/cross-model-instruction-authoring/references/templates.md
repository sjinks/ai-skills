# Templates

Use these as starting structures. Remove sections that do not affect behavior.

## Portable Agent Skill

```markdown
---
name: example-skill
description: >-
  Use when [recognizable user intent and trigger terms]. Produces [main
  deliverable]. Do not use when [important exclusion].
---

# Objective

Produce [observable result].

# Deliverable

This is an [implementation | analysis | transformation] task.
[State what must be returned or changed.]

# Inputs

Use [sources of requirements].

Resolve minor omissions from context. Ask only when missing information
materially affects correctness, cannot be established from context, and has no
safe reversible default.

# Required Outcomes

- [Outcome]
- [Outcome]

# Invariants

- [Constraint]
- [Constraint]

# Default Workflow

Use this workflow unless an equivalent approach is safer or more efficient:

1. [Inspect or gather context.]
2. [Perform the task.]
3. [Validate the result.]
4. [Review against acceptance criteria.]

# Tool Use

Use available tools when conclusions depend on current state or runtime
evidence. Do not assume specific tool names.

When a required capability is unavailable, use a safe alternative or report
what remains unverified.

# Validation

- [Required check]
- [Interpretation of failure]
- [What may be skipped and how to report it]

# Completion Criteria

The task is complete when:

- [Observable criterion]
- [Observable criterion]

# Output

Report or produce:

1. [Result]
2. [Evidence or validation]
3. [Risks, assumptions, or blockers]
```

## Portable Custom Agent Prompt

```markdown
You are a [narrow specialist role].

# Delegation Scope

Use this agent for [problem class and workflow stage].

Do not use it for [important exclusions].

# Ownership

This agent owns:

- [Responsibility]
- [Responsibility]

This agent does not own:

- [Excluded responsibility]

# Authority

The agent may [inspect/edit/execute/browse/delegate].

The agent must pause before [destructive, irreversible, or out-of-scope
actions].

# Evidence Policy

Verify claims about current state with available tools or supplied evidence.
Distinguish verified facts, supported inferences, assumptions, and unknowns.

# Operating Policy

- [Judgment rule]
- [Scope rule]
- [Ask-versus-assume rule]
- [Tool or delegation trigger]

# Stopping Conditions

Stop when [observable completion state] or when [concrete blocker].

# Return Contract

Return to the parent agent or user:

1. [Conclusion or artifact]
2. [Evidence]
3. [Actions performed]
4. [Unresolved risks or next decision]
```

## Runtime Adapter Note

```markdown
# Runtime Adapter: [runtime]

This adapter defines runtime-specific behavior only.

- Installation or discovery path: [...]
- Invocation controls: [...]
- Exact tools or capabilities: [...]
- Permissions and approval gates: [...]
- Sandbox and network policy: [...]
- Subagent configuration: [...]
- Model and effort routing: [...]
- Hooks or integrations: [...]

The portable core remains the source of truth for task behavior.
```

## Cross-Model Compatibility Note

```markdown
## Compatibility

Target models:
- [...]

Compatibility floor:
- [What the smallest supported models can execute reliably.]

Routing limitations:
- [Tasks that require a stronger model or decomposition.]

Runtime assumptions:
- [...]

Unverified areas:
- [What must be tested.]
```
