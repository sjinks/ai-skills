---
name: cpp-error-handling-design
description: "Use when: designing, reviewing, or refactoring C++ error handling policy, exceptions vs std::expected vs error codes, exception safety guarantees (basic, strong, nothrow), RAII rollback, noexcept and move semantics interactions, error propagation across module or ABI or thread or coroutine boundaries, std::error_code categories, terminate paths, or destructor and swap exception rules."
argument-hint: "Describe the code, API, error policy, or boundary where error handling design or exception safety is in question."
user-invocable: true
---

# C++ Error Handling Design

Use this skill when C++ code must choose, implement, or review an error-reporting strategy: exceptions, `std::expected`/result types, `std::error_code`, status enums, or a mix — and when exception-safety guarantees, rollback, or propagation across boundaries are in question. `std::expected` requires C++23; pre-C++23 codebases substitute an equivalent result type (`tl::expected`, `boost::outcome`, `absl::StatusOr`, or an in-house one), and every `expected` mention in this skill covers those equivalents.

The goal is a coherent error policy: every function declares which failures it can report, by which channel, with which safety guarantee, and every boundary translates errors deliberately instead of leaking or swallowing them.

**UTILITY SKILL.** INVOKES: read-only file access for supplied targets; no other tools or skills. FOR SINGLE OPERATIONS: use for focused error-policy review, exception-safety analysis, error-type design, or boundary translation questions.

## Scope

- Use this skill for choosing between exceptions, `std::expected`/result types, and `std::error_code`-style reporting; exception-safety guarantees (basic, strong, nothrow) and how to achieve them with RAII and commit-rollback patterns; `noexcept` placement and its interaction with move operations and containers; destructor/swap exception rules; `std::terminate` paths; and error translation at module, ABI, thread, callback, and coroutine boundaries.
- Apply it to API design ("how should this library report failures?"), reviews of throwing code for safety guarantees, refactors between error styles, and error-category/domain design for `std::error_code` or custom result types.
- Treat error-handling consistency as a contract: mixed styles inside one layer without a documented translation rule are findings.

## DO NOT USE FOR:

- Logging/observability pipeline design; retry/backoff and distributed resilience policy; API/ABI compatibility classification of an existing boundary change.
- Debugging a specific crash where the task is root-cause analysis rather than error-policy or safety-guarantee review.

## Required Context

Collect or infer before judging:

- Target: files, diff, API, or design under review.
- Error policy in force: exceptions allowed or banned (`-fno-exceptions`?), result-type conventions, error-code categories, and what downstream consumers expect.
- Boundaries crossed: module/library, ABI, `extern "C"`, threads, callbacks, coroutines/async, process exits.
- Failure classes in scope: allocation failure, I/O, validation, contract violations (programming bugs), and which are recoverable by the caller.
- Existing tests for failure paths.

If the target cannot be established, return `Verdict: BLOCK` with one open question; do not guess. When the target is supplied but the policy is unstated, analyze policy-independent findings (safety-guarantee violations, terminate paths, swallowed errors) normally, state the policy as `undeclared`, and record policy-dependent recommendations as open questions instead of guessing the policy.

## Output Depth

Default to `standard`. `quick` still reports missing required context, blockers, unmitigated HIGH/CRITICAL findings, and target-specific concerns; it only omits non-applicable checklist expansion. `standard` covers the applicable checklist with concise evidence. `exhaustive` enumerates the full checklist only when asked or when the risk surface warrants it. Name the selected depth when the user asks for `quick` or `exhaustive`.

## Workflow

1. Establish the error policy: which channel reports what, per layer, and whether exceptions are permitted at all.
2. Separate failure classes: recoverable runtime failures (report via the chosen channel), programming-bug contract violations (assert/terminate policy), and unrepresentable states (type design).
3. For each mutating operation, name its safety guarantee (basic, strong, nothrow) and verify the implementation delivers it — partial mutations rolled back or never observable.
4. Check `noexcept` placement: move constructors/assignment, swap, destructors, and functions whose failure is unrecoverable; verify nothing `noexcept` can throw through.
5. Check every boundary: which errors cross, how they are translated, and that none escape into `extern "C"`, any thread entry point, any destructor, or `noexcept` frames.
6. Check completeness of handling: every error channel is consumed (no discarded `expected`/`error_code`), no catch-and-swallow without a documented reason, and termination paths are intentional.
7. Classify findings by severity, map to a verdict, and state the failure-path tests each fix needs.

## Decision Rules

The Checklist below is the gating source of truth when these rules overlap; the rules explain rationale.

- When failures are recoverable by callers and call sites are not dominated by immediate-handling, prefer exceptions for deep call stacks and constructors; prefer `std::expected`/result types (or a pre-C++23 equivalent such as `tl::expected` or `absl::StatusOr`) when failures are frequent, local, part of the domain (parse/validate), or exceptions are banned; prefer `std::error_code` parameters mainly at OS/legacy boundaries. Mixing styles is fine across layers only with an explicit translation rule at each boundary.
- When a failure indicates a programming bug (violated precondition, broken invariant), do not report it through the recoverable-error channel: assert/contract-check and terminate policy applies; recoverable channels are for environmental and input failures.
- When a constructor can fail and exceptions are unavailable, use a named factory returning `expected`/optional and make the raw constructor private or trivially non-failing; half-constructed observable states are findings.
- When a mutating function promises the strong guarantee, implement it as commit-rollback: do all throwing work on the side (copies, temporaries), then commit with nothrow operations (swap, pointer/move assignment). Claiming strong while mutating in place across throwing calls is a finding.
- When writing move constructors, move assignment, and swap, make them `noexcept` whenever possible: standard containers fall back to copying (or lose the strong guarantee) when moves may throw; a throwing move that could be nothrow is a performance and correctness finding.
- When a destructor can encounter failures (flush, close, commit), the destructor must swallow or log them and stay nothrow; offer an explicit `close()`/`commit()` API for callers who need the error. Destructors are `noexcept` by default (absent a `noexcept(false)` declaration or a potentially-throwing base/member destructor), so throwing out of one terminates immediately, unwinding or not; declaring `noexcept(false)` to permit it is itself a finding.
- When `noexcept` is on a function whose callees may throw, verify the catch-or-impossible argument; an exception reaching a `noexcept` boundary calls `std::terminate` with no unwinding guarantee.
- When errors cross threads, futures/promises, queued callbacks, or coroutine awaitables, the carrier must transport the error (`std::exception_ptr`, an `expected` in the message, or `promise.set_exception(std::current_exception())`); a detached or fire-and-forget path with no error sink is a finding.
- When `expected`/`error_code` results can be ignored silently, mark the types or functions `[[nodiscard]]`; discarded error channels are findings.
- When designing `std::error_code` domains, give each subsystem its own category with stable values and map to `std::errc` conditions for portable comparison; comparing raw integer values across categories is a finding.
- When catch blocks appear, they must rethrow, translate, recover, or document why swallowing is correct; `catch (...) {}` without rationale is a finding. Catch by reference; catching polymorphic exceptions by value slices.

## Checklist

### Policy And Channels

- The error policy per layer is explicit: which channel (exceptions, expected, error_code) reports which failure class, and whether exceptions are enabled.
- Programming-bug detection (asserts/contracts/terminate) is separated from recoverable-error reporting.
- Mixed styles only occur across documented translation boundaries, not within a layer.

### Safety Guarantees

- Every mutating public operation has a named guarantee (basic, strong, nothrow), documented or evident, and the implementation delivers it.
- Strong-guarantee operations use commit-rollback or equivalent; no observable partial mutation on the throw path.
- RAII owns every resource acquired on paths that can throw; no manual cleanup that unwinding skips.

### Noexcept And Special Functions

- Move constructors, move assignment, and swap are `noexcept` where their operations permit; destructors never throw.
- `noexcept` claims are backed by catch-or-impossible reasoning; no throwing callee reaches a `noexcept` frame unhandled.
- Functions whose failure is unrecoverable (or where unwinding would be unsafe) are deliberately `noexcept` rather than accidentally.

### Boundaries And Propagation

- Exceptions do not escape `extern "C"`, thread entry points, destructors, or callback frames owned by foreign code; each such boundary translates or stops them.
- Cross-thread and async paths carry errors (`std::exception_ptr`, `expected`, or `std::promise::set_exception`); no error-free fire-and-forget without documented intent.
- Boundary translations preserve enough information to act on (error class, context), not just a generic failure flag.

### Consumption And Completeness

- Error-returning functions and result types are `[[nodiscard]]` or otherwise unignorable; no silently discarded error channel.
- Catch blocks rethrow, translate, recover, or document swallowing; catches are by reference.
- Every failure class in scope has a defined consumer; no error path ends in undefined or unobserved state.

### Tests

- Failure paths have tests: thrown/returned errors are exercised, strong-guarantee rollback is asserted (object state unchanged after a failed operation), and boundary translation is verified. If no failure-path changes are in scope, this item is n/a.

## Severity And Verdicts

- `CRITICAL`: an error path that corrupts state (partial mutation under a claimed strong guarantee, double-release on unwind), terminates the process unintentionally (throwing destructor, exception through `noexcept`/`extern "C"`), or silently loses errors that callers must act on.
- `HIGH`: a guarantee claimed but not delivered, a throwing move that disables container guarantees, a swallowed error with plausible recovery need, or an async path with no error sink.
- `MEDIUM`: undocumented policy or guarantees, missing `[[nodiscard]]` on error channels, missing translation documentation at a boundary, or a test gap on changed failure paths.
- `LOW`: clarity, naming, or hardening with no current incorrect behavior.

Verdicts:

- `BLOCK`: the target cannot be established, any `CRITICAL`, or any unmitigated `HIGH`. Other missing Required Context items (policy, boundaries, failure classes, tests) become open-question findings, not automatic blocks.
- `CONCERNS`: any unmitigated `MEDIUM`, or remaining `HIGH`/`MEDIUM` findings that each have a compensating control, accepted tradeoff, or bounded reachability.
- `CLEAN`: every applicable checklist item holds; `LOW`-only findings do not block `CLEAN` and are listed as findings. If no failure-path changes are in scope, Tests is n/a and does not block `CLEAN`. For design-stage targets with no code or tests yet, the best achievable verdict is `CONCERNS` with test expectations recorded per finding.

## Output Format

```text
Verdict: BLOCK | CONCERNS | CLEAN
Target: <files, diff, API, or design>
Error policy: <exceptions | expected | error_code | mixed-with-translation | undeclared>
Boundaries: <module, ABI, extern "C", threads, callbacks, coroutines in scope>

Findings:
1. <short title>
  Severity: CRITICAL | HIGH | MEDIUM | LOW
  Classification: Confirmed issue | Likely risk | Open question | Accepted tradeoff | Test gap
  Evidence: <file:line, diff hunk, or design sentence>
  Rule: <policy | guarantees | noexcept | boundaries | consumption | tests>
  Risk: <what is lost, corrupted, or terminated on the failure path>
  Required guard: <policy, design, or implementation change>
  Test expectation: <failure-path test or N/A>

Checklist status:
- Policy and channels: covered | missing | n/a
- Safety guarantees: covered | missing | n/a
- Noexcept and special functions: covered | missing | n/a
- Boundaries and propagation: covered | missing | n/a
- Consumption and completeness: covered | missing | n/a
- Tests: covered | missing | n/a

Residual risk: <remaining caveats or None>
```

`Rule:` values map to checklist sections as follows: `policy` -> Policy And Channels; `guarantees` -> Safety Guarantees; `noexcept` -> Noexcept And Special Functions; `boundaries` -> Boundaries And Propagation; `consumption` -> Consumption And Completeness; `tests` -> Tests.

When no material issues exist, write exactly `Findings: None` (allowed only with `CLEAN`) and list assumptions under Residual risk. For design-stage targets that earn `CONCERNS` solely because tests cannot exist yet, emit one `Test gap` finding with `Rule: tests` listing the required test expectations instead of an empty findings list.

Insufficient-context mode: when the target itself cannot be established, emit exactly this reduced template and stop; do not emit policy, boundaries, or checklist status with guessed values (an unstated policy with a supplied target follows the undeclared-policy rule in Required Context instead):

```text
Verdict: BLOCK
Target: <files, diff, API, or design>

Findings:
1. <missing-context short title>
  Severity: LOW
  Classification: Open question
  Evidence: <which required context is missing>
  Rule: <policy | guarantees | noexcept | boundaries | consumption | tests>
  Risk: <why no safe conclusion is possible>
  Required guard: <what context must be supplied>
  Test expectation: N/A
```

## Examples

- Broken strong guarantee: `void Config::merge(const Config& o) { for (auto& [k,v] : o.map_) map_.insert_or_assign(k, v); }` claims strong in its docs, but a throw mid-loop leaves a half-merged map. Fix: build the merged map on the side, then `swap` (commit-rollback).
- Throwing destructor: `~Transaction() { commit(); }` where `commit()` throws on conflict — the implicitly-noexcept destructor terminates the process on any throw. Fix: destructor rolls back nothrow; explicit `commit()` for callers who need the error.
- Lost async error: `std::thread([cfg]{ reload(cfg); }).detach();` — a throw in `reload` terminates the process; a returned error would have no consumer. Fix: run through a future/promise or a queue that transports `std::exception_ptr`/`expected` to an owner.

## Definition Of Done

An error-handling change is ready only when:

- The policy and channel per failure class is explicit, with translation rules at every boundary (per Policy And Channels).
- Each mutating operation's guarantee is named and delivered (per Safety Guarantees).
- `noexcept` placement and special functions satisfy their checklist section; no unintended terminate paths remain.
- Every error channel has a consumer; nothing is silently discarded or swallowed without rationale.
- Failure-path tests cover the changed behavior per the Tests item.
