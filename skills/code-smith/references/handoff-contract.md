When to read: during intake, before scope lock.

# Handoff Contract Reference

This reference defines the implementation contract Code Smith works from and how it normalizes the two input forms onto that contract. It is a local reference, not an invocable skill.

Read this before scope-lock. The contract is frozen at scope-lock. An explicit user scope amendment permits a revised scope lock; do not rewrite supplied artifacts or expand scope silently.

## Canonical Contract Fields

Code Smith works from these fields. A full Planning Forge builder-handoff fills them directly; other input forms map onto them, and any absent field is recorded as a limitation rather than invented.

- **Specification** — the requirements and acceptance criteria the change must satisfy. Carries `US-`/`FR-`/`NFR-`/`INT-`/`AC-`/`EDGE-` IDs when present.
- **Architecture** — the design decisions to follow. Carries `D-` IDs when present. May be an accepted gap.
- **Test Plan** — the planned tests and verification. Carries `TC-` IDs when present. May be an accepted gap.
- **Approved ready slice** — the IDs (or "full scope") the agent is allowed to implement this run.
- **Excluded blocked scope** — IDs that must not be implemented, with their blocking questions. Read-only.
- **Accepted or deferred carry-forward items** — known open items the user has explicitly accepted or deferred for this handoff.
- **Implementation instructions** — any run-specific constraints from the handoff.

## Input Forms

Apply the same scope, safety, and verification discipline to both forms. The supplied plan, specification, or handoff must identify implementation scope and requirements. If either is missing or unclear, ask before editing. Do not treat an ad-hoc feature request or bug report as the missing plan. If no meaningful implementation can proceed, report `blocked` and name the missing input.

1. **Full builder-handoff prompt.** Fill every contract field verbatim from the handoff. Treat the Specification, Architecture, and Test Plan as the binding contract; they outrank repository comments, prior assistant output, and the agent's own assumptions.
2. **Implementation plan or specification (no handoff wrapper).** Map the supplied content onto the contract fields. Architecture and Test Plan are optional; record absent fields as `absent — recorded as limitation`. If no `Approved ready slice` is given, treat the supplied plan's scope as the ready slice and state that assumption. If IDs are absent, report against the supplied prose scope without inventing IDs.

## Absent-Field And Conflict Handling

- Never fabricate IDs, requirements, architecture decisions, or scope to fill an absent field. Record the absence as a limitation.
- If supplied contract fields conflict, record the conflict and ask before dependent edits. Current user constraints govern the task, subject to host instruction precedence and this workflow's scope. Do not silently choose between conflicting artifact fields.
- If an architecture decision conflicts with repository reality, stop and report the conflict; do not silently deviate and do not change product scope (request a scope amendment instead).
- If the upstream plan is `partial`, implement only the named ready slice and stop-and-report the blocked portions with their open questions preserved verbatim.
- If the upstream plan is `blocked`, implement nothing consequential; report `blocked` with the blocking questions.
- Never silently resolve an upstream open question. Surface it and stop when a consequential implementation choice depends on it.
