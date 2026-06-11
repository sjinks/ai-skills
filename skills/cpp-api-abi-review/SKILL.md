---
name: cpp-api-abi-review
description: "Use when: reviewing, designing, or evolving C++ library public headers and binary interfaces, including ABI stability, ABI breaks, ODR violations, noexcept contracts, pimpl, inline functions and templates at API boundaries, default arguments vs overloads, extern \"C\" boundaries, symbol visibility, versioned or inline namespaces, header hygiene, and shared-library compatibility."
argument-hint: "Describe the public header, API change, library boundary, versioning policy, or compatibility question under review."
user-invocable: true
---

# C++ API And ABI Review

Use this skill when C++ code defines or changes a library boundary that other code compiles or links against: public headers, exported classes and functions, shared-library interfaces, or plugin ABIs.

The goal is to make every boundary contract explicit: what is API (source compatibility), what is ABI (binary compatibility), which changes break each, and how the library versions and communicates those breaks.

**UTILITY SKILL.** INVOKES: read-only file access for supplied targets; no other tools or skills. FOR SINGLE OPERATIONS: use for focused header review, ABI-impact analysis of a change, boundary design, or compatibility policy questions.

## Scope

- Use this skill for public header hygiene, ABI stability analysis of class/function changes, ODR risk, `noexcept` as an API contract, inline functions and templates crossing library boundaries, default arguments vs overloads, pimpl and other compilation-firewall idioms, symbol visibility and export macros, `extern "C"` boundaries, and versioned/inline namespaces.
- Apply it to diffs against installed/public headers, new public APIs, plugin interfaces, and questions like "can I change this without breaking downstream binaries?".
- Distinguish three compatibility levels in every answer: source (API), binary (ABI), and semantic (behavioral contract).

## DO NOT USE FOR:

- Internal refactors with no exported or installed surface; build-system mechanics; packaging/distribution policy.
- General API ergonomics or naming review with no compatibility, ODR, or boundary question.

## Required Context

Collect or infer before judging:

- Target: headers, diff, or design under review, and which parts are public/installed vs internal.
- Compatibility promise, one of: `none`, `source` (source-compatible), `ABI-stable` (within a major version), or `plugin-frozen` (plugin ABI frozen); and the platform/toolchain assumptions behind it (one compiler vs many, one standard library vs many).
- Distribution model: header-only, static library, shared library, plugin loaded at runtime, or mixed.
- Versioning mechanism: semver, inline namespaces, symbol versioning, or none.
- Boundary discipline: export/visibility macros and what the library exports by default.
- Downstream consumers: same-repo only, known external binaries, or unknown third parties.

If the target cannot be established, return `Verdict: BLOCK` with one open question; do not guess. When the target is supplied but the promise is unstated, analyze promise-independent findings (boundary-contract violations such as exceptions crossing `extern "C"`, header hygiene, ODR risks) normally, state the promise as `undeclared`, and record promise-dependent classifications as open questions instead of guessing the promise.

## Output Depth

Default to `standard`. `quick` still reports missing required context, blockers, unmitigated HIGH/CRITICAL findings, and target-specific concerns; it only omits non-applicable checklist expansion. `standard` covers the applicable checklist with concise evidence. `exhaustive` enumerates the full checklist only when asked or when the risk surface warrants it. Name the selected depth when the user asks for `quick` or `exhaustive`.

## Workflow

1. Identify the boundary: which declarations are public/installed, which symbols are exported, and what the stated compatibility promise is.
2. Classify each change: API-breaking, ABI-breaking, both, or neither — under the stated promise and toolchain assumptions.
3. Check ODR exposure: inline functions, templates, default arguments, and constants that compile into consumers and silently diverge between library versions.
4. Check exception and `noexcept` contracts at the boundary.
5. Check structural ABI factors: object layout, virtual tables, inheritance changes, member order, and standard-library types in the public interface.
6. Check the versioning and migration mechanism for any break found.
7. Classify findings by severity, map to a verdict, and state the verification each change needs (ABI-diff tooling, symbol diff, recompile tests).

## Decision Rules

The Checklist below is the gating source of truth when these rules overlap; the rules explain rationale.

- When the promise is ABI stability, treat these as ABI breaks: adding/removing/reordering non-static data members; changing member types or class size/alignment; adding, removing, or reordering virtual functions (including adding a first virtual function); adding or changing base classes; changing template arguments of a public type; changing a function's parameter types, return type, constness, ref-qualifier, or calling convention; and any change that alters whether the type is trivial or trivially copyable (a user-declared destructor or copy/move member changes how the type is passed by value on the Itanium ABI).
- When the promise is ABI stability, treat these as safe at the binary level on common ABIs (but verify against the documented promise): adding new non-virtual, non-special member functions; adding static members; adding new exported symbols; and adding entirely new types. Binary-safe additions can still break source compatibility: new overloads can change overload resolution, create ambiguities, or break `&Class::f` address-taking at existing call sites.
- When a function body is inline, a template, or a default argument value, it compiles into the consumer: changing it does not break linking but creates mixed-version behavior and ODR risk. Classify inline semantic drift as its own category — `ODR/mixed-version` — distinct from a binary-layout break, but apply the same break process (version bump or symbol-level separation).
- When `noexcept` appears on a public function, treat it as a one-way contract: adding `noexcept` is usually safe; removing it is an API and behavioral break (callers may have selected move paths or omitted handlers based on it). `noexcept` changes also alter the function type since C++17.
- When standard-library or third-party types appear in public signatures or object layout, the ABI promise inherits their ABI: document the standard-library and dependency versions the promise assumes (e.g. libstdc++ dual-ABI strings, debug-iterator builds).
- When a class is meant to be ABI-stable across feature growth, use pimpl or another compilation firewall; reserve space or use a versioned-struct pattern only with explicit documentation.
- When default arguments are part of a public API, prefer overloads when the value may evolve: default-argument values bake into call sites at compile time, so already-compiled consumers keep the old value while recompiled ones get the new value — a silent mixed-fleet behavior split. Note the tradeoff: the added overload is binary-safe but can change overload resolution at existing call sites (a source-compatibility hazard to check explicitly).
- When a public enum lacks a fixed underlying type, treat enumerator additions as potentially layout-affecting: the underlying type may change size. Require `enum class E : type` or `enum E : type` on every public enum under an ABI promise.
- When a header is public, it must be self-contained (compiles alone), include only what it uses, avoid `using namespace` and macros that leak, and avoid internal headers in its include graph.
- When `extern "C"` boundaries exist, keep them free of C++ types, exceptions (terminate/UB at the boundary), and bool/enum size assumptions; document ownership and lifetime of every pointer crossing the boundary.
- When symbols are exported from a shared library, use explicit export/visibility macros (default-hidden visibility) rather than exporting everything; exported internal symbols become accidental contract.
- When an ABI break is necessary, make it loud: bump the soname/major version, use an inline-namespace rename, or both; never ship a silent layout change under a stable soname.

## Checklist

### Boundary Definition

- The public/installed surface is explicitly identified (headers, export macros, symbol list), and internal headers cannot be reached from public includes.
- The compatibility promise (none/source/ABI-stable/plugin-frozen) and its toolchain assumptions are written down.
- Exported-symbol visibility is explicit; nothing internal is exported by default.

### Layout And Virtual Structure

- No change to data members, their order, types, alignment, or class size on ABI-stable types; no change to whether the type is trivial or trivially copyable (user-declared special members).
- No added, removed, or reordered virtual functions, changed overrides, or changed bases on ABI-stable types.
- Public enums under an ABI promise have a fixed underlying type.
- Standard-library and dependency types in public signatures/layout are documented as part of the ABI assumption.

### Inlined Code And ODR

- Inline functions, templates, constexpr variables, and default arguments in public headers are treated as compiled-into-consumers; semantic changes to them get a version or symbol-level separation.
- One definition per entity across the install: no same-name-different-definition headers, no macros changing declarations between consumers (including NDEBUG-dependent layout).
- Header-only and compiled parts of the library cannot disagree about type definitions or feature macros.

### Contracts At The Boundary

- `noexcept` is applied deliberately and never removed from a published function without a break process.
- Exceptions do not cross `extern "C"` or plugin boundaries; error reporting at those boundaries is by return value or out-parameter with documented ownership.
- Default arguments on published functions are stable or replaced by overloads.

### Versioning And Migration

- Any API or ABI break is paired with its mechanism: soname/major bump, inline-namespace version, symbol versioning, or documented recompile requirement.
- Deprecations precede removals where the promise allows; `[[deprecated]]` markers carry migration hints.
- ABI-affecting changes have verification: an ABI-diff tool run, symbol diff, or documented manual layout analysis.

### Tests

- Compatibility-sensitive fixes have regression evidence: an ABI-diff check in CI, a link test against a previous binary, or a header self-containment/IWYU check, as applicable. If no such fix is in scope, this item is n/a.

## Severity And Verdicts

- `CRITICAL`: a silent ABI break under a stable soname/promise — layout or vtable changes, or signature changes that do not alter the mangled name on the target ABI (return-type changes on ordinary functions, `extern "C"` signatures, and calling-convention changes where the convention is not mangled, as on the Itanium ABI; MSVC encodes the convention in the decorated name, making those loud) — or an ODR violation with divergent definitions. Signature changes that alter the mangled name fail loudly at link/load time and are `HIGH` when they violate the promise.
- `HIGH`: a promise-violating break that is detectable at compile/link time, or a boundary-contract violation that fails at run time: exceptions crossing `extern "C"`, or removed `noexcept` on a published function (on the Itanium ABI a function's own mangled name does not include its exception specification, so ordinary calls from already-compiled callers stay silent; the spec is mangled only where the function type itself is mangled, such as a function type used as a template argument, where removal becomes a loud link-time break).
- `MEDIUM`: undocumented promise assumptions, missing export-macro discipline, header hygiene that leaks internals, missing deprecation step, or missing ABI verification on a risky change.
- `LOW`: clarity and hardening with no current compatibility impact.

Verdicts:

- `BLOCK`: missing required context, any `CRITICAL`, or any unmitigated `HIGH`.
- `CONCERNS`: any unmitigated `MEDIUM`, or remaining `HIGH`/`MEDIUM` findings that each have a compensating control, accepted tradeoff, or bounded reachability.
- `CLEAN`: every applicable checklist item holds; `LOW`-only findings do not block `CLEAN` and are listed as findings. If no compatibility-sensitive fixes are in scope, Tests is n/a and does not block `CLEAN`. For design-stage targets with no headers yet, the best achievable verdict is `CONCERNS` with verification expectations recorded per finding.

## Output Format

```text
Verdict: BLOCK | CONCERNS | CLEAN
Target: <headers, diff, or design>
Compatibility promise: <none | source | ABI-stable | plugin-frozen | undeclared> <toolchain assumptions, when stated>
Distribution: <header-only | static | shared | plugin | mixed>

Findings:
1. <short title>
  Severity: CRITICAL | HIGH | MEDIUM | LOW
  Classification: Confirmed issue | Likely risk | Open question | Accepted tradeoff | Test gap
  Evidence: <file:line, diff hunk, or design sentence>
  Rule: <boundary | layout | odr | contracts | versioning | tests>
  Risk: <which consumers break, at compile, link, or run time>
  Required guard: <design, versioning, or process change>
  Test expectation: <ABI diff, link test, header check, or N/A>

Checklist status:
- Boundary definition: covered | missing | n/a
- Layout and virtual structure: covered | missing | n/a
- Inlined code and ODR: covered | missing | n/a
- Contracts at the boundary: covered | missing | n/a
- Versioning and migration: covered | missing | n/a
- Tests: covered | missing | n/a

Residual risk: <remaining caveats or None>
```

`Rule:` values map to checklist sections as follows: `boundary` -> Boundary Definition; `layout` -> Layout And Virtual Structure; `odr` -> Inlined Code And ODR; `contracts` -> Contracts At The Boundary; `versioning` -> Versioning And Migration; `tests` -> Tests.

When no material issues exist, write exactly `Findings: None` (allowed only with `CLEAN`) and list assumptions under Residual risk. For design-stage targets that earn `CONCERNS` solely because verification cannot exist yet, emit one `Test gap` finding with `Rule: tests` listing the required verification instead of an empty findings list.

Insufficient-context mode: when the target itself cannot be established, emit exactly this reduced template and stop; do not emit promise, distribution, or checklist status with guessed values (an unstated promise with a supplied target follows the undeclared-promise rule in Required Context instead):

```text
Verdict: BLOCK
Target: <headers, diff, or design>

Findings:
1. <missing-context short title>
  Severity: LOW
  Classification: Open question
  Evidence: <which required context is missing>
  Rule: <boundary | layout | odr | contracts | versioning | tests>
  Risk: <why no safe conclusion is possible>
  Required guard: <what context must be supplied>
  Test expectation: N/A
```

## Examples

- Silent layout break: adding a `bool dirty_` member to an exported, ABI-stable class shifts every subsequent member and changes the class size; old binaries read garbage. Fix: move new state behind the pimpl, or bump the major version/inline namespace.
- Inline divergence: a public header's inline `validate()` gains a stricter check; consumers compiled before the change keep the old logic, and mixing objects from both versions violates the ODR. Fix: out-of-line the function in the next major, or version the inline namespace.
- Default-argument drift: changing `connect(timeout = 30s)` to `timeout = 5s` changes behavior of every already-compiled call site only after recompilation, creating mixed-fleet behavior. Fix: add an explicit overload and deprecate the defaulted one.

## Definition Of Done

An API/ABI change is ready only when:

- Every change is classified against the stated promise (API break, ABI break, both, or neither).
- Breaks carry their versioning mechanism and migration path; nothing breaks silently under a stable soname.
- Inlined code, templates, and default arguments with changed semantics are versioned or renamed per the Inlined Code And ODR checklist.
- Boundary contracts (`noexcept`, `extern "C"`, ownership across the boundary) satisfy their checklist section.
- ABI-affecting changes have verification evidence per the Tests checklist item.
