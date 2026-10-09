When to read: only when assessing a supplied Haiku 5.5 API integration or agent harness; these checks do not impose runtime adapters on portable instruction text.

# Haiku 5.5 Runtime Checks

Inspect supplied configuration and code without making live calls. Report unavailable configuration as an evidence limitation. Never invent the effective effort or thinking mode.

## Tool and message handling

When JSON structured output and tools are combined with thinking disabled, check that required calls remain possible. [Anthropic's prompting guide](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-haiku-5-5) recommends adaptive thinking, removing the structured-output constraint for tool-dependent requests, or supported forced tool choice. Do not mandate one option universally. Check that the harness delivers mid-task user input as user text, separate from untrusted tool results and harness notices.

## API compatibility and failures

According to [the migration guide](https://platform.claude.com/docs/en/models/haiku-5-5/migration-guide), check:

- no legacy manual `budget_tokens`; adaptive or disabled thinking supported by the selected effort level;
- token budgets leaving room for thinking and text, with tokenizer changes accounted for;
- content selected by block type, with empty or truncated visible output handled;
- no assistant prefill or unsupported sampling parameters;
- refusal handling that reports the outcome rather than claiming completion or relying on server-side fallback.

Keep these checks conditional on the actual integration. Do not treat unavailable runtime evidence as a defect in an otherwise portable skill.
