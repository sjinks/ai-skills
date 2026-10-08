When to read: when choosing review lenses, gathering domain context, or distinguishing failure-mode categories.

# Review Guide

This guide supplies context and illustrations. The core defines required decisions and output.

Collect or read the narrowest useful context before judging:

- Target artifact and content type: spec, design, implementation, workflow, test plan, prior skill output, or other.
- Intended behavior, success criteria, explicit requirements, and non-goals.
- Actors, users, tenants, permissions, data boundaries, and trust boundaries when relevant.
- Inputs, outputs, dependencies, lifecycle, state transitions, rollback paths, and error paths.
- Release context, blast radius, reversibility, and whether the target is prototype, internal, production, regulated, security-sensitive, or safety-sensitive.
- Existing tests, verification evidence, monitoring, runbooks, or acceptance criteria.


## Optional Review Lenses

Apply the lenses that fit the target. Do not force every lens into the output.

- **Breaker/reliability:** What realistic edge, failure, ordering, timeout, or dependency condition breaks the promise?
- **Maintainer:** What future change, unclear contract, duplicated rule, or hidden coupling makes the artifact easy to misuse or regress?
- **Security/privacy:** What permission, identity, tenancy, data exposure, misuse, or trust-boundary failure is plausible?
- **User/workflow:** Where can a user become stuck, confused, misled, blocked, or lose work?
- **Verification:** What important behavior is unproved, unobservable, or only tested through an unrealistic mock?
- **AI-output:** If the target was produced by an AI system, check for happy-path bias, over-acceptance of the requested scope, confidence without evidence, attraction to familiar patterns, reactive patching, and tests rewritten to match implementation instead of intended behavior.

## Failure-Mode Taxonomy

Classify findings using the closest category:

- `requirements-clarity`: Missing, conflicting, ambiguous, or unverifiable requirements.
- `contract-logic`: Contract or logic failures between caller/callee, spec/implementation, UI/API, or workflow/runtime behavior.
- `input-handling`: Input, boundary, malformed data, default, null, duplicate, stale, or adversarial data handling failures.
- `error-rollback`: Error handling, rollback, retry, idempotency, partial-success, or compensation failures.
- `state-concurrency`: State, ordering, concurrency, cache, clock, race, or lifecycle transition failures.
- `auth-tenancy`: Permission, identity, tenancy, privacy, data-boundary, or secret-handling failures.
- `data-integrity`: Persistence, migration, schema, compatibility, durability, or data-integrity failures.
- `resource-lifecycle`: Resource lifecycle, timeout, cancellation, cleanup, scalability, quota, or backpressure failures.
- `user-workflow`: User workflow confusion, irreversible action, silent failure, misleading feedback, or work-loss failures.
- `verification-gap`: Test or verification gaps tied to specific unverified behavior.

Use the exact category values defined in the core; this catalogue explains them.

