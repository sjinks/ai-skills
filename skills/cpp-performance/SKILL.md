---
name: cpp-performance
description: "Use when: reviewing, designing, implementing, or debugging C++ performance hot spots involving unnecessary copies, pass-by-value of expensive types, range-for copies, misused std::move, missing noexcept on move/swap/destructor, inefficient container or string operations, missing reserve, STL algorithms on associative containers, std::endl flushing, float-to-double math promotion, oversized enums, integer-to-pointer casts, or redundant string/string_view conversions."
argument-hint: "Describe the code, API, hot path, or review target where copies, allocations, move semantics, or other runtime overhead are in question."
---

# C++ Performance

Use this skill when C++ code may pay avoidable runtime cost: copies that could be references or moves, allocations that could be hoisted or reserved, move-enabling operations that the compiler will silently downgrade to copies, or library calls that have a cheaper equivalent with identical semantics.

The goal is to remove waste that does not change observable behavior: every expensive copy has a justification, every move actually moves, every container and string operation uses the cheapest correct form, and move/swap exception specifications match their operations. Require `noexcept` only when the operations cannot throw; accurate exception specifications take precedence over library optimizations.

**UTILITY SKILL.** INVOKES: read-only file access for supplied targets; no other tools or skills. FOR SINGLE OPERATIONS: use for focused copy/allocation review, move-semantics correctness, `noexcept` audit, or hot-path tuning.

The clang-tidy `performance-*` checks are the canonical catalog this skill encodes, plus a small set of cost-relevant checks from the `modernize-*`, `bugprone-*`, `readability-*`, and `clang-analyzer-*` namespaces (see Related Checks Outside The performance-* Namespace); cite the matching check name in findings so the reader can cross-reference and optionally automate the fix.

## Scope

- Use this skill for: unnecessary copies (value parameters, copy-initialized locals, range-for loop variables, implicit conversions in range-for), broken or pointless `std::move` (move of const, move of trivially-copyable, move into a const-ref sink, missing `std::move` on a copy-assigned local, `const` locals that block automatic move on return), move constructors that copy a base or member, missing `noexcept` on move constructor / move assignment / `swap` / `iter_swap` / destructor, inefficient container growth (`push_back`/`emplace_back` in a loop without `reserve`), inefficient string building (`operator+` chains instead of `+=`/`append`), STL free-function algorithms on associative containers that have a method form, `std::endl` where `'\n'` suffices, `float`-to-`double` promotion in C math functions, oversized enum underlying types, integer-to-pointer casts that lose provenance, redundant `string`/`string_view` conversions, single-character string-literal arguments to `find`/`+=` family, and out-of-line defaulted destructors that block trivial destructibility.
- Use it also for the closely-related cost checks in other namespaces: `emplace` vs insert-of-temporary (`modernize-use-emplace`), pass-by-value-and-move constructors (`modernize-pass-by-value`), the erase-remove idiom (`bugprone-inaccurate-erase`), `empty()` vs `size() == 0` (`readability-container-size-empty`), `contains()` vs `count`/`find` (`readability-container-contains`), redundant `c_str()`/`data()` (`readability-redundant-string-cstr`), and struct padding (`clang-analyzer-optin.performance.Padding`).
- Apply it to API signatures (by-value vs by-const-ref vs by-value-and-move), data-member and return-value move flow, type definitions that go into standard containers, and tight loops where per-iteration cost multiplies.
- Keep the review centered on runtime cost with preserved semantics. The performance fix must be a behavior-preserving transformation; if a cheaper form changes observable behavior, lifetime, or exception guarantees, it is out of scope as a pure performance change.

## DO NOT USE FOR:

- Algorithmic complexity redesign, data-structure selection, caching strategy, I/O batching, or system-level throughput work that is not a local source-level transformation.
- Lifetime/dangling analysis when replacing a copy with a reference (out of scope: that is object-lifetime review), or data-race/synchronization correctness of shared state (out of scope: that is concurrency review). Name the out-of-scope concern and route it instead of judging it here.
- Coroutine frame or awaiter cost mechanics, micro-benchmark authoring, compiler flag / link-time-optimization tuning, or correctness/style review with no runtime-cost dimension.

## Required Context

Collect or infer before judging:

- Target: files, diff, API, type definition, or hot-path snippet under review.
- Type cost: for each type in question, whether it is trivially copyable, expensive to copy (non-trivial copy ctor/dtor, owns heap memory), and whether it has move operations.
- Usage shape: is the cost on a hot path or per-iteration; how many times per call the copy/allocation occurs; whether sizes are known ahead of a loop. Absent a profile or benchmark, treat a site as a "hot path" only when it is a loop over caller-controlled or unbounded input, per-connection/per-request/per-message code, or a site the user names as hot; otherwise mark the path as unverified and cap severity at MEDIUM (see Severity And Verdicts).
- Semantic constraints: does a candidate copy outlive its source (so a reference would dangle); does a call rely on a specific overload, exception guarantee, or value category.
- Existing tests, benchmarks, or profiles relevant to the hot path.

If the target cannot be seen, or a type's copy/move cost cannot be established, return `Verdict: BLOCK` with one open question. Do not guess whether a type is expensive to copy. Insufficient-context mode takes precedence over pattern-level decision rules: general rules may be cited as context, but no verdict other than `BLOCK` may rest on an unseen target or an unknown-cost type.

## Output Depth

Default to `standard`. `quick` still reports missing required context, blockers, unmitigated HIGH/CRITICAL findings, and target-specific concerns; it only omits non-applicable checklist expansion. `standard` covers the applicable checklist with concise evidence. `exhaustive` enumerates the full checklist only when asked or when the change surface warrants it. Name the selected depth when the user asks for `quick` or `exhaustive`.

## Workflow

1. Inventory types: for each type that is copied, passed, returned, stored, or moved in the target, classify it as trivially copyable, cheap, or expensive to copy.
2. Trace copies: find every value parameter, copy-initialized local, range-for loop variable, and implicit conversion in a range-for; for each expensive-to-copy one, decide const-ref, move-in, or justified copy.
3. Trace moves: find every `std::move`/`std::forward`, every return of a local, every copy-assignment of a local that is dead afterward; confirm each move can and does happen, and that no `const` or value-category mistake silently downgrades it to a copy.
4. Audit move-enabling declarations: move ctor, move assignment, `swap`, `iter_swap`, and destructor for accurate exception specifications; require `noexcept` only when the operations cannot throw. Check move ctor mem-initializers for accidental member/base copies and out-of-line defaulted destructors for blocked trivial destructibility.
5. Audit library-call efficiency: container growth without `reserve`, string `operator+` chains, STL algorithms on associative containers, `std::endl`, math-function float promotion, single-char `find`/`+=` literals, redundant `string`/`string_view` conversions.
6. Audit type layout: enum underlying type vs enumerator range; integer-to-pointer casts.
7. For each candidate fix, verify it preserves behavior, lifetime, and exception guarantees; classify by severity, map to a verdict, and state the regression test or benchmark each fix needs.

## Decision Rules

The Checklist is the gating source of truth. Evaluate every applicable item; do not skip a category merely because its explanations are in a reference.

Cross-cutting safety constraint (applies to every rule below): a performance fix is valid only when it preserves observable behavior, object lifetime, exception guarantees, and public API/ABI. When a suggested fix would change a public or exported signature (for example switching a by-value parameter to `const&` in a shipped header), record the compatibility impact, downgrade urgency, and route the call to a versioning decision rather than asserting a free fix.

Read [copy and move explanations](references/copies-moves.md) for applicable value-passing, return, and special-member checks. Read [library cost explanations](references/library-costs.md) for applicable library, layout, and callable checks. These references provide rationale, analyzer mappings, and exceptions; they do not replace the Checklist.

## Checklist

### Copies (Parameters, Locals, Loops)

- Expensive-to-copy value parameters that are only read are `const&`; sink parameters are taken by value and `std::move`d into storage exactly once.
- Copy-initialized locals used only as const are `const&` where the source provably outlives the last use; otherwise the lifetime dependency is documented and the copy is justified.
- Range-for loop variables of expensive types are `const&`; `const auto&` is used where the element type would otherwise force an implicit conversion copy.

### Moves And Returns

- Every `std::move`/`std::forward` actually enables a move: no move of `const`, no move of trivially-copyable, no move into a `const&` sink, no `std::move` on a plain local return that defeats copy elision.
- Locals copy-assigned out and then dead are moved out.
- Returned local lvalues eligible for automatic move are not `const`.
- Move-constructor mem-initializers move (not copy) their bases and members.

### noexcept And Special Members

- User-defined move constructor and move assignment are `noexcept` when their operations cannot throw; throwing operations retain an accurate exception specification and document the cost tradeoff.
- User-defined `swap`/`iter_swap` are `noexcept` when their operations cannot throw; destructor exception specifications match the implementation. Never add `noexcept` solely to silence a diagnostic.
- Out-of-line defaulted destructors that needlessly block trivial destructibility are removed.

### Containers, Strings, Algorithms

- Vector (and vector-like) appends in a known-size loop are preceded by `reserve`.
- Strings are built with `+=`/`append`, not chained `operator+`, especially in loops; single-char literals use `char` overloads.
- Algorithms on associative containers use the container's method form.
- `'\n'` is used instead of `std::endl` unless an explicit flush is intended.
- No redundant `string`/`string_view` conversions; `string_view` is passed directly where expected.

### Types, Math, Layout

- C math functions on `float` use `std::` overloads to avoid `float`->`double` promotion.
- Enum underlying types match the enumerator range where footprint matters and ABI permits.
- Integer-to-pointer casts are justified; accidental provenance loss is rewritten as pointer arithmetic.
- Hot-path `std::function`s do not capture non-trivially-copyable state (e.g. `shared_ptr`) expecting the small-buffer optimization; where the allocation matters, the captured state is trivially copyable or `std::function` is replaced, verified by allocation count.

### Related Checks Outside The performance-* Namespace

- Container insertions of explicit temporaries use the `emplace` family (`modernize-use-emplace`); constructors that copy a parameter into a member take it by value and move (`modernize-pass-by-value`).
- `std::remove`/`unique` results use the two-argument `erase` (`bugprone-inaccurate-erase`); emptiness uses `empty()` (`readability-container-size-empty`); membership uses `contains()` (`readability-container-contains`); no redundant `c_str()`/`data()` (`readability-redundant-string-cstr`).
- Padding-heavy struct layouts are referred to the static analyzer (`clang-analyzer-optin.performance.Padding`) rather than asserted by lint.

### Tests And Measurement

- Each fix on a hot path has a regression test asserting preserved behavior; where the claim is throughput/allocation, a benchmark or allocation count backs it. Cold-path micro-fixes note that the benefit is incidental and may be skipped if they hurt clarity.

## Severity And Verdicts

Severity reflects expected runtime impact, not just pattern presence: the same anti-pattern is higher severity on a hot path or per-iteration than in cold setup code. Use the Required Context definition of "hot path"; when a site cannot be confirmed hot (no profile, benchmark, or qualifying structural signal), mark the path unverified and cap the finding at `MEDIUM`.

- `CRITICAL`: an avoidable copy, allocation, or copy-instead-of-move on a hot or per-iteration path that dominates the operation's cost (e.g. deep copy of a large container every iteration, container move falling back to copy during reallocation of many large elements).
- `HIGH`: a clear, behavior-preserving waste on a frequently executed path (missing `reserve` before a large loop, expensive value parameter on a hot call, missing `noexcept` on a proven non-throwing move operation used by containers).
- `MEDIUM`: real but bounded or cold-path waste, or a latent issue (missing `noexcept` on a proven non-throwing operation, `const`-blocked return move, redundant conversion) that future edits or scale will amplify.
- `LOW`: micro-optimization with negligible measured impact (`std::endl` on a rarely written stream, single-char literal off the hot path) - flag for consistency, not as a blocker.

Verdicts (apply BLOCK first, then CONCERNS, otherwise CLEAN subject to the stated design-stage limitation):

- `BLOCK`: missing required context, any `CRITICAL`, or any unmitigated `HIGH`.
- `CONCERNS`: no BLOCK condition applies, but any finding remains or an applicable checklist item is missing. This includes unmitigated MEDIUM/LOW findings and compensated HIGH findings. Record the justification or required correction per finding.
- `CLEAN`: every applicable checklist item holds and hot-path fixes have behavior-preserving test coverage. For design-stage or definition-only targets with no benchmarks yet, the best achievable verdict is `CONCERNS` with measurement expectations recorded per finding.

A performance finding must never be promoted over a correctness or lifetime concern: if applying the cheaper form risks a dangling reference, changed overload resolution, or weakened exception guarantee, downgrade or withdraw the finding and route it to the governing concern (object-lifetime or concurrency correctness).

## Output Format

```text
Verdict: BLOCK | CONCERNS | CLEAN
Target: <files, diff, API, type, or hot path>
Type costs: <which types are trivially-copyable | cheap | expensive-to-copy in scope>
Hot paths: <loops or frequently-called sites in scope, or None identified>

Findings:
1. <short title>
  Severity: CRITICAL | HIGH | MEDIUM | LOW
  Classification: Confirmed waste | Likely waste | Open question | Accepted tradeoff | Test/measurement gap
  Evidence: <file:line, diff hunk, or design sentence>
  Rule: <copies | moves-returns | noexcept-special-members | containers-strings-algorithms | types-math-layout | related-checks | tests-measurement>
  Check: <clang-tidy check name (performance-* or the related-checks namespace), or N/A>
  Cost: <what is copied/allocated/flushed, how often, and on which path>
  Behavior-preserving fix: <the cheaper equivalent form>
  Test expectation: <regression test, benchmark, allocation count, or N/A>

Checklist status:
- Copies (parameters, locals, loops): covered | missing | n/a
- Moves and returns: covered | missing | n/a
- noexcept and special members: covered | missing | n/a
- Containers, strings, algorithms: covered | missing | n/a
- Types, math, layout: covered | missing | n/a
- Related checks outside the performance-* namespace: covered | missing | n/a
- Tests and measurement: covered | missing | n/a

Residual risk: <remaining caveats, deferred lifetime/concurrency questions, or None>
```

`Rule:` values map to checklist sections as follows: `copies` -> Copies (Parameters, Locals, Loops); `moves-returns` -> Moves And Returns; `noexcept-special-members` -> noexcept And Special Members; `containers-strings-algorithms` -> Containers, Strings, Algorithms; `types-math-layout` -> Types, Math, Layout; `related-checks` -> Related Checks Outside The performance-* Namespace; `tests-measurement` -> Tests And Measurement.

When no material issues exist, write exactly `Findings: None` (allowed only with `CLEAN`) and list assumptions under Residual risk. For definition-only or design-stage targets that earn `CONCERNS` solely because measurement cannot exist yet, emit one `Test/measurement gap` finding with `Rule: tests-measurement` listing the required evidence instead of an empty findings list.

Insufficient-context mode: when the target cannot be seen or a type's copy/move cost cannot be established, emit exactly this reduced template and stop; do not emit type costs, hot paths, or checklist status with guessed values:

```text
Verdict: BLOCK
Target: <files, diff, API, type, or hot path>

Findings:
1. <missing-context short title>
  Severity: LOW
  Classification: Open question
  Evidence: <which required context is missing>
  Rule: <copies | moves-returns | noexcept-special-members | containers-strings-algorithms | types-math-layout | related-checks>
  Check: <clang-tidy check name, or N/A>
  Cost: <why no safe conclusion is possible>
  Behavior-preserving fix: <what context must be supplied>
  Test expectation: N/A
```

## Examples

Read [examples](references/examples.md) for partial illustrations of common findings. They do not add requirements or authorize a transformation without the core safety checks.

## Definition Of Done

A performance change is ready only when:

- Every expensive copy in the target is either eliminated (reference, move, or `reserve`) or has a stated justification (lifetime dependency, required overload, accepted tradeoff).
- Every `std::move` provably enables a move, and no `const` declaration or value-category mistake silently downgrades a move to a copy.
- Move/`swap` operations are `noexcept` only when their operations cannot throw; otherwise retain an accurate exception specification. No fix weakens an exception guarantee.
- Each library-call substitution (container, string, algorithm, stream, math, conversion) preserves observable behavior.
- Hot-path fixes carry behavior-preserving regression tests; throughput/allocation claims carry a benchmark or allocation count. If no hot-path fixes were made, the Tests and measurement item is n/a and does not block `CLEAN`.
- Any deferred lifetime or concurrency question raised by a candidate fix is named and routed to the governing skill rather than silently assumed safe.
