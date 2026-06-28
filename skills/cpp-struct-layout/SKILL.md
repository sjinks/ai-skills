---
name: cpp-struct-layout
description: "Use when: reviewing, designing, or shrinking the in-memory layout of a C/C++ class, struct, or union to remove padding waste by reordering data members from largest to smallest alignment, or when sizeof seems larger than the sum of its members."
argument-hint: "Describe the class/struct/union (or file/diff) whose member layout, sizeof, padding, or alignment you want audited."
user-invocable: true
---

# C++ Struct Layout

Use this skill to audit a `class`, `struct`, or `union` for **padding waste** and propose a member ordering that minimizes `sizeof` without changing behavior. The canonical fix is to order non-static data members from **largest alignment to smallest** so the compiler inserts fewer alignment-padding bytes. Placing a small member such as `std::uint16_t` *between* two larger, more-strictly-aligned members forces internal padding to re-align the member that follows it; moving the small member to the end lets it share the struct's trailing slot instead. Whether that actually shrinks `sizeof` depends on the exact widths, so the rule is always: **compute the before/after layout, then reorder** (see How Padding Arises for a worked example).

The goal is a **behavior-preserving** layout change: same members, same types, same observable semantics, smaller (or equal) footprint and better cache density. Reordering members is the cheapest such change; this skill also flags when reordering is *unsafe* (ABI, wire formats, C interop, init-order dependencies).

**UTILITY SKILL.** INVOKES: read-only file access for supplied targets; no other tools or skills. FOR SINGLE OPERATIONS: use to reorder one type's members, audit a header for padding, or judge whether a proposed layout change is safe.

This skill is the deep, dedicated treatment of struct/union padding waste — the kind a brief `clang-analyzer-optin.performance.Padding` lint item only flags; cite that check in findings so the reader can enable it (`-Xclang -analyzer-checker=optin.performance.Padding`, or via `clang-tidy`).

## Scope

- Use this skill for: non-static data member **ordering** to reduce internal and tail padding; identifying which member's alignment forces padding; estimating `sizeof`/`alignof`/`offsetof` before and after a reorder; deciding when `alignas`, `[[no_unique_address]]`, or splitting hot/cold fields is warranted; spotting oversized members (e.g. an `enum` with a needlessly wide underlying type, an `int` where `std::uint8_t` suffices) that inflate alignment.
- Apply it to: plain data aggregates, value types stored in large arrays/containers (where per-element padding multiplies), per-connection/per-request/per-message structs in this server (footprint × concurrency), and any type the user reports as "bigger than expected".
- Keep the change behavior-preserving: same set of members and types, same access semantics. Only the **declaration order** (and occasionally alignment qualifiers) changes.

## DO NOT USE FOR:

- **Reordering members of a type with a frozen layout.** Types that cross an ABI boundary (exported in a shared library / public header consumed by separately-compiled code), are serialized by raw `memcpy`/`fwrite`/`send` of the struct bytes, overlay a wire/file/hardware format, or are shared with C code via a matching declaration — their member order is part of the contract. Flag the waste, but do **not** reorder without an explicit ABI/format break decision.
- Algorithmic memory reduction, allocator/arena choice, container selection, or replacing a type with a smaller representation (different members) — that is design work, not a layout reorder; out of scope: copy/allocation-cost work.
- False-sharing / cache-line padding for concurrently-written members (`alignas(std::hardware_destructive_interference_size)`, padding to separate hot atomics) — out of scope: that is concurrency/contention tuning. This skill only notes when packing *increases* false-sharing risk.
- Lifetime/dangling consequences of any change — out of scope: that is object-lifetime review.

## Required Context

Collect or infer before judging:

- **Target**: the full type definition (all non-static data members, in order, with types), plus any base classes and virtual functions (a vptr adds a pointer-sized, pointer-aligned slot, usually first).
- **Member sizes/alignments**: `sizeof`/`alignof` of each member type. For standard types assume the platform's common values (`std::string` is 32 bytes / 8-byte aligned on libstdc++ and MSVC but **24 bytes on libc++** (x86-64), so confirm the standard library before computing; pointers and `std::size_t` 8/8; `double` 8/8; `int`/`float` 4/4; `short`/`char16_t` 2/2; `bool`/`char` 1/1) but **state the assumption** and confirm if the target platform differs (32-bit, MSVC, packed builds).
- **Layout constraints**: is the type ABI-exposed, serialized by raw bytes, a C-interop struct, an aggregate initialized positionally with designated/braced init, or does it have non-trivial member-init-order dependencies?
- **Usage shape**: is the type stored in large arrays/containers or allocated per-connection/request (so padding multiplies), or a one-off singleton (where layout barely matters)?
- **Bitfields / `alignas` / `#pragma pack` / `[[no_unique_address]]`**: these override the default rules and must be accounted for.

If the full member list cannot be seen, or the platform's type sizes cannot be established, return `Verdict: BLOCK` with one open question. Do not guess a type's `sizeof` when the answer drives the verdict.

## How Padding Arises (the rules)

1. Each member is placed at an offset that is a multiple of its **alignment**; the compiler inserts **internal padding** before a member when the running offset is not yet aligned.
2. The struct's own alignment is the **maximum** alignment of its members; `sizeof` is rounded up to a multiple of that alignment, producing **tail padding**.
3. Members are laid out in **declaration order**: the standard guarantees increasing addresses for non-static data members declared in the same access-control section ([class.mem]), and the compiler may **not** reorder them, so order is the programmer's lever. (Across *different* access sections the relative order is unspecified, which is why rule 7 keeps data members in one section.)
4. Therefore: ordering members by **descending alignment** (8-byte, then 4-byte, then 2-byte, then 1-byte) minimizes internal padding, and small trailing members are absorbed by tail padding that would exist anyway.

Worked example (x86-64 LP64, `alignof(double)==8`, `alignof(int)==4`, `alignof(char)==1`):

```cpp
struct Bad  { char a; double x; char b; int n; char c; };
// a:0 | 7 pad | x:8..15 | b:16 | 3 pad | n:20..23 | c:24 | 7 tail pad => sizeof 32
struct Good { double x; int n; char a; char b; char c; };
// x:0..7 | n:8..11 | a:12 | b:13 | c:14 | 1 tail pad => sizeof 16
```

Here the three `char`s, scattered between the `double` and `int`, each forced a separate gap (17 wasted bytes total); clustered after the wide members they share a single tail slot, halving `sizeof`. The win is largest with **mixed-width members interleaved with wide ones**.

Note the opposite case: two `std::string` members (32 bytes, align 8) around a `std::uint16_t` — moving the `uint16_t` to the tail leaves `sizeof` unchanged (72 → 72), because tail padding still rounds up to alignment 8 and there is no second small member to share the slot. **Always compute the before/after `sizeof`; do not assume a reorder shrinks the type.** A reorder that does not change `sizeof` is a no-op and should be dropped (or kept only if it improves readability/grouping).

## Decision Rules

1. **Compute before deciding.** Lay out the current members with offsets and total `sizeof`; then lay out the descending-alignment ordering and compute its `sizeof`. Only propose the reorder if it strictly reduces `sizeof` (or equalizes it while improving grouping). State both numbers.
2. **Order by descending alignment, then group same-alignment members.** Within an alignment class, keep semantically related members adjacent and preserve original relative order where it is free to do so (reduces diff noise and keeps init order intuitive).
3. **Respect frozen layouts.** If the type is ABI-exposed, serialized by raw bytes, C-interop, or overlays an external format, do **not** silently reorder. Report the waste and the *would-be* layout, and require an explicit break decision. Cite which constraint applies.
4. **Account for the vptr.** A polymorphic class has a vtable pointer (pointer-sized, pointer-aligned), conventionally first; reordering data members cannot move it. Compute layout after the vptr slot.
5. **Preserve member-initializer order.** Members are initialized in declaration order regardless of the mem-init-list order. Reordering changes initialization order; if any member's constructor reads another member, or the init list relied on the old order, this can change behavior or trip `-Wreorder`. Verify no init-order dependency before reordering.
6. **Preserve aggregate / designated init.** For aggregates initialized with braced lists `T{a, b, c}`, reordering members silently re-maps positional initializers to the wrong fields — a correctness bug. Reorder only if all initializations are designated (`.a = …`) or named, or update every call site. C++20 designated initializers must also appear in declaration order, so a reorder may force call-site edits.
7. **Don't break standard-layout / trivial properties.** Reordering within a single access-control section preserves standard-layout; splitting members across `public:`/`private:` sections (or adding one) can make a type non-standard-layout and break `offsetof`, `memcpy`-ability, and C compatibility. Keep all data members in one access section if the type must stay standard-layout.
8. **Prefer ordering over `#pragma pack`.** Packing removes padding but creates **misaligned members**, which are slower (or UB to take addresses of on some targets) — never reach for `#pragma pack` purely to save space; reorder first. Use `alignas` only to *increase* alignment for a deliberate reason (SIMD, cache line), not to shrink.
9. **Consider shrinking oversized members.** If a member's wide type forces the struct's alignment (e.g. a `std::size_t` flag that only needs `std::uint8_t`, or an `enum` defaulting to `int`), a narrower type both saves the member's bytes and may lower the struct alignment — but only when the narrower range is provably sufficient. This crosses into representation change; flag it, don't assume it.
10. **`[[no_unique_address]]` for empty members.** An empty member (stateless comparator, allocator, tag) costs ≥1 byte plus alignment; `[[no_unique_address]]` (C++20) lets it overlap, often saving a full slot — on Itanium-ABI toolchains (GCC/Clang). MSVC ignores the standard attribute for ABI compatibility and needs `[[msvc::no_unique_address]]`, so the saving does not occur on MSVC without it. Suggest it for empty non-static members, noting the MSVC caveat.
11. **Verify after applying.** Confirm the new `sizeof`/`offsetof`/`static_assert` and that the build compiles with no `-Wreorder` / aggregate-init mismatch; ideally add a `static_assert(sizeof(T) == N)` to lock the gain.

## Tools To Confirm Layout

Recommend (do not run; this is a read-only skill) one of:

- `clang -Xclang -fdump-record-layouts -emit-llvm -c file.cpp` (or `-fsyntax-only`): prints exact offsets, sizes, and padding per record — the authoritative answer.
- `clang -Wpadded` / `gcc -Wpadded`: warns at each inserted padding byte (noisy but precise).
- `pahole <object-with-debuginfo>`: shows holes and suggests packing for compiled types.
- clang static analyzer `optin.performance.Padding` (in `clang-tidy`, enable it as `clang-analyzer-optin.performance.Padding`; configurable `AllowedPad`): flags types wasting more than a threshold of padding.
- In code: `static_assert(sizeof(T) == N); static_assert(offsetof(T, m) == K);` to pin the result (note `offsetof` is only well-defined for standard-layout types).

## Checklist

- Current layout computed: per-member offsets, internal padding, tail padding, total `sizeof` and `alignof`, with the platform/type-size assumptions stated.
- Proposed layout computed the same way; the reorder **strictly reduces** `sizeof` (or is declared a no-op and dropped).
- Members ordered by descending alignment; same-alignment members grouped and original relative order preserved where free.
- Frozen-layout constraints checked: ABI export, raw-byte serialization, C interop, external wire/file/hardware format — reorder withheld (or break explicitly approved) if any apply.
- vptr accounted for; bitfields, `alignas`, `#pragma pack`, `[[no_unique_address]]` accounted for.
- Member-init order change reviewed for dependencies and `-Wreorder`; aggregate/designated init call sites checked and updated if needed.
- standard-layout / trivial properties and `offsetof`/`memcpy` usage preserved (single access section kept if required).
- No `#pragma pack` introduced purely to save space; `alignas` only used to increase alignment deliberately.
- Result locked with `static_assert(sizeof…)` where practical; build compiles with no new warning.

## Severity And Verdicts

Padding waste is a low-correctness-risk efficiency issue; severity reflects the multiplied cost and the risk of an unsafe reorder. `CRITICAL` is reserved for a change that silently corrupts a contract other code depends on.

- `CRITICAL`: a layout change that silently breaks a frozen contract other code relies on — an exported ABI, raw-byte serialization, a wire/file/hardware format, or a matching C declaration — shipping data corruption or interop breakage the compiler does not catch.
- `HIGH`: a reorder that breaks behavior within the translation unit — re-mapped positional aggregate init, or changed member-init order with a dependency (a `-Wreorder`-class hazard).
- `MEDIUM`: real, multiplied padding waste (type stored in large arrays/containers or per-connection/request) that a safe reorder removes; or an oversized member inflating alignment.
- `LOW`: padding in a singleton / rarely-instantiated type where footprint barely matters, or a reorder that does not actually change `sizeof`.

Verdicts:

- `BLOCK`: missing required context (the full member list or the platform type sizes cannot be seen), or any `CRITICAL` (a proposed reorder would break a frozen layout) or unmitigated `HIGH` (positional-init or member-init-order break) that is not approved.
- `CONCERNS`: the reorder is correct and saves space but intersects another constraint to confirm (init order, designated-init call sites, standard-layout requirement) before applying.
- `CLEAN`: layout is already optimal for its alignment classes, or the proposed reorder strictly shrinks `sizeof`, is provably safe, and is locked with a `static_assert`.

## Output Format

```text
Verdict: BLOCK | CONCERNS | CLEAN
Target: <type name, file:line, or diff>
Assumptions: <platform / type sizes used, e.g. libstdc++ x86-64, sizeof(std::string)=32>

Findings:
1. <short title>
  Severity: CRITICAL | HIGH | MEDIUM | LOW
  Classification: Padding waste | Unsafe reorder | Frozen layout | Oversized member | Open question
  Current: sizeof=<N>, alignof=<A> — <offset/padding sketch>
  Proposed: sizeof=<M> — <new member order>
  Safety: <reorderable | frozen: ABI/serialized/C-interop/format | init-order/aggregate caveat>
  Fix: <the reordered member declarations, or why it must not change>
  Cross-check: <clang-analyzer optin.performance.Padding | -Wreorder | copy/allocation-cost | none>

Checklist status:
- Current layout computed: covered | missing | n/a
- Proposed layout strictly smaller: covered | missing | n/a
- Frozen-layout constraints checked: covered | missing | n/a
- Init-order / aggregate-init reviewed: covered | missing | n/a
- standard-layout / offsetof preserved: covered | missing | n/a
- Result locked with static_assert: covered | missing | n/a

Residual risk: <remaining caveats, or None>
```

When no material issues exist, write exactly `Findings: None` (allowed only with `CLEAN`).

Insufficient-context mode: when the full member list cannot be seen or the platform's type sizes cannot be established, emit exactly this reduced template and stop; do not emit a computed layout or checklist status with guessed values:

```text
Verdict: BLOCK
Target: <type name, file:line, or diff>

Findings:
1. <missing-context short title>
  Severity: LOW
  Classification: Open question
  Current: unknown — <which member types or sizes are unseen>
  Proposed: N/A
  Safety: unknown
  Fix: <what context must be supplied to compute the layout>
  Cross-check: none
```

## Examples

- Interleaved widths: `struct S { bool a; double x; bool b; double y; bool c; };` → 40 bytes; reorder to `{ double x; double y; bool a; bool b; bool c; };` → 24 bytes (three `bool`s share one 8-byte tail slot). (`optin.performance.Padding`.)
- Pointer + small + pointer: `{ void* p; std::uint8_t flag; void* q; }` (24 bytes, 7 pad after `flag`) → `{ void* p; void* q; std::uint8_t flag; }` (24 bytes — same `sizeof`, but the gap moves to free tail; report it as a no-op unless more small members can join `flag`).
- Oversized alignment driver: `{ std::size_t kind; /* values 0..3 */ std::uint32_t count; }` is 16 bytes (the 8-byte `size_t` forces 8-byte alignment, so `count` leaves 4 tail-pad bytes). Narrow `kind` to `std::uint8_t` and reorder to `{ std::uint32_t count; std::uint8_t kind; }` → 8 bytes (alignment drops to 4, saving 8 bytes). This is a representation change — flag it, confirm the `0..3` range is permanent, don't assume. Contrast `{ std::size_t kind; char* p; }`: narrowing `kind` saves **0** bytes there, because the 8-byte pointer still forces 8-byte alignment and a 16-byte minimum — always compute before claiming a saving.
- Frozen layout — do NOT reorder: a `struct` `memcpy`'d onto a socket or matching a C header. Report the waste and the would-be order, require an explicit format-break decision.
- Empty member: `struct Holder { Compare cmp; /* empty */ std::vector<int> data; };` → `[[no_unique_address]] Compare cmp;` to reclaim the slot (GCC/Clang; MSVC needs `[[msvc::no_unique_address]]`).

## Definition Of Done

A layout change is ready only when:

- The current and proposed layouts are both computed (offsets, padding, `sizeof`, `alignof`) under stated platform assumptions, and the proposal strictly reduces `sizeof`.
- No frozen-layout contract (ABI, raw-byte serialization, C interop, external format) is broken without an explicit, recorded decision.
- Member-init order and aggregate/designated-init call sites were reviewed; no `-Wreorder` or positional-init mismatch is introduced.
- standard-layout / `offsetof` / `memcpy` usage is preserved where required.
- The result is locked with a `static_assert(sizeof(T) == N)` where practical, and the build compiles with no new warning.
