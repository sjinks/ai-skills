# cpp-struct-layout

> Use when: reviewing, designing, or shrinking the in-memory layout of a C/C++ class, struct, or union to remove padding waste by reordering data members from largest to smallest alignment, or when sizeof seems larger than the sum of its members.

This skill audits a `class`, `struct`, or `union` for **padding waste** and proposes a behavior-preserving member ordering — largest alignment first — that minimizes `sizeof` and improves cache density. It is the deep, dedicated treatment of the struct padding waste that a brief `clang-analyzer-optin.performance.Padding` lint item only flags.

It helps an assistant:

- compute the current layout (per-member offsets, internal and tail padding, `sizeof`/`alignof`) under stated platform/type-size assumptions, and the proposed reordered layout, so a reorder is only suggested when it strictly shrinks the type
- order members by descending alignment and cluster same-alignment members, accounting for the vptr, bitfields, `alignas`, `#pragma pack`, and `[[no_unique_address]]`
- withhold the reorder for frozen layouts: ABI-exported types, raw-byte serialization, C interop, and external wire/file/hardware formats
- catch the unsafe-reorder traps: changed member-init order (`-Wreorder`), positional aggregate/designated-init mismatches, and loss of standard-layout (`offsetof` validity, C-interop)
- return `BLOCK`, `CONCERNS`, or `CLEAN` with before/after sizes, safety classification, the reordered declarations, a `static_assert` to lock the gain, and a deterministic insufficient-context template

## Files

- [`SKILL.md`](SKILL.md) — the full skill definition.
