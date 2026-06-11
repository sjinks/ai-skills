---
name: cpp-sanitizer-triage
description: "Use when: triaging, interpreting, or acting on AddressSanitizer, ThreadSanitizer, UndefinedBehaviorSanitizer, MemorySanitizer, or LeakSanitizer reports, including heap-use-after-free, heap-buffer-overflow, stack-use-after-return, data race reports, ODR violation reports, suppression files, sanitizer flags and runtime options, symbolization problems, false-positive claims, and deciding whether a report is real, its root cause frame, and the fix owner."
argument-hint: "Paste or describe the sanitizer report, the sanitizer and flags in use, and what decision you need (real or not, root cause, suppression, fix)."
user-invocable: true
---

# C++ Sanitizer Triage

Use this skill when a sanitizer (ASan, TSan, UBSan, MSan, LSan) has produced a report and the task is to interpret it, decide whether it is a true positive, locate the root-cause frame, and route the fix — or to justify and scope a suppression.

The goal is disciplined triage: every report gets a classification (true positive, tool limitation, configuration artifact), a root-cause frame distinct from the symptom frame, and an owner — never a reflexive suppression.

**UTILITY SKILL.** INVOKES: read-only file access for supplied targets; no other tools or skills. FOR SINGLE OPERATIONS: use for focused report interpretation, suppression review, sanitizer configuration questions, or triage-process design.

## Scope

- Use this skill for reading sanitizer report anatomy (error kind, access/allocation/free stacks, shadow bytes, mutexes-held, thread creation stacks), distinguishing symptom frames from root-cause frames, classifying reports as true positives vs tool limitations vs build/configuration artifacts, designing and reviewing suppression files, sanitizer build flags and runtime options (`ASAN_OPTIONS`, `TSAN_OPTIONS`, `halt_on_error`, `detect_leaks`), symbolization problems, and sanitizer interactions (which sanitizers combine, instrumented vs uninstrumented code).
- Apply it to pasted reports, CI sanitizer failures, suppression-file diffs, flaky sanitizer findings, and "is this a false positive?" claims.
- Treat every "false positive" claim as a hypothesis to verify against known tool limitations, not a default.

## DO NOT USE FOR:

- Reviewing synchronization or ownership design in code with no sanitizer report in hand; designing error-handling policy; writing new tests unrelated to a report.
- Hardware-level debugging (core dumps without sanitizers, JTAG), or fuzzing campaign design beyond interpreting the sanitizer output a fuzzer produced.

## Required Context

Collect or infer before judging:

- The report: error kind and at least the primary stack(s). A paraphrase ("ASan says use-after-free in Foo") is enough to start but limits confidence.
- Sanitizer and build configuration: which sanitizer, compiler, optimization level, whether all linked code (including static libraries and the standard library where relevant) is instrumented.
- Runtime options and suppression files in force.
- Reproducibility: deterministic, flaky, or CI-only, and whether the failing test is parallel.
- What decision is needed: real-or-not, root cause, suppression scope, or fix routing.

If neither a report nor a concrete description of one can be established, return `Verdict: BLOCK` with one open question; do not guess. When the report is supplied but configuration items are unstated, analyze the report normally, mark those fields `undeclared`, and record configuration-dependent conclusions as open questions instead of guessing.

## Output Depth

Default to `standard`. `quick` still reports missing required context, blockers, the classification, and the root-cause frame; it only omits non-applicable checklist expansion. `standard` covers the applicable checklist with concise evidence. `exhaustive` enumerates the full checklist only when asked or when the risk surface warrants it. Whenever the selected depth is `quick` or `exhaustive` — whether user-requested or risk-selected — state it on a `Depth:` line directly after `Target:` in the report.

## Workflow

1. Parse the report anatomy: error kind, faulting access (read/write, size, address), and every stack the tool printed (access, allocation, free, previous write, thread creation, mutexes held).
2. Classify the error kind against the sanitizer's guarantees: ASan reports and UBSan reports from the default `-fsanitize=undefined` group are almost always true positives at the machine level — the open question is usually *where* the bug is, not *whether*; UBSan's opt-in non-UB checks (e.g. `unsigned-integer-overflow`, `implicit-conversion`) flag policy violations that may be intentional and follow the Decision Rules below. MSan reports are true positives only under verified full instrumentation — otherwise treat them per step 4. TSan race reports are true positives unless a happens-before edge exists that TSan cannot see (uninstrumented synchronization, custom atomics through uninstrumented code, fences it models conservatively).
3. Separate symptom from root cause: the faulting frame is where the damage surfaced; walk the allocation/free/previous-access stacks to the frame that violated the contract (freed too early, retained too long, wrote out of bounds, raced).
4. Check configuration artifacts before blaming code: mixed instrumented/uninstrumented binaries (MSan requires full instrumentation including libc++; TSan misses synchronization in uninstrumented code), container-annotation mismatches, interceptor gaps, and optimization-level effects on stacks.
5. Decide the action: fix (with owner and the root-cause frame), suppress (narrowest matcher, documented reason, link to an issue, expiry/review note), or reconfigure (instrument the missing component, fix symbolization).
6. For suppressions, verify scope: suppression by exact function/library, not wildcard-by-default; `called_from_lib:` vs `race:` semantics for TSan; suppressions must not hide first-party bugs.
7. State the verification: rerun with the fix, a regression test that fails under the sanitizer without the fix, or a documented re-review date for suppressions.

## Decision Rules

The Checklist below is the gating source of truth when these rules overlap; the rules explain rationale.

- When a TSan report is claimed to be a false positive, require the specific happens-before edge TSan cannot see (named uninstrumented synchronization mechanism); "it's protected by timing" or "it never happens in practice" are not edges — those reports are true positives.
- When an ASan heap report fires, read the three stacks in order — access, free (if any), allocation — and identify which of the three holds the contract violation; the fix belongs where the lifetime decision was wrong, which is frequently the free or retention site, not the access site.
- When `stack-use-after-return` fires, note it needs both compile-time support (emitted by default in recent Clang via `-fsanitize-address-use-after-return=runtime`; an explicit flag on GCC) and the `detect_stack_use_after_return` runtime option (default on only for recent Clang on Linux; opt-in via `ASAN_OPTIONS` elsewhere); the root cause is an escaped reference/pointer/lambda capture to a frame, and the access stack shows the consumer, not the escape — find the escape site.
- When ASan reports an ODR violation (`detect_odr_violation`), the cause is the same symbol defined differently across linked objects (duplicate static libraries, divergent inline definitions, mismatched build flags); the fix is deduplicating the definition or the link, and `odr_violation:` suppressions are a last resort for vendored duplicates.
- When MSan reports uninitialized reads, verify full instrumentation first: any uninstrumented library (including the C++ standard library not built with MSan) produces false positives by design; an MSan report from a partially instrumented build is a configuration artifact until proven otherwise.
- When LSan reports leaks at exit, remember that under the default configuration LSan reports only unreachable memory (direct/indirect leaks) — still-reachable blocks held by live globals are not reported unless `LSAN_OPTIONS=report_reachable=1` is set or the root-set scanning options (e.g. `use_globals`) have been changed, so check the options in force before classifying. Distinguish intentional leaks (a pointer deliberately dropped, e.g. a leaked singleton — candidates for `__lsan_ignore_object` or a documented `leak:` suppression) from accidental lost-pointer leaks (true bugs); shutdown-order suppression of entire libraries hides first-party leaks.
- When UBSan fires on checks in `-fsanitize=undefined` (signed overflow, misaligned access, invalid enum load, null dereference via `-fsanitize=null`), the report is a true positive about UB even if the program "works"; optimizers may exploit exactly that UB later, so do not suppress those on the grounds of current behavior. Checks outside the `undefined` group (`unsigned-integer-overflow`, `implicit-conversion`, `vptr`, `nullability-*`) flag defined or merely suspicious behavior and may be legitimately scoped or suppressed for intentional patterns (hashes, RNGs).
- When UBSan gates CI, it must be made fatal (`-fno-sanitize-recover=...` or `halt_on_error=1`) or its logs scraped: UBSan recovers and exits 0 by default, so a green pipeline does not mean no findings.
- When a sanitizer finding is flaky, treat flakiness as scheduling-dependence evidence (especially for TSan), not as evidence of a false positive; stabilize the reproduction (single test, `--gtest_repeat`, stress schedule) before triaging.
- When a suppression is proposed, require: the narrowest matcher that works, an explanatory comment with an issue link, third-party-only scope unless a first-party fix is scheduled, and a review/expiry note. A growing unreviewed suppression file is itself a finding.
- When stacks are unsymbolized or truncated, fix symbolization first (`llvm-symbolizer` on PATH, `ASAN_SYMBOLIZER_PATH`, debug info present, no stripping); triage on raw offsets produces wrong owners.
- When multiple sanitizers are wanted, remember compatibility: ASan+UBSan combine in one build; TSan and MSan each require their own build and cannot be combined with ASan; running the suite means separate CI configurations.
- When a report implicates third-party code, check whether the violation is induced by first-party misuse (bad arguments, lifetime broken by caller) before routing the fix outward; the deepest frame is not automatically the owner.

## Checklist

### Report Reading

- The error kind, faulting access, and all printed stacks are identified and named.
- The symptom frame and the root-cause frame are distinguished, with the contract violation located on a specific stack.
- Shadow-byte / address annotations (for ASan) or mutex/thread annotations (for TSan) are used, not skipped.

### Classification

- The report is classified: true positive, tool limitation (with the specific named limitation), or configuration artifact (with the specific gap).
- False-positive claims cite a concrete mechanism the tool cannot model; timing or rarity arguments are rejected.
- Instrumentation completeness has been checked for sanitizers that require it (MSan strictly; TSan for synchronization visibility).

### Action And Routing

- Every true positive has a fix owner and the root-cause frame, not just the symptom frame.
- Suppressions are narrowest-scope, commented, issue-linked, third-party-oriented, and carry a review note.
- Configuration artifacts produce configuration fixes (instrumentation, symbolization, options), not code churn or suppressions.

### Configuration Hygiene

- Sanitizer, flags, and runtime options in force are recorded; symbolization works.
- Sanitizer combinations respect compatibility constraints; CI runs each incompatible sanitizer in its own configuration.
- Suppression files are inventoried and periodically reviewed; no wildcard suppressions without documented justification.

### Tests

- Each fixed report has a regression test that fails under the sanitizer without the fix, or a documented reason why the reproduction cannot be a test. If no fixes are in scope, this item is n/a.

## Severity And Verdicts

- `CRITICAL`: a true-positive memory-safety or data-race report in first-party code that ships, or a suppression that hides such a report.
- `HIGH`: a true positive gated to tests/tools but on a path that mirrors production code; a wildcard or undocumented suppression on first-party code; triage that routed a fix to the symptom frame.
- `MEDIUM`: configuration artifacts producing noise (partial instrumentation, broken symbolization), unreviewed suppression growth, or a missing regression test for a fixed report.
- `LOW`: hygiene and clarity items with no current wrong conclusion.

Verdicts:

- `BLOCK`: neither a report nor a concrete description can be established, any `CRITICAL`, or any unmitigated `HIGH`.
- `CONCERNS`: any unmitigated `MEDIUM`, or remaining `HIGH`/`MEDIUM` findings that each have a compensating control, accepted tradeoff, or bounded reachability.
- `CLEAN`: every applicable checklist item holds; `LOW`-only findings do not block `CLEAN` and are listed as findings. If no fixes are in scope, Tests is n/a and does not block `CLEAN`.

## Output Format

```text
Verdict: BLOCK | CONCERNS | CLEAN
Target: <report, suppression diff, or configuration>
Depth: <quick | exhaustive; include this line whenever the selected depth is not standard>
Sanitizer: <ASan | TSan | UBSan | MSan | LSan, flags/options or undeclared>
Classification: <true positive | tool limitation | configuration artifact | undetermined>

Findings:
1. <short title>
  Severity: CRITICAL | HIGH | MEDIUM | LOW
  Finding type: Confirmed issue | Likely risk | Open question | Accepted tradeoff | Test gap
  Evidence: <report excerpt, stack frame, or suppression line>
  Rule: <report-reading | classification | action-routing | configuration | tests>
  Risk: <what the wrong triage decision would cost>
  Required guard: <fix site, suppression scope, or configuration change>
  Test expectation: <sanitizer regression test or N/A>

Root cause: <frame and contract violation, or undetermined with the missing evidence named>
Symptom: <faulting frame, for contrast>

Checklist status:
- Report reading: covered | missing | n/a
- Classification: covered | missing | n/a
- Action and routing: covered | missing | n/a
- Configuration hygiene: covered | missing | n/a
- Tests: covered | missing | n/a

Residual risk: <remaining caveats or None>
```

`Rule:` values map to checklist sections as follows: `report-reading` -> Report Reading; `classification` -> Classification; `action-routing` -> Action And Routing; `configuration` -> Configuration Hygiene; `tests` -> Tests.

When no material issues exist, write exactly `Findings: None` (allowed only with `CLEAN`) and list assumptions under Residual risk.

Insufficient-context mode: when neither a report nor a concrete description of one can be established, emit exactly this reduced template and stop; do not emit sanitizer, classification, root cause, or checklist status with guessed values. The `BLOCK` verdict here is triggered by the missing report, not by the finding's `LOW` severity:

```text
Verdict: BLOCK
Target: <report, suppression diff, or configuration>

Findings:
1. <missing-context short title>
  Severity: LOW
  Finding type: Open question
  Evidence: <which required context is missing>
  Rule: <report-reading | classification | action-routing | configuration | tests>
  Risk: <why no safe conclusion is possible>
  Required guard: <what context must be supplied>
  Test expectation: N/A
```

## Examples

- Symptom vs root cause: ASan `heap-use-after-free` faulting in `Render::draw()` with the free stack in `Scene::reset()` — the bug is that `reset()` frees nodes the render queue still references; fix the retention contract in `Scene`, not `draw()`.
- TSan false-positive claim rejected: "the race on `stats_` is fine because the reader runs once a second" names no happens-before edge; it is a true positive. A valid claim would be "the reader is gated by a custom futex wrapper in libuv that TSan does not instrument" — then the fix is `__tsan_acquire`/`__tsan_release` annotations or instrumenting the wrapper. `called_from_lib:` suppresses interceptor-level events invoked from the named library; it is not a fix for a race whose racing frames are first-party code.
- MSan configuration artifact: MSan reports uninitialized reads inside `std::string` in a build that links the system libc++ — partial instrumentation; rebuild libc++ with MSan or use the provided instrumented sysroot before triaging the code.

## Definition Of Done

A sanitizer triage is ready only when:

- The report anatomy is read and the root-cause frame is named, distinct from the symptom (per Report Reading).
- The classification is explicit and mechanism-backed (per Classification).
- The action is a routed fix, a scoped documented suppression, or a configuration change (per Action And Routing).
- Configuration hygiene items are recorded; incompatible sanitizers run in separate configurations.
- Fixed reports carry sanitizer regression tests per the Tests item.
