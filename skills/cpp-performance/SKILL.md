---
name: cpp-performance
description: "Use when: reviewing, designing, implementing, or debugging C++ performance hot spots involving unnecessary copies, pass-by-value of expensive types, range-for copies, misused std::move, missing noexcept on move/swap/destructor, inefficient container or string operations, missing reserve, STL algorithms on associative containers, std::endl flushing, float-to-double math promotion, oversized enums, integer-to-pointer casts, or redundant string/string_view conversions."
argument-hint: "Describe the code, API, hot path, or review target where copies, allocations, move semantics, or other runtime overhead are in question."
user-invocable: true
---

# C++ Performance

Use this skill when C++ code may pay avoidable runtime cost: copies that could be references or moves, allocations that could be hoisted or reserved, move-enabling operations that the compiler will silently downgrade to copies, or library calls that have a cheaper equivalent with identical semantics.

The goal is to remove waste that does not change observable behavior: every expensive copy has a justification, every move actually moves, every container and string operation uses the cheapest correct form, and every type that participates in moves or containers is `noexcept` where the standard library rewards it.

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
4. Audit move-enabling declarations: move ctor, move assignment, `swap`, `iter_swap`, and destructor for `noexcept`; move ctor's mem-initializers for accidental member/base copies; out-of-line defaulted destructors that block trivial destructibility.
5. Audit library-call efficiency: container growth without `reserve`, string `operator+` chains, STL algorithms on associative containers, `std::endl`, math-function float promotion, single-char `find`/`+=` literals, redundant `string`/`string_view` conversions.
6. Audit type layout: enum underlying type vs enumerator range; integer-to-pointer casts.
7. For each candidate fix, verify it preserves behavior, lifetime, and exception guarantees; classify by severity, map to a verdict, and state the regression test or benchmark each fix needs.

## Decision Rules

The Checklist below is the gating source of truth when these rules overlap; the rules explain rationale. Each rule names the clang-tidy check it encodes. The subheadings here match the Checklist sections so a rule and its gating item are found together.

Cross-cutting safety constraint (applies to every rule below): a performance fix is valid only when it preserves observable behavior, object lifetime, exception guarantees, and public API/ABI. When a suggested fix would change a public or exported signature (for example switching a by-value parameter to `const&` in a shipped header), record the compatibility impact, downgrade urgency, and route the call to a versioning decision rather than asserting a free fix.

### Copies (Parameters, Locals, Loops)

- When a function takes an expensive-to-copy type by value:
  - If the parameter is only read, pass it by `const&` (`performance-unnecessary-value-param`).
  - If the parameter is copied or assigned exactly once into longer-lived storage, keep it by value and `std::move` it into the sink (sink-parameter idiom) rather than passing `const&` and copying inside.
- When a local is copy-initialized from a `const&`-returning expression and used only as const, bind it as `const&` instead of copying (`performance-unnecessary-copy-initialization`). This is conditional on the reference not dangling: if a later mutation, `erase`, or scope exit can invalidate the source before the last use, the copy is required - flag the lifetime dependency as out-of-scope object-lifetime work and route it.
- When a range-for loop variable of expensive-to-copy type is used only as const, declare it `const&` (`performance-for-range-copy`).
- When a range-for loop variable's written type does not match the iterator's value type, an implicit per-iteration conversion copies; use `const auto&` so no conversion occurs (`performance-implicit-conversion-in-loop`).

### Moves And Returns

- When `std::move` produces no move, it is misleading and should usually be removed (`performance-move-const-arg`) - but confirm the removal does not change overload resolution (dropping `std::move` turns an rvalue into an lvalue, which can re-select a `const&` overload instead of a `T&&` one); remove it only when the selected overload is unchanged. It produces no move in each of these cases:
  - the argument is a `const` object (a move silently falls back to a copy);
  - the argument is a trivially-copyable type (move and copy are equivalent, so the `std::move` buys nothing);
  - the result is bound to a `const&` parameter (the rvalue cannot bind to a non-const sink, so no move occurs).
- When a local is copy-assigned out (e.g. `out = some;`) and is dead afterward, `std::move` it into the assignment to turn a copy into a move (no dedicated clang-tidy check; `bugprone-use-after-move` guards against doing this while the local is still read afterward).
- When returning a local lvalue eligible for the implicit move-on-return, do not declare it `const`: `const` blocks the automatic move and forces a copy (`performance-no-automatic-move`). Return a non-const local; do not add an explicit `std::move` on a plain local return (that defeats copy elision).
- When a move constructor's mem-initializer list initializes a base or member, move it, not copy it; a missing `std::move` there silently copies (`performance-move-constructor-init`).

### noexcept And Special Members

- When a type defines a move constructor or move assignment operator, mark it `noexcept`; otherwise standard containers (e.g. `vector` reallocation) fall back to copying for the strong guarantee (`performance-noexcept-move-constructor`).
- When a type defines a user-defined `swap` or `iter_swap`, mark it `noexcept` for the same container-optimization reason (`performance-noexcept-swap`).
- When a destructor carries `noexcept(expr)`, do not let `expr` evaluate to `false` (`performance-noexcept-destructor`).
- When an out-of-line defaulted destructor (`A::~A() = default;`) makes an otherwise trivially-destructible type non-trivial, remove the declaration so the type stays trivially destructible (`performance-trivially-destructible`).

### Containers, Strings, Algorithms

- When elements are appended to a `std::vector` (or vector-like type) inside a counted or range-based loop with a known final size, call `reserve` before the loop to avoid repeated reallocation (`performance-inefficient-vector-operation`).
- When building a string, prefer `+=`/`append` over chained `operator+` (which materializes temporaries), especially inside loops (`performance-inefficient-string-concatenation`).
- When passing a single-character string literal to `find`/`rfind`/`starts_with`/`ends_with`/`contains`/`operator+=` and friends, use a `char` literal instead of a length-1 string literal (`performance-faster-string-find`).
- When calling an STL algorithm (`std::find`, `std::count`, `std::lower_bound`, etc.) on an associative container that provides an equivalent method, call the method - it exploits the container's ordering (`performance-inefficient-algorithm`).
- When emitting a newline to a stream, use `'\n'`; reserve `std::endl` for the rare case where an explicit flush is required (use `std::flush` explicitly), because `std::endl` flushes every time (`performance-avoid-endl`).
- When a `std::string_view` would already satisfy a callee expecting `string_view`, do not wrap it in a temporary `std::string` (or `std::string(sv).c_str()`); pass the view directly. No dedicated `performance-*` check covers this; the redundant-`c_str()` sub-case is `readability-redundant-string-cstr` (cited under Related Checks), and the rest is manual review. The `std::string(sv).c_str()` form is only legitimate when an explicit null-terminated copy is intended.

### Types, Math, Layout

- When calling a C math function (`sin`, `asin`, ...) with a `float` argument, use the `std::` overload (or `*f` variant in C) to avoid an implicit `float`-to-`double` promotion and back (`performance-type-promotion-in-math-fn`).
- When defining an `enum`/`enum class`, choose the smallest fixed-width underlying type that holds the enumerator range to shrink memory footprint and improve cache behavior (`performance-enum-size`) - weighed against ABI stability and readability.
- When casting an integer to a pointer, recognize that provenance is lost and the optimizer is blinded; prefer pointer arithmetic on the original pointer when concealment is accidental (`performance-no-int-to-ptr`).

### Type Erasure And Callables (no clang-tidy check)

- A `std::function` heap-allocates its target unless the target fits the small-buffer **and** satisfies the implementation's small-object criteria, which are implementation- and version-specific. On current libstdc++, for example, the small-object optimization requires the callable to be **trivially copyable**, so a lambda that captures a non-trivial type - notably a `std::shared_ptr` - typically heap-allocates regardless of capture size, and shrinking such a capture below the buffer size does *not* remove the allocation (a common mistaken "fix"). Other standard libraries and future versions may differ, so confirm the behavior on the target toolchain by measuring rather than assuming. To actually avoid the allocation on a hot path, make the captured state trivially copyable (capture a raw pointer / `T*` / `string_view` whose lifetime is separately guaranteed), or avoid `std::function` entirely (a template callable parameter, `function_ref`-style non-owning view, or a hand-written type-erased class with its own inline storage). For example, `std::function<void()> f = [self]{ self->go(); };` (captures `shared_ptr` -> heap) becomes `std::function<void()> f = [raw = self.get()]{ raw->go(); };` (captures a raw pointer -> fits the small buffer, no heap) **only when the target's lifetime is separately guaranteed for the call** (otherwise this trades an allocation for a dangling pointer - an object-lifetime concern to resolve before applying the fix). Verify with an allocation count, not by reading the capture list. No lint check catches this - it requires measurement.
- Per-call `std::function` construction on a hot path (per-request/per-message handlers stored or rebuilt each iteration) multiplies this allocation; hoist a stable callable to a member or pass it by reference rather than reconstructing it.

### Related Checks Outside The performance-* Namespace

These clang-tidy checks live in other namespaces but address the same copy/allocation cost. Apply them, but cite the actual check name (not `performance-*`).

- When a container insertion (`push_back`/`push`/`push_front`) is given an explicitly-constructed temporary of the element type, use the `emplace`-family method and pass the constructor arguments directly, avoiding the temporary's move/copy (`modernize-use-emplace`). Do not transform when the argument is a `new` expression or bit-field (exception-safety / binding rules), matching the check's own exclusions.
- When a constructor takes a `const&` parameter only to copy it into a member, take it by value and `std::move` it into the member, letting callers move from rvalues (`modernize-pass-by-value`). This overlaps the sink-parameter rule under Copies; cite whichever check the reader runs. The transformation is only safe when the parameter is used exactly once and no hidden reference mutates the source before the init-list.
- When `std::remove`/`std::unique`/`std::remove_if` results feed a single-argument `erase`, only one element is removed and the algorithm's wasted shuffle is kept; use the two-argument `erase(first, last)` (erase-remove idiom) (`bugprone-inaccurate-erase`).
- When emptiness is tested with `size()`/`length()`/`std::size() == 0`, use `empty()`; it is O(1) for every container (e.g. `std::list::size` may be O(n) historically) and clearer (`readability-container-size-empty`).
- When membership is tested with `count()` or `find() == end()`, use `contains()` (C++20 associative containers, C++23 strings); `contains` avoids `count`'s extra work on multi-key containers (`readability-container-contains`).
- When `std::string::c_str()`/`data()` is passed to an API that already accepts `std::string`/`string_view`, drop the call to avoid a needless C-string round-trip (`readability-redundant-string-cstr`).
- Struct field ordering that wastes space to padding (hurting cache density) is detectable only by the path-sensitive Clang Static Analyzer (`clang-analyzer-optin.performance.Padding`), not by clang-tidy lint; flag the pattern but recommend running the analyzer rather than asserting a precise layout.

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

- User-defined move constructor and move assignment are `noexcept` (so containers move rather than copy).
- User-defined `swap`/`iter_swap` are `noexcept`; no destructor carries a non-literal `noexcept(false)`.
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
- `HIGH`: a clear, behavior-preserving waste on a frequently executed path (missing `reserve` before a large loop, expensive value parameter on a hot call, missing `noexcept` on a move type stored in containers).
- `MEDIUM`: real but bounded or cold-path waste, or a latent issue (missing `noexcept`, `const`-blocked return move, redundant conversion) that future edits or scale will amplify.
- `LOW`: micro-optimization with negligible measured impact (`std::endl` on a rarely written stream, single-char literal off the hot path) - flag for consistency, not as a blocker.

Verdicts:

- `BLOCK`: missing required context, any `CRITICAL`, or any unmitigated `HIGH`.
- `CONCERNS`: remaining `HIGH`/`MEDIUM` findings each have a compensating justification, accepted tradeoff, or bounded impact.
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

- Expensive value parameter: `void store(std::string s) { m_name = s; }` copies twice. If `s` is a read-only sink, write `m_name = std::move(s);` (keep by value); if only read, take `const std::string&`. (`performance-unnecessary-value-param`.)
- Const blocks return move: `const std::vector<int> v = build(); return v;` copies on return because `const` disables the automatic move. Drop `const` so the return moves. (`performance-no-automatic-move`.)
- Missing reserve: `for (int i = 0; i < n; ++i) out.push_back(f(i));` reallocates repeatedly. Add `out.reserve(n);` before the loop. (`performance-inefficient-vector-operation`.)
- Pointless move: `const std::string s; sink(std::move(s));` cannot move a `const`; the `std::move` is misleading and a silent copy still happens. Remove it. (`performance-move-const-arg`.)
- Missing noexcept: a `Widget(Widget&&)` without `noexcept` makes `std::vector<Widget>` copy every element on growth. Mark it `noexcept`. (`performance-noexcept-move-constructor`.)

## Definition Of Done

A performance change is ready only when:

- Every expensive copy in the target is either eliminated (reference, move, or `reserve`) or has a stated justification (lifetime dependency, required overload, accepted tradeoff).
- Every `std::move` provably enables a move, and no `const` declaration or value-category mistake silently downgrades a move to a copy.
- Move/`swap` types are `noexcept` where the standard library rewards it, and no fix weakens an exception guarantee.
- Each library-call substitution (container, string, algorithm, stream, math, conversion) preserves observable behavior.
- Hot-path fixes carry behavior-preserving regression tests; throughput/allocation claims carry a benchmark or allocation count. If no hot-path fixes were made, the Tests and measurement item is n/a and does not block `CLEAN`.
- Any deferred lifetime or concurrency question raised by a candidate fix is named and routed to the governing skill rather than silently assumed safe.
