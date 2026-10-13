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
The skill selects a repository root before invoking the helper. Outside a
repository, it requires an explicit repository selection or, for `tips` and
`cost-tips`, an explicit all-repositories request. The low-level helper's
working-directory default is directory scope, not automatic repository discovery;
it must not substitute for this selection step.
Inside a repository, the default current repository root counts as selected;
no additional confirmation is needed for its configuration inspection or
repository-specific recommendations. Explicit selection is needed outside a
repository, not for an already-resolved default.

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
`usage_provenance` samples contributing sessions' `id` and `usage_source`,
independently of `--limit` or `--session`. At most 100 entries are exported across
all surfaces together; the top-level `usage_provenance_limit` declares this cap.
Each surface's `sessions_with_usage` is its complete contributor count, and
`usage_provenance_truncated` flags omitted contributors. Totals remain complete.
Only sessions with usage contribute; missing usage is visible in session counts
and coverage. A no-usage surface has `measured_usage` set to `null`, empty
provenance and a false truncation flag. Deduplication and scope filtering precede
aggregation; the sample follows deterministic file-discovery order.
This cap bounds the provenance payload, not the entire analyzer's memory;
the complete session inventory still scales with history size.

## Sources and accounting

The helper recursively reads regular `.jsonl` files under `sessions/` and
`archived_sessions/`. It skips symlinks and files over 64 MiB, and reports scan,
parse, unknown-event, duplicate-session, and coverage counts. A missing source
directory is reported. Scan/error counts cover the entire data directory;
matched-session and usage counts cover the selected scope.
Files are opened once with `O_NOFOLLOW` (and `O_NONBLOCK` when available), then
type and size are checked on that descriptor. The same descriptor reads only
the initial byte range, bounded to 64 MiB; appends cannot expand that range.
Empty files read zero bytes. Unsupported no-follow opens fail closed with
`ENOTSUP`; non-regular files report `ENOTFILE`. No-follow protects the final
path component; discovery skips observed directory symlinks but is not a
race-proof sandbox against ancestor-directory replacement. In-place changes
and truncation can still affect a best-effort snapshot.
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
come from `response_item`, with `event_msg` message fallback only when the selected
window has no response messages for that role. Older or future response messages
do not suppress in-window fallback messages; in-window response messages still
prevent duplicate fallback counts for their role only when extracted text is
usable. Text is usable when masking/control removal leaves non-whitespace text.
Empty, unsupported, whitespace-only, or control-only response text neither counts
as a message nor suppresses fallback. Empty fallback text is also excluded.
Raw text lengths remain the observed prompt metrics. Tool names and output lengths are
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
If a cached/reasoning counter decreases while required totals increase, its
negative delta is invalid, becomes unknown, and emits a field-specific warning.
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
latest preceding turn context; missing values use `unknown`.
Per-session `models` keys are JSON-encoded `[model, effort]` string pairs, such
as `["example","low"]`. Decode a key with `JSON.parse`; do not split on `/`.
Separators, quotes, backslashes and other log characters cannot merge distinct
pairs. The same encoding applies to both accounting streams.
Unrecognized formats are reported, not treated as zero usage. Missing per-response records
in a partially populated preferred stream cannot be detected reliably.

## Privacy and interpretation

The helper itself performs no network or model calls. When invoked through
Codex, its tool results enter the active model context, which may be hosted
remotely. Summaries contain metadata/counts; drill-down includes transcript text.
Before drill-down, explain the selected scope, 1600-UTF-16-unit excerpt bound,
best-effort masking, and this model-context disclosure; obtain explicit informed
approval unless it already covers that scope. Without it, use only summary
metadata, do not attribute conversational causes, and report the limitation.
Do not transfer logs to other services. Direct standalone CLI output remains
local unless the caller shares it.

Drill-down
strips control characters, masks common credential formats, then clips each
excerpt to at most 1600 UTF-16 code units, retaining complete surrogate pairs.
A pair crossing the limit is omitted together, so the result may be shorter.
`clipped` is based on the masked length and actual cutoff, so it
describes actual truncation rather than redaction or control-character removal.
Control removal covers C0 except tab/LF, DEL, and C1 (U+0080–U+009F).
This is not comprehensive redaction. Do not publish
raw output without inspection. For excerpt-backed findings, record timestamps,
session ID, file, and log line. For aggregate usage, cite session IDs,
`usage_source`, and the relevant JSON fields; usage-event line provenance is
not exported. For surface totals, cite the JSON field, `sessions_with_usage`,
the bounded `usage_provenance` sample and `usage_provenance_truncated`; disclose
missing contributor IDs instead of implying complete attribution. Do not treat a
regex match or a large token total as causal proof.

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
