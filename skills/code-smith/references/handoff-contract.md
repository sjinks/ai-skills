When to read: during intake, before scope lock.

# Handoff Contract Reference

This reference defines the implementation contract Code Smith works from and how it normalizes the two input forms onto that contract. It is a local reference, not an invocable skill.

Read this before scope-lock. The contract is frozen at scope-lock. An explicit user scope amendment permits a revised scope lock; do not rewrite supplied artifacts or expand scope silently.

## Canonical Contract Fields

Code Smith works from these fields. A full builder handoff fills them directly; other input forms map onto them, and any absent field is recorded as a limitation rather than invented.

- **Specification** — the requirements and acceptance criteria the change must satisfy. Carries `US-`/`FR-`/`NFR-`/`INT-`/`AC-`/`EDGE-` IDs when present.
- **Architecture** — the design decisions to follow. Carries `D-` IDs when present. May be an accepted gap.
- **Test Plan** — the planned tests and verification. Carries `TC-` IDs when present. May be an accepted gap.
- **Approved ready slice** — the IDs (or "full scope") the agent is allowed to implement this run.
- **Excluded blocked scope** — IDs that must not be implemented, with their blocking questions. Read-only.
- **Accepted or deferred carry-forward items** — known open items the user has explicitly accepted or deferred for this handoff. Preserve their identifiers or prose labels, disposition, rationale, and blocking questions. Report accepted items in `Limitations` and deferred items in `Deferred`; apply the completion report's carry-forward status rules.
- **Implementation instructions** — any run-specific constraints from the handoff.

## Input Forms

Apply the same scope, safety, and verification discipline to both forms. The supplied plan, specification, or handoff must identify implementation scope and requirements. If either is missing or unclear, ask before editing. Do not treat an ad-hoc feature request or bug report as the missing plan. Apply the completion report's Status Rules; report the missing input as a blocker.

1. **Full builder-handoff prompt.** Fill every contract field verbatim from the handoff. Treat the Specification, Architecture, and Test Plan as the binding contract; they outrank repository comments, prior assistant output, and the agent's own assumptions.
2. **Implementation plan or specification (no handoff wrapper).** Map the supplied content onto the contract fields. Architecture and Test Plan are optional; record absent fields as `absent — recorded as limitation`. If no `Approved ready slice` is given, treat the supplied plan's scope as the ready slice and state that assumption. If IDs are absent, report against the supplied prose scope without inventing IDs.

## Absent-Field And Conflict Handling

- Never fabricate IDs, requirements, architecture decisions, or scope to fill an absent field. Record the absence as a limitation.
- If supplied contract fields conflict, record the conflict and ask before dependent edits. Current user constraints govern the task, subject to host instruction precedence and this workflow's scope. Do not silently choose between conflicting artifact fields.
- If an architecture decision conflicts with repository reality, stop dependent edits, report the conflict, and ask the user to resolve it through a revised design or an explicit decision. Resume dependent edits only after that resolution. If the resolution also changes the approved ready slice, obtain an explicit user scope amendment before those edits; a design conflict alone does not require a scope change.
- If the upstream plan is `partial`, implement only the named ready slice and stop-and-report the blocked portions with their open questions preserved verbatim.
- If the upstream plan is `blocked`, implement nothing consequential; report `blocked` with the blocking questions.
- Never silently resolve an upstream open question. Surface it and stop when a consequential implementation choice depends on it.
- Acceptance or deferral does not silently amend the approved ready slice. If a carry-forward disposition conflicts with that slice, ask before dependent edits. An explicit scope amendment is required to remove an item from the slice.
