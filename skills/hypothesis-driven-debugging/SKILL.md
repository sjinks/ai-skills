---
name: hypothesis-driven-debugging
description: "Use when: debugging a failure, bug, flaky test, or unexpected behavior with a disciplined loop: reproduce first, falsifiable hypothesis, cheapest discriminating experiment, evidence log, root-cause versus symptom decision, and a regression check before the fix counts as done."
argument-hint: "The failure description, error output, or bug report, plus reproduction info and any experiments already tried."
user-invocable: true
---

# Hypothesis-Driven Debugging

Run debugging as a sequence of falsifiable hypotheses and cheap discriminating experiments instead of guess-edit-rerun. Undisciplined debugging converges by luck; disciplined debugging converges by elimination and leaves a trail someone else can audit.

## When to Use

Use when a failure, bug, flaky test, or unexpected behavior needs structured investigation — whether starting fresh or rescuing a stalled guess-driven session. Out of scope: interpreting a specific sanitizer or memory-tool report against its own report anatomy, planning the fix's impact once the cause is known, post-incident retrospectives, and performance tuning without a defined misbehavior.

## Required Inputs

- The observed failure: what happens, what was expected instead, and the error output when there is any.
- Reproduction status: known steps, frequency, environments where it does and does not occur. Intermittent frequency is estimated as `1-in-N` from supplied data, or written `1-in-N (N unknown)`; when supplied claims and supplied evidence disagree (user says "always", logs show intermittent), record both as observations and use the evidence-backed value on the `Reproduction:` line.
- What has already been tried, when supplied; prior experiments are evidence, not noise.

If no failure description is provided, emit the BLOCK template; do not invent symptoms.

## The Loop

Work the loop in order; do not skip ahead to fixes:

1. Reproduce: establish the smallest, fastest reproduction you can and state its reliability (`always`, `1-in-N`, `1-in-N (N unknown)`, `not yet reproduced`). Without a reproduction, the only valid next steps are experiments that improve reproduction (logging, tighter loops, environment matching) — record them as experiments against reproduction itself.
2. Observe: state the facts only — exact messages, versions, timing, what differs between working and failing cases. No interpretation in this step.
3. Hypothesize: one falsifiable claim naming a mechanism ("the cache returns stale entries after TTL expiry because eviction never runs"), not a suspicion ("something with the cache").
4. Experiment: the cheapest test that discriminates this hypothesis from its rivals — prefer reading code, adding one assertion, bisecting (over commits, configs, or input), or toggling one variable, before stepping through everything.
5. Record: experiment, prediction, observed result, verdict — `confirmed`, `refuted`, `inconclusive`, or `proposed` (designed but not runnable yet; Observed `pending`). Refuted hypotheses stay in the log; they are paid-for progress.
6. Repeat 3–5 until a hypothesis is confirmed and explains all recorded observations, then proceed to the fix gate. When the cheap experiments are exhausted or a user-stated time or experiment budget runs out without a confirmation, stop and emit the report with `Cause: not established` and the remaining hypotheses in `### Untested backlog`; an unfinished honest report beats a forced conclusion.

## Fix Gate

Before any fix counts as done:

- Root cause or symptom: state which the confirmed cause is; this call applies only when a cause is confirmed. A symptom-level fix (retry, guard, suppression) is allowed only with the deeper cause named and a one-line reason for stopping there.
- The confirmed hypothesis must explain every observation in the log; unexplained observations mean the investigation is not finished — say so rather than declaring victory.
- Regression check: define the named test or check so that it fails on current code and must pass after the fix; running it post-fix is downstream work. A fix with no such check defined is `unverified`.
- Intermittent failures: the regression check states its statistical basis (N clean runs where it previously failed about 1-in-M).

## Rules

- One hypothesis under test at a time; parallel speculation goes to `### Untested backlog`, not the loop.
- Never change more than one variable per experiment; an experiment that changed two things confirms nothing.
- Distinguish "cannot reproduce" from "fixed": a disappearance without a confirmed mechanism is recorded as `Cause: not established (not reproduced — cause unknown)`, never closed as fixed.
- Evidence beats seniority of opinion: a refuted favorite hypothesis is closed, not retried with variations until it confesses.
- When the session inherits prior guesses: guesses the supplied evidence confirms or refutes become log rows marked `(inherited)`, with the Experiment and Observed cells citing that supplied evidence; guesses whose supplied evidence is inconclusive become `(inherited)` rows with verdict `inconclusive`; guesses with no evidence go to `### Untested backlog`.
- Experiments the session designs but cannot run get the verdict `proposed` with the prediction filled and the Observed cell `pending`.
- Investigation only: this skill produces the cause, the fix direction, and the regression check definition; writing the fix is downstream work.

## Output Format

```markdown
## Debugging Report

- Failure: <one sentence: observed vs expected>
- Reproduction: <always | 1-in-N | 1-in-N (N unknown) | not yet reproduced> — <smallest known repro, or what is being tried to obtain one>

### Observations

- <fact, no interpretation>

### Hypothesis log

| # | Hypothesis (falsifiable mechanism) | Experiment | Predicted | Observed | Verdict |
|---|------------------------------------|------------|-----------|----------|---------|
| 1 | <claim naming a mechanism; `(inherited)` when classified from supplied evidence> | <cheapest discriminating test> | <prediction> | <result, or `pending`> | confirmed \| refuted \| inconclusive \| proposed |

### Conclusion

- Cause: <confirmed mechanism — root-cause | symptom (<deeper cause and reason for stopping>); or `not established` with the missing evidence named and no root-cause/symptom suffix>
- Fix direction: <what the fix changes, or `blocked on cause`>
- Regression check: <check defined to fail on current code and pass after the fix, with its statistical basis when intermittent; or `unverified` when no such check is defined>

### Untested backlog

- <parked hypothesis, why it can wait>
```

Empty sections are written with `None`. Emit exactly one value for each enum field; do not copy enum lists or angle-bracket placeholders into the report. The report has no verdict line; `Verdict: BLOCK` appears only in the insufficient-input template below.

## Error Handling (BLOCK Template)

Use this reduced template only for missing or unreadable input.

```markdown
## Debugging Report

Verdict: BLOCK

- Missing input: <no failure description provided / text unreadable>
- Smallest addition to proceed: <concrete ask>
```

## Example

Failure: nightly export job writes truncated files about once a week; full files all other nights.

Hypothesis log row:

| # | Hypothesis (falsifiable mechanism) | Experiment | Predicted | Observed | Verdict |
|---|------------------------------------|------------|-----------|----------|---------|
| 1 | the job's pod is OOM-killed mid-write on large-export nights | correlate truncation dates with pod OOM events and export sizes | truncated nights show OOM kills and top-decile sizes | all three truncated nights have OOM kills; no OOM on clean nights | confirmed |

Conclusion lines:

- Cause: pod memory limit below peak export working set — root-cause
- Fix direction: stream the export instead of buffering it; raising the limit alone is the symptom-level alternative
- Regression check: integration test exporting a top-decile dataset under the production memory limit; fails on current code, passes with streaming — deterministic given top-decile input, so no N-run statistical basis is needed

## Anti-Patterns

- Editing code as a probe and keeping the edit when the failure happens to vanish.
- Hypotheses without mechanisms ("it's probably a race") that no experiment can refute.
- Two changed variables per experiment, proving nothing either way.
- Treating "cannot reproduce anymore" as fixed.
- A fix with no check that fails before and passes after.
- Discarding refuted hypotheses from the report as embarrassing instead of recording them as eliminated space.

## Definition of Done

Reproduction status is stated, every hypothesis in the log is a falsifiable mechanism with one-variable experiments and recorded verdicts, the conclusion is `confirmed`-backed or honestly `not established`, the root-cause-vs-symptom call is explicit whenever a cause is confirmed, and a regression check is defined or the fix is marked `unverified`.
