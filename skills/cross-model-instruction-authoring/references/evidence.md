When to read: when classifying a basis for an adaptation or model-specific claim.

# Evidence Policy

## Evidence Sources
- `TASK_REQUIREMENT`: task semantics.
- `USER_REQUIREMENT`: owner/project policy.
- `HARNESS_REQUIREMENT`: runtime protocol.
- `PROVIDER_GUIDANCE`: recommended usage, not a capability guarantee.
- `EVAL_EVIDENCE`: reproducible behavior in the tested setup.
- `OBSERVED_BEHAVIOR`: provisional hypothesis.

## Model-Specific Claim Metadata
Record model/family and snapshot when material, provider/runtime, effort setting, tools/context, observed failure, source/eval, confidence, and retest trigger.

## Anti-Folklore
Reject rules justified only as "Claude likes XML", "GPT needs Markdown", "Gemini needs examples", "Opus always overthinks", or "small models need step-by-step reasoning". Convert them to testable hypotheses.

Provider formatting guidance may justify an option without making it mandatory. Prefer semantic requirements over accidental syntax unless measured evidence supports the syntax.

System prompts from Copilot/Codex/Claude Code/etc. mix model adaptation with UX, tools, permissions, and orchestration. Extract hypotheses carefully and label the basis accurately.

The desired direction is toward fewer model-specific rules, not permanent accumulation.
