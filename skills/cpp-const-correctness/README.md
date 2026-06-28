# cpp-const-correctness

> Use when: fixing or reviewing clang-tidy misc-const-correctness findings, or deciding whether a local variable, reference, or pointer that is never modified after initialization should be declared const.

This skill resolves `misc-const-correctness` findings, which flag **local variables** (value, reference, and — when enabled — pointer locals) that are never modified and could be declared `const`. The check analyzes only locals, not function parameters, members, or globals.

It helps an assistant:

- decide when a local value, reference, or pointer is provably immutable and should be `const`-qualified
- place `const` correctly per category (`const T`, `const T&`, and `T* const` only when `WarnPointersAsValues` is enabled — the check never suggests pointer-to-const) and split grouped declarations before a fix-it can land
- avoid out-of-scope and unsafe fixes: function parameters (the check ignores them), member functions, members/globals, templated variables, and `const` that blocks a return move (`performance-no-automatic-move`)
- verify the fix by re-running clang-tidy so the finding clears without introducing a new diagnostic or build break
- return `BLOCK`, `CONCERNS`, or `CLEAN` with per-declaration findings, checklist status, cross-check notes, and a deterministic insufficient-context template

## Files

- [`SKILL.md`](SKILL.md) — the full skill definition.
