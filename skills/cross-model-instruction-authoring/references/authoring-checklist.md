When to read: before finalizing a portable instruction artifact or its evals.

# Authoring Checklist

## Portable Core
- [ ] Outcome, inputs, constraints, permissions, defaults, failure behavior, output, verification, and done condition are clear.
- [ ] Verification distinguishes attempted from successful checks.

## Portability
- [ ] No unnecessary provider vocabulary or chain-of-thought request.
- [ ] No duplicated tool-schema prose.
- [ ] No fixed tool/search/edit order without a correctness reason.
- [ ] Runtime protocol is separated from task behavior.

## Compatibility Floor
- [ ] Weakest intended profile can follow the normal path.
- [ ] Required branches/criteria are explicit enough.
- [ ] Prompt size is not compensating for insufficient capability.

## Capability Ceiling
- [ ] Strong models retain strategy freedom.
- [ ] No unnecessary plans/progress narration, redundant confirmation, or forced exploration.

## Adaptations
- [ ] Every non-universal rule has an evidence class.
- [ ] Model name alone caused no patch.
- [ ] Observed behavior is provisional.
- [ ] Harness quirks are not model quirks.
- [ ] Universal patches were promoted; stale patches can be removed.

## Output Contract
- [ ] A caller-supplied schema replaces the default wrapper only when required.
- [ ] The selected default mode uses its exact labels once, in order, with nonempty bodies.
- [ ] The terminal field ends the response: `Compatibility note:` for artifact modes and the final evidence bullet for Profile Recommendation.

## Evals
- [ ] Portable-core behavior is covered.
- [ ] Weak-target omission and strong-target overconstraint are covered.
- [ ] Folklore rejection and runtime-vs-model distinction are covered.
- [ ] Patch addition and patch removal are both tested.
- [ ] Deterministic wrapper tests cover omission, reorder, duplicate, invalid profile, profile crossover, and trailing prose.
