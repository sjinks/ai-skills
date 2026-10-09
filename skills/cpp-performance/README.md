# cpp-performance

> Use when: reviewing, designing, implementing, or debugging C++ performance hot spots involving unnecessary copies, pass-by-value of expensive types, range-for copies, misused std::move, missing noexcept on move/swap/destructor, inefficient container or string operations, missing reserve, STL algorithms on associative containers, std::endl flushing, float-to-double math promotion, oversized enums, integer-to-pointer casts, or redundant string/string_view conversions.

This skill removes avoidable runtime cost without changing observable behavior. It encodes the clang-tidy `performance-*` catalog plus a set of cost-relevant checks from the `modernize-*`, `bugprone-*`, `readability-*`, and `clang-analyzer-*` namespaces, citing the matching check name in each finding.

It helps an assistant:

- trace copies (value parameters, copy-initialized locals, range-for variables, implicit conversions) and choose `const&`, move-in, or a justified copy
- confirm every `std::move`/`std::forward` actually moves and that `const` or a value-category mistake never silently downgrades a move to a copy, including return-move eligibility
- audit move/`swap`/`iter_swap`/destructor exception specifications against their operations; require `noexcept` only for non-throwing operations
- catch inefficient container growth, string building, STL-on-associative-container calls, `std::endl` flushing, math float-promotion, oversized enums, integer-to-pointer casts, and redundant `string`/`string_view` conversions
- weigh hot-path severity using a defined "hot path" rule, cap unverified paths at MEDIUM, and never promote a performance fix over a correctness or lifetime concern (routing those out of scope)
- return `BLOCK`, `CONCERNS`, or `CLEAN` with type-cost inventory, hot-path notes, per-finding checks, test/measurement expectations, residual risk, and a deterministic insufficient-context template

Verdicts apply in order: blocking conditions produce `BLOCK`; other findings or missing applicable checks produce `CONCERNS`; otherwise the package's `CLEAN` criteria apply. Design-stage verification limitations retain `CONCERNS`.

## Files

- [`SKILL.md`](SKILL.md) — operational workflow, decision rules, output contract, and completion gates.
- [`references/copies-moves.md`](references/copies-moves.md) — copy, move, return, and special-member explanations.
- [`references/examples.md`](references/examples.md) — partial examples of common findings.
- [`references/library-costs.md`](references/library-costs.md) — library, layout, and callable cost explanations.
