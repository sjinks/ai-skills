---
name: cpp-const-correctness
description: "Use when: fixing or reviewing clang-tidy misc-const-correctness findings, or deciding whether a local variable, reference, or pointer that is never modified after initialization should be declared const."
argument-hint: "Describe the local variable, file, or diff where a missing const qualifier may need to be added."
user-invocable: true
---

# C++ Const Correctness

Use this skill to resolve clang-tidy `misc-const-correctness` findings: **local variables** (value, reference, and - when enabled - pointer locals) that are never modified after initialization and could therefore be declared `const`. The goal is a fast, correct, mechanical fix that does not introduce a regression or a new tidy warning.

The check enforces [ES.25](https://isocpp.github.io/CppCoreGuidelines/CppCoreGuidelines#es25-declare-an-object-const-or-constexpr-unless-you-want-to-modify-its-value-later-on): declare an object `const` unless you intend to modify it. The analysis is **type-based only** — it flags a local as `const`-able when no expression in scope can mutate it. It analyzes only **local variables**: it does not look at function parameters, data members, or globals.

**UTILITY SKILL.** INVOKES: read-only file access for supplied targets; no other tools or skills. FOR SINGLE OPERATIONS: use to fix a single flagged declaration or sweep a file for missing `const`.

## Scope

- Use this skill for **local variables** only: local value variables (`int i = 42;` → `int const i = 42;`), local references (`int& r = i;` → `int const& r = i;`), and - when `WarnPointersAsValues` is enabled - local pointers that are never reseated (`T* p` → `T* const p`).
- Apply it whenever clang-tidy emits `misc-const-correctness`. The check is most useful when the project gates the `misc-*` group as warnings-as-errors, so a missing `const` on a flagged local fails the build.
- Keep the fix behavior-preserving: adding `const` must not change overload resolution, template instantiation, move eligibility, or API/ABI.

## DO NOT USE FOR:

- **Function parameters of any kind.** `misc-const-correctness` does not analyze parameters (it has no parameter-analysis option); for a never-mutated reference/pointer parameter, deciding `const` is manual review, not this check. Top-level `const` on a by-value parameter is also not part of the function type and is out of scope.
- Marking **member functions** `const` (that is a `readability`/design concern, not `misc-const-correctness`), or `const`-ness of class data members and globals (the check ignores members and globals; non-const globals are a separate `cppcoreguidelines-avoid-non-const-global-variables` concern).
- Suggesting **pointee** `const` (`int* p` → `const int* p`). The check never does this; with `WarnPointersAsValues` it suggests a `const` *pointer* (`int* const p`), not a pointer-to-const.
- Pure performance work (copies vs references) — out of scope: that is runtime-cost work. Const-correctness is about intent and immutability, not cost.
- Lifetime/dangling questions raised when binding a `const&` to a temporary or returned reference — out of scope: that is object-lifetime/ownership review.

## What The Check Flags (and What It Does Not)

`misc-const-correctness` real options (clang-tidy defaults):

- **Values** (`AnalyzeValues`, default on): a never-reassigned local of value type → add top-level `const`. `int i = 42;` becomes `int const i = 42;` (equivalently `const int i = 42;`).
- **References** (`AnalyzeReferences`, default on): a local reference never used to mutate its referent → add `const`. `int& ref = i;` → `int const& ref = i;`. A reference is only flagged when it is not itself used to modify the referent.
- **Pointers** (`WarnPointersAsValues`, default **off**): when enabled, the check flags a local **pointer** that is never reseated and suggests a `const` pointer — `int* p = &i;` → `int* const p = &i;`. It analyzes the pointer *value*, not the pointee; it never suggests pointer-to-const (`const int*`). With the default config (off), local pointers are not flagged at all.

The check analyzes **only local variables**. It does **not** fire on:

- **Function parameters** of any kind (reference, pointer, or value) — there is no parameter-analysis option.
- Class data members, globals, and member functions.
- Templated variables, template functions, or instantiation-dependent variables (different instantiations may differ; the check skips them).
- C code.
- Variables only read but used to create a non-`const` handle that may escape scope (type-based analysis cannot prove immutability there).

Automatic fix-its (`TransformValues`/`TransformReferences`, default on; `TransformPointersAsValues`, default off) apply only to **single declarations** — a comma-grouped declaration (`int a = 1, b = 2;`) must be split first (run `readability-isolate-declaration`) before a fix-it lands.

## Decision Rules

1. **Confirm immutability over the whole scope.** Add `const` only when the variable is never the target of: assignment (`=`, `+=`, `++`, `--`), a non-const member-function call, binding to a non-const reference or non-const pointer, passing by non-const reference/pointer to a function, or being moved-from. If any of these occur after initialization, leave it non-`const` — the check will not flag it, and forcing `const` breaks the build.
2. **Place `const` correctly.**
   - Value: `const T v = …;` (or `T const v`). Pick the style already dominant in the file; both are accepted.
   - Reference: `const T& r = …;`. Never `T& const` (ill-formed for references' top-level).
   - Const pointer (`T* const p`): only when `WarnPointersAsValues` is enabled in config; this makes the *pointer* `const` (not reseatable), not the pointee. Do not add it pre-emptively — it is off by default. The check never suggests pointer-to-const (`const T* p`).
3. **Do not touch function parameters.** The check analyzes only local variables, so a parameter it appears to implicate is out of scope: deciding `const` on a never-mutated reference/pointer parameter is manual review, and top-level `const` on a by-value parameter is not part of the function type and only creates header/source churn.
4. **Split grouped declarations before fixing.** `int x = a, y = b;` cannot receive a fix-it; isolate to `int x = a;` `int y = b;` first, then qualify the ones that are immutable.
5. **Preserve `auto` deduction intent.** `auto x = f();` → `const auto x = f();` when never mutated; for references prefer `const auto&` (this also intersects `performance-for-range-copy`). Ensure adding `const` to `auto` does not silently change a returned-by-value into something unexpected — it does not change the deduced type, only adds the qualifier.
6. **Watch for move eligibility.** A local that is `return`ed and eligible for the implicit move-on-return must **not** be made `const` — `const` blocks the automatic move (`performance-no-automatic-move`). If a variable is returned by value at the end of its scope, prefer leaving it non-`const`; the const-correctness check will not flag a returned local that is moved. When the two checks conflict, the move (performance + correctness) wins.
7. **Verify after applying.** Re-run clang-tidy on the touched files; a correct fix removes the `misc-const-correctness` diagnostic without producing a new one (e.g. `performance-no-automatic-move`, a build error from an actually-mutated variable, or an overload-resolution change). If the project also runs a formatter, re-run its format check after a fix-it lands.

## Project Integration

- When a project gates the `misc-*` group as warnings-as-errors, a missing `const` on a flagged local fails the build, which is why this finding recurs; fix it mechanically rather than suppressing it.
- Member naming/access conventions (e.g. an `m_` member prefix or explicit `this->`) are orthogonal to local-variable `const`: this check targets **locals**, not members, so those conventions do not interact with the fix.
- Confirm the fix with the project's own clang-tidy invocation and formatter check before considering it done; a tidy fix-it must still satisfy the formatter.

## Checklist

- Every flagged local value/reference/pointer that is provably never mutated carries `const`; the qualifier is placed correctly for its category (value, `const&`, `const` pointer when `WarnPointersAsValues` is on).
- No `const` was added to a function parameter, to a member function, to a member/global (out of this check's scope), or to a templated/instantiation-dependent variable.
- Grouped declarations were isolated before a fix-it was applied.
- No returned-by-value local was made `const` in a way that blocks automatic move (`performance-no-automatic-move`); when in conflict, the move wins.
- Adding `const` did not change overload resolution, template behavior, or API/ABI; the build still compiles.
- Re-running clang-tidy shows the `misc-const-correctness` finding cleared and no new diagnostic introduced.

## Severity And Verdicts

`misc-const-correctness` is a low-risk readability/intent check; its findings rarely indicate a latent bug. Severity reflects the cost of leaving it (a build-gate failure where the project treats the check as an error) versus the risk of a wrong fix.

- `HIGH`: a wrong fix that breaks the build (added `const` to an actually-mutated variable) or silently changes behavior (blocking a return move, changing overload resolution).
- `MEDIUM`: a true missing `const` on a flagged local that fails a gating tidy run.
- `LOW`: stylistic placement preference (`const T` vs `T const`) where the file is consistent either way.

Verdicts:

- `BLOCK`: a proposed `const` would break the build or change behavior, or the variable's mutation cannot be confirmed from the supplied context.
- `CONCERNS`: the `const` is correct but intersects another check (e.g. return-move) that should be confirmed, or grouped declarations still need isolation.
- `CLEAN`: every flagged declaration in scope is correctly qualified, the build compiles, and re-running tidy clears the finding with no new one.

## Output Format

```text
Verdict: BLOCK | CONCERNS | CLEAN
Target: <files, diff, or declaration>

Findings:
1. <short title>
  Severity: HIGH | MEDIUM | LOW
  Classification: Confirmed missing const | Wrong/unsafe fix | Out of scope | Open question
  Evidence: <file:line of the declaration and any mutation site>
  Category: value | reference | pointer
  Fix: <the exact const-qualified declaration, or why it must stay non-const>
  Cross-check: <performance-no-automatic-move | none | other>

Checklist status:
- Flagged declarations qualified: covered | missing | n/a
- Out-of-scope cases avoided: covered | missing | n/a
- Grouped declarations isolated: covered | missing | n/a
- Return-move conflicts resolved: covered | missing | n/a
- Build / overload behavior preserved: covered | missing | n/a
- tidy re-run clears finding: covered | missing | n/a

Residual risk: <remaining caveats, or None>
```

When no material issues exist, write exactly `Findings: None` (allowed only with `CLEAN`).

Insufficient-context mode: when the declaration cannot be seen or its mutation over the whole scope cannot be established, emit exactly this reduced template and stop; do not emit checklist status with guessed values:

```text
Verdict: BLOCK
Target: <files, diff, or declaration>

Findings:
1. <missing-context short title>
  Severity: LOW
  Classification: Open question
  Evidence: <which required context is missing>
  Category: value | reference | pointer
  Fix: <what context must be supplied to decide const>
  Cross-check: none
```

## Examples

- Local value: `int total = compute(); use(total);` → `const int total = compute();` (never reassigned). (`misc-const-correctness`, `AnalyzeValues`.)
- Reference: `auto& entry = map.at(key); read(entry);` → `const auto& entry = map.at(key);` when `entry` is not mutated. (`AnalyzeReferences`.)
- Pointer (only when `WarnPointersAsValues` is enabled): `int* p = &node->value; log(*p);` → `int* const p = &node->value;` when `p` is never reseated. The check makes the *pointer* `const`, not the pointee; it never emits `const int* p`.
- Do NOT fix: `std::string build() { std::string s; append(s); return s; }` — `s` is mutated then returned; not flagged, and `const` would block the return move.
- Out of scope: `void send(Buffer& b) { write(b.data()); }` — `b` is a parameter; the check does not analyze parameters, so any `const` decision here is manual review, not a `misc-const-correctness` fix.
- Out of scope: `void f(int n)` — value parameter; the check ignores top-level `const` on value parameters.

## Definition Of Done

A const-correctness change is ready only when:

- Every `misc-const-correctness`-flagged local in the target is `const`-qualified or has a stated reason it must stay mutable.
- No `const` was added outside the check's scope (function parameters, members, globals, templated variables) or in a way that blocks a return move or alters overload resolution.
- Grouped declarations were isolated before fix-its applied.
- The build compiles and re-running clang-tidy clears the finding without producing a new diagnostic.
