When to read: before finalizing a portable instruction artifact.

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

## Final Review
- [ ] The portable core handles the normal path and material branches explicitly.
- [ ] The compatibility floor is not based on unsupported capability assumptions.
- [ ] Adaptations distinguish task requirements, provider guidance, runtime constraints, and observed behavior.
- [ ] Examples and output contracts match the procedure.
