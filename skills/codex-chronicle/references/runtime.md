Read this guide before running the local helper or interpreting its JSON output.

# Local runtime

Use Node.js 22 or later. The helper uses built-in modules and makes no network
calls. Run from the workspace, using the actual skill directory path when the
package is installed elsewhere. Quote paths according to the executing shell.

```sh
node skills/codex-chronicle/scripts/chronicle.mjs cost-tips --repo /absolute/repository
node skills/codex-chronicle/scripts/chronicle.mjs tips --repo /absolute/repository
node skills/codex-chronicle/scripts/chronicle.mjs improve --repo /absolute/repository
```

The helper returns evidence, not finished recommendations. JSON is written to
stdout; fatal errors go to stderr with exit status 1. `--help` lists options.

## Scope and drill-down

- `--home PATH`: Codex data directory; defaults to `CODEX_HOME` or `~/.codex`.
- `--repo PATH`: include sessions whose recorded working directory is this path or a descendant, with a path-separator boundary. Only absolute recorded paths are accepted; missing, empty, or relative paths remain `null` and are excluded from repository-scoped runs. They can still appear in an all-repositories run. Default: process working directory. This is directory scope, not remote-repository identity; separate worktrees require separate passes.
- `--all-repos`: explicitly widen scope; incompatible with `--repo` and `improve`.
- `--days N`: positive integer, at most 3650. Default: 7 for `tips`, 30 otherwise.
- `--until ISO`: inclusive endpoint with an explicit timezone. Default: current instant. Start is endpoint minus N times 24 hours, inclusive. These are rolling windows, not calendar-day boundaries.
- `--agents roots|subagents|all`: default `roots`. JSON groups surfaces separately; unknown metadata is its own surface.
- `--limit N`: summary session limit (default 20); excerpt limit (default 12) when `--session` is supplied. Range 1–100 for summaries, 1–50 for excerpts.
- `--session ID`: select one exact session ID within the same scope and window. Returns bounded user/assistant/tool excerpts with log line references. Default excerpts are the most recent ones. No match is an explicit empty result.
- `--line N`: with `--session`, return excerpts within three physical log lines of N. Use the summary's candidate line references for targeted inspection. Increase context by selecting another line; do not infer a cause from a clipped excerpt.

`tips` and `improve` order candidates by correction-signal count, then recency.
`cost-tips` orders by measured input tokens, then recency. All aggregates cover
all matched sessions, even when the session list is truncated.

## Sources and accounting

The helper recursively reads regular `.jsonl` files under `sessions/` and
`archived_sessions/`. It skips symlinks and files over 64 MiB, and reports scan,
parse, unknown-event, duplicate-session, and coverage counts. A missing source
directory is reported. Scan/error counts cover the entire data directory;
matched-session and usage counts cover the selected scope.
With duplicate session IDs, it selects the largest file
(lexical path breaks ties); it does not merge divergent copies. This can omit
activity and must be disclosed. Growing logs are a best-effort snapshot.

Metadata comes from `session_meta`; model/effort from `turn_context`. Messages
and usage events require finite parsed string timestamps; non-string timestamps
are invalid rather than coerced. An absent session-start timestamp falls back
to the event timestamp; an explicitly invalid start remains unknown, warns,
and cannot authorize a zero counter baseline. `invalid_timestamps` counts
invalid event timestamps and explicitly invalid session-start timestamp fields.
Messages
come from `response_item`, with `event_msg` message fallback only when the file
has no response messages for that role. Tool names and output lengths are
observations; outputs are not interpreted as verified failures. Correction
signals are keyword heuristics over request text, not proven mistakes. Recognized
AGENTS/environment/skill/open-page wrappers are excluded from that heuristic; IDE context is
removed before `## My request:`. Stored message counts and lengths still include
these wrappers. No chain-of-thought or
injected system/developer instructions are exported.
Largest prompt and tool-output lengths include log line references for targeted inspection.

For usage, prefer `token_usage_record.payload.usage`, deduplicated by
`response_id`. Records lacking a response ID or valid nonnegative integer input
and output counts are excluded with warnings. If any valid records exist in a
file, do not also count its `event_msg.token_count` events. Otherwise, subtract
successive valid cumulative input/output counters. Validate snapshot subsets
before subtraction and validate resulting delta subsets again. Invalid required
totals or invalid counter timestamps are warned and discard the baseline; omit the next valid snapshot to
establish a new baseline without bridging unknown activity. Invalid or missing
subset counts stay unknown for deltas that depend on them.
The baseline is zero only for the first observed counter
when the session starts within the window; for an older session with no earlier
counter, omit the first counter and warn. Counter decreases start a new segment,
whose first counter is omitted and warned. Usage is assigned by event timestamp.

Cached input and reasoning output are subsets, not additional tokens. Missing
subset counts remain `null` for aggregate subsets. Invalid subsets, including
counts larger than their corresponding whole, are omitted and warned.
Individual token counts must be nonnegative safe integers. If a sum exceeds
`Number.MAX_SAFE_INTEGER`, that aggregate field becomes `null` and remains
unknown. This applies to session, model/effort, and client-surface totals;
warnings appear in the session or surface's `warnings` array. Other fields
remain independently measurable. Unknown input totals sort after measured
totals in `cost-tips`.
Model attribution uses the
latest preceding turn context; missing values use `unknown`. Unrecognized
formats are reported, not treated as zero usage. Missing per-response records
in a partially populated preferred stream cannot be detected reliably.

## Privacy and interpretation

Summaries contain metadata and counts, not transcript excerpts. Drill-down
clips each excerpt to 1600 characters, strips control characters, and masks
common credential formats. This is not comprehensive redaction. Do not publish
raw output without inspection. For excerpt-backed findings, record timestamps,
session ID, file, and log line. For aggregate usage, cite session IDs,
`usage_source`, and the relevant JSON fields; usage-event line provenance is
not exported. Do not treat a regex match or a large token total as causal proof.

Do not convert these local observations into a bill. Any optional API-dollar
estimate needs verified model rates, cache categories, billing mode, and an
explicit estimate label. Subscription limits require separate account evidence.
Unknown events, missing tokens, excluded agents, alternate devices, separate
worktrees, clipped excerpts, and duplicate files limit conclusions.

## Local verification

```sh
node --test skills/codex-chronicle/scripts/chronicle.test.mjs
```

Tests use synthetic temporary data and remove only their own temporary directory.
Live smoke tests read local logs without changing them. No model calls are needed.

When `improve` supports no instruction changes, report `Recommendations: None supported.`
and `Instruction changes: None supported.`. Preserve all five report
labels from `SKILL.md` and explain missing or insufficient evidence in
`Limitations:`.
