# Codex Chronicle

Analyze local Codex history for personalized token-efficiency tips, workflow
recommendations, and proposed improvements to project instructions. Supports
`cost-tips`, `tips`, and `improve` through a dependency-free Node.js helper.

The helper reads local logs; it does not call models, upload history, or change
session stores. Recommendations require conversation evidence. Instruction
changes require explicit authorization. Token observations are not billing data.

## Usage

Invoke the skill in Codex with a mode and optional scope:

```text
$codex-chronicle cost-tips
$codex-chronicle tips
$codex-chronicle tips for all repositories
$codex-chronicle improve
```

| Mode | Purpose | Default window |
| --- | --- | --- |
| `cost-tips` | Find token-efficiency opportunities supported by conversation evidence | 30 days |
| `tips` | Identify workflow friction and concrete ways to improve it | 7 days |
| `improve` | Propose evidence-backed changes to the selected project's instructions | 30 days |

The default scope is the current repository and root sessions. Ask explicitly
to include all repositories or subagents. `improve` stays within one selected
repository and requires evidence from at least two sessions for each recurring
problem. It proposes changes before applying explicitly authorized edits.
When no changes are supported, its `Instruction changes:` field is `None supported.`.

Node.js 22 or later is required. To inspect evidence directly from the repository
root, run:

```sh
node skills/codex-chronicle/scripts/chronicle.mjs tips --all-repos
node skills/codex-chronicle/scripts/chronicle.mjs --help
```

The helper returns JSON evidence, not a finished recommendation report. Read the
[runtime guide](references/runtime.md) for repository-path filtering, rolling
windows, bounded excerpts, and other options. Separate worktrees require separate
repository-scoped passes, or an explicit all-repositories pass.

## Evidence and limitations

The helper reads `sessions/` and `archived_sessions/` under `CODEX_HOME` or
`~/.codex`. It reports coverage and keeps usage from different client surfaces
separate. Missing usage remains unknown; cached input and reasoning output are
subsets, not additional tokens. Duplicate session copies are selected rather
than merged, so divergent copies can omit activity.
Unsafe token sums remain unknown and produce warnings at the affected session
or client surface. Recorded working directories must be absolute to qualify for
repository-scoped analysis; invalid paths remain unassigned.
Cumulative snapshots are validated before subtraction; malformed required
totals break the baseline, and invalid subsets remain unknown. Aggregate usage
is attributed by session, `usage_source`, and JSON field; log-line references
accompany excerpts, not usage events.

Correction signals are keyword-based candidates, not confirmed mistakes.
Recommendations require inspection of surrounding conversations and current
project configuration. Excerpts are bounded and common credential formats are
masked, but masking is not comprehensive. Inspect output before sharing it.
Unknown log formats and history from other devices can limit conclusions.

## Verification

```sh
node --test skills/codex-chronicle/scripts/chronicle.test.mjs
```

Tests use synthetic temporary logs. Local smoke tests can read this computer's
history without model calls or changes to session stores.

## Files

- [SKILL.md](SKILL.md) — activation, workflow, boundaries, modes, and report contract.
- [Runtime guide](references/runtime.md) — CLI, schemas, privacy, and limitations.
- [Helper](scripts/chronicle.mjs) — read-only JSONL analysis and bounded excerpts.
- [Tests](scripts/chronicle.test.mjs) — isolated accounting, filtering, failure, and privacy checks.

## Provenance

Inspired by the `tips`, `cost-tips`, and `improve` workflows in the locally
installed GitHub Copilot Chronicle package. This is a Codex-specific implementation
with its own history reader and output contract. The observed Codex log schemas
are implementation data, not a promised stable public interface.

The streaming reader uses Node.js's [readline API](https://nodejs.org/api/readline.html).
Skill packaging follows the [official skill guide](https://learn.chatgpt.com/docs/build-skills).
