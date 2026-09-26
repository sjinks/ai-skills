When to read: after a concrete failure risk is identified and before adding a non-universal correction.

# Behavioral Patches

Patches are narrow corrections for specific failure modes, not personality descriptions of model families.

Record `patch`, `scope`, `basis`, `confidence`, and `reason`.

## `bounded-exploration`
> Gather enough context to act confidently. Once the relevant evidence has converged, proceed rather than continuing exploration merely for additional confirmation.

## `context-before-conclusion`
> Inspect the surrounding context necessary to support the conclusion; do not infer broader behavior from the immediate artifact alone.

## `verification-over-reasoning`
> When verification is available, use it. Do not treat reasoning about expected behavior as equivalent to a successful check.

## `strategy-reset-after-failure`
> After repeated failure of the same approach, change strategy rather than retrying a materially equivalent attempt.

Prefer deterministic harness retry limits when possible.

## `explicit-criteria`
> Evaluate every required criterion explicitly before returning the result.

## `explicit-defaults`
> Use the stated defaults for unspecified choices; do not invent material requirements.

Usually promote the actual default into the portable core.

## `completion-persistence`
> Continue until the requested outcome is complete, verified, or genuinely blocked.

Never override permission boundaries.

## `parallelize-independent-reads`
> Parallelize independent read-only lookups when the runtime supports it and their results do not depend on one another.

## Lifecycle
Promote a patch into the portable core if it proves task-universal. Move it into the runtime adapter if it is harness-only. Remove a model-specific patch when it stops reproducing in evals.
