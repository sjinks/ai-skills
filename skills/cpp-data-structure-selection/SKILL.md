---
name: cpp-data-structure-selection
description: "Use when: choosing or replacing the C++ container/data structure behind a lookup, membership test, dedup, ordering, or accumulation, when a loop scans a collection that grows with input (linear scan, nested scan, repeated find), or when deciding between linear scan, hash map/set, sorted vector, balanced tree, or a small fixed table — including the crossover-size and measure-first reasoning."
argument-hint: "Describe the access pattern (lookup/insert/iterate/dedup/order), the element type, the expected and worst-case element count, and any ordering/stability/allocation constraints."
user-invocable: true
---

# C++ Data Structure Selection

Use this skill to pick the container behind an operation so its **work scales correctly with input size**, and to decide whether an existing structure should change. The canonical fix is replacing a per-element linear scan that runs once per element — an O(n²) shape — with a structure that makes the inner step O(1) or O(log n): a hash map/set, a sorted vector with binary search, or a balanced tree. The opposite is also a finding: a heavyweight node-based container used for a handful of elements where a flat array or linear scan is faster and lighter.

The goal is a **behavior-preserving** change: same elements, same observable results and ordering guarantees, lower asymptotic or constant cost. This is design work — choosing the representation — not a local copy/move tweak.

**UTILITY SKILL.** INVOKES: read-only file access for supplied targets; no other tools or skills. FOR SINGLE OPERATIONS: use to judge one hot loop, one container choice, or one "should this be a map?" question.

This skill owns the algorithmic and data-structure question of *which structure* a collection should be. It is distinct from local source-level cost review (how a single value is copied, moved, or passed) and from in-memory layout review (how one type's members are ordered to shrink its footprint). When the finding is about which container makes an operation scale, it belongs here; when it is about copy/move/allocation cost of an already-chosen structure, or member padding of one type, it does not.

## Scope

- Use this skill for: a loop whose inner step scans a collection that grows with input (nested `find`/`find_if`/`any_of`/`count`, dedup by re-scanning the output, "is this already in the list" checks); choosing between **linear scan over a contiguous array**, **hash map/set** (`unordered_map`/`unordered_set`, `boost::unordered_flat_map`), **sorted `std::vector` + `std::lower_bound`/`std::ranges::binary_search`**, **balanced tree** (`std::map`/`std::set`), and a **small fixed lookup table**; deciding whether an associative container is worth its per-node allocation and pointer-chasing versus a flat structure; sizing the crossover point where one structure overtakes another.
- Apply it to: per-request/per-connection/per-message code in a server (cost multiplies by concurrency and request rate), inner loops over caller-controlled or unbounded input, and any structure the user reports as "slow as N grows."
- Keep the change behavior-preserving: same logical contents and the same ordering/iteration/stability guarantees the callers actually depend on. Only the **representation** changes.

## DO NOT USE FOR:

- **Local source-level cost with the structure unchanged** — unnecessary copies, missing `reserve` on an already-correct container, pass-by-value, move-vs-copy, redundant conversions. That is copy/move/allocation cost review, not container selection.
- **Shrinking one type's footprint by reordering members** (padding) without changing the container. That is in-memory layout review, not container selection.
- **Concurrency/contention** of a shared structure — lock granularity, false sharing, lock-free choice, sharding for parallelism. That is concurrency review; this skill assumes single-threaded access unless the input says otherwise.
- **Lifetime/dangling** consequences of swapping a container (iterator/reference invalidation differs between `vector`, `unordered_map`, and `map`; pointers into a `vector` die on reallocation). Name the risk here, but the invalidation judgment itself is object-lifetime review.
- **I/O batching, caching/memoization strategy, query/index design in a database, or system-level throughput** that is not an in-process container choice.

## Required Context

Collect or infer before judging. Return `Verdict: BLOCK` with one open question when the **dominant access pattern** cannot be established **or** when **all** size information is unknown — do not guess the element count or the access mix. A missing worst-case N, element cost, or constraint when the other drivers are known does not block; it caps confidence and is noted under Residual risk.

- **Access pattern**: which operations run, and how often relative to each other — lookup by key, membership test, insert, erase, iterate-in-order, iterate-any-order, dedup, find-min/max, range query. Name the dominant one.
- **Sizes**: expected (typical) element count **and** worst-case/adversarial count. The crossover between structures depends on N; a structure that is correct at N=10 may be the wrong choice at N=10 000. If only one is known, state which and cap confidence accordingly.
- **Element cost**: is comparison/hashing cheap (integers, small enums) or expensive (case-insensitive string compare, deep equality)? Expensive comparisons change the crossover and may favor hashing or precomputed keys.
- **Ordering / stability constraints**: do callers depend on insertion order, sorted order, stable iteration, stable references/pointers across inserts, or duplicate keys (multimap semantics)? These are correctness constraints, not preferences, and they eliminate candidates.
- **Allocation shape**: is this on a hot path where per-node heap allocation (node-based `map`/`set`/`list`) matters, or is the structure built once and reused? Is the structure reused across iterations (so capacity can be retained)?
- **Existing benchmark/profile**: any measurement that names this structure as hot, or its absence (then the hot-path claim is structural, not measured — see Severity).

## Decision Rules

Work the rules in order. Each names the operation it governs.

### 1. Name the asymptotic shape first

- Count loop nesting where the inner loop's trip count grows with the same N as the outer: that is **O(n²)** (or worse) and is the primary trigger. A single pass with an O(1)/O(log n) inner step is fine and usually needs no change.
- A linear scan that runs **once total** (one lookup, one pass) is O(n) and is rarely worth replacing — the structure that supports it (a plain `vector`) is often already optimal. Do not "upgrade" an O(n) one-shot scan to a hash map; you pay build cost for no asymptotic gain.

### 2. Match the structure to the dominant operation

- **Membership / lookup by key, order does not matter** → hash set/map (`unordered_set`/`unordered_map`, or an open-addressing `boost::unordered_flat_*` for better cache behavior). Average O(1); worst case O(n) on pathological hashing — note adversarial input if keys are attacker-controlled. Caveat: a flat (open-addressing) hash map invalidates references and pointers to elements on rehash, whereas `std::unordered_map` keeps element references/pointers stable across rehash; keep `std::unordered_map` when callers hold element pointers across inserts.
- **Lookup by key, sorted iteration or range queries needed** → balanced tree (`std::map`/`std::set`), O(log n), or a **sorted `vector` + binary search** when the set is built once then queried many times (better cache density, no per-node allocation, but O(n) inserts).
- **Dedup / "seen already" while building output** → a side hash set of keys, turning the O(n²) re-scan into O(n) average; keep the output `vector` for order if callers depend on it.
- **Iterate in insertion order, occasional lookup, small N** → keep a flat `vector`; add a parallel index only if lookups dominate.
- **Find-min / find-max repeatedly with inserts** → a heap (`std::priority_queue`); a sorted container if you also need ordered iteration.
- **Accumulate / group-by (count, sum, or bucket per key)** → a hash map from key to accumulator when keys are sparse or unbounded; a flat array indexed by key when keys are a small dense integer/enum range (an array bucket beats a hash map there). Re-scanning the input once per distinct key to total it is the O(n²) anti-pattern this replaces.

### 3. Respect the crossover — small N favors the flat scan

- For small N (rule of thumb: up to a few dozen elements of a cheaply-compared type), a **linear scan over a contiguous `vector`** usually beats a hash map or tree: no hashing, no allocation, no pointer-chasing, and the whole range fits in cache. The asymptotically "better" structure can be slower below its crossover point.
- Therefore do not replace a small, bounded linear scan with a hash/tree purely on Big-O grounds. Replace it only when N is unbounded or large, **or** when measurement shows the scan is hot. State the assumed crossover and the N you expect.

### 4. Preserve ordering, stability, and duplicate semantics

- If callers rely on insertion order, a plain `unordered_*`/`map` reorders iteration — preserve order with a `vector` (optionally plus an index) or an insertion-ordered map. This is a correctness constraint; violating it is a behavior change, not a perf win.
- If code stores raw pointers/iterators into the container across mutations, the invalidation rules differ: a `vector` reallocation invalidates iterators, references, and pointers; an `std::unordered_*` rehash invalidates iterators only (element references and pointers survive); `std::map`/`std::set` insert/erase invalidates only iterators/references to an erased node. Name the relevant difference; the lifetime judgment itself is object-lifetime review.
- If duplicate keys are meaningful, only a multi-container or a `vector` of pairs preserves them; a `set`/`map` silently collapses them.

### 5. Account for build cost and reuse

- A structure built fresh every iteration pays its construction (hashing, allocation) every time; if it is queried only a few times before being discarded, the build can cost more than the linear scans it replaces. Favor structures that can be **reserved once and reused** (cleared, capacity retained) on hot paths rather than reconstructed per iteration.

### 6. Cross-cutting safety constraint

- A data-structure change is valid only when it preserves observable results, the ordering/stability/duplicate guarantees callers depend on, exception guarantees, and public API/ABI. If the structure is part of an exported type's layout or a serialized format, treat the change as an ABI/format break and route it to a versioning decision rather than asserting a free swap.

## Checklist

### Asymptotic shape

- The dominant operation and its frequency are named; loop nesting over the same growing N is identified as O(n²) (or worse) where present.
- One-shot O(n) scans are left alone unless measurement says otherwise (no needless "upgrade").

### Structure choice

- The chosen structure matches the dominant operation (membership → hash; ordered/range → tree or sorted vector; dedup → side set + ordered output; min/max → heap).
- Expensive comparisons/hashing are accounted for; precomputed or normalized keys are considered when comparison is costly.

### Crossover and constants

- Expected and worst-case N are stated; the crossover point is named so small-N cases keep the flat scan and large/unbounded-N cases get the better structure.
- Build-and-discard cost is weighed against reuse; hot-path structures are reservable and reusable.

### Behavior preservation

- Insertion order, sorted order, iteration stability, reference/iterator stability, and duplicate-key semantics callers depend on are preserved or the change is flagged as behavioral.
- Iterator/reference invalidation differences are named and the lifetime question routed to object-lifetime review.
- ABI/serialized-format exposure is checked; a layout-or-format change is routed to a versioning decision.

### Measurement

- Hot-path changes carry a benchmark or profile, or a microbenchmark across the expected N range that shows the new structure wins at the chosen crossover. A swap justified only by Big-O at small N is marked a measurement gap, not a confirmed win.

## Severity And Verdicts

Severity reflects expected impact at the realistic N and call frequency, not just the presence of a scan.

- `CRITICAL`: an O(n²)-or-worse shape on a hot or per-request path where N is unbounded or attacker-controlled (e.g. dedup by re-scan over caller-supplied list elements that grows without limit) — a denial-of-service or latency-cliff risk.
- `HIGH`: a clear superlinear shape on a frequently executed path with realistically large N, or a node-based container on a hot allocation path where a flat structure is both faster and lighter.
- `MEDIUM`: a real but bounded superlinear shape (N capped at a modest limit), or a latent choice that future scale will amplify; also a correct-but-suboptimal structure whose win is unmeasured.
- `LOW`: a structure choice with negligible impact at the actual N (small, bounded, cold) — flag for consistency, not as a blocker. The sole exception is the missing-required-context finding, which uses `LOW` severity but still yields `Verdict: BLOCK`; its severity reflects the open question, not a blocking gate.

Verdicts:

- `BLOCK`: either a **context gap** (the dominant access pattern is unknown, or all size information is unknown) — emit the reduced insufficient-context template with `Classification: Open question` — **or** a **finding-driven** block (any `CRITICAL`, or any unmitigated `HIGH`) — emit the full template. The verdict label is shared; the Classification and template distinguish the two.
- `CONCERNS`: remaining `HIGH`/`MEDIUM` findings each have a compensating justification, a stated bound, or a recorded measurement gap.
- `CLEAN`: every applicable checklist item holds and hot-path changes carry a benchmark across the expected N range. For design-stage targets with no benchmark yet, the best achievable verdict is `CONCERNS` with the measurement expectation recorded.

A data-structure finding must never be promoted over a correctness or lifetime concern: if the faster structure changes ordering callers rely on, collapses duplicates, or invalidates retained references, downgrade or withdraw the finding and route the question to object-lifetime or concurrency review as appropriate.

## Output Format

```text
Verdict: BLOCK | CONCERNS | CLEAN
Target: <files, function, loop, or container in scope>
Access pattern: <dominant operation(s) and frequency>
Sizes: <expected N | worst-case N | unknown>
Constraints: <ordering | stability | duplicates | reference-stability | ABI/format, or None>

Findings:
1. <short title>
  Severity: CRITICAL | HIGH | MEDIUM | LOW
  Classification: Confirmed hot-path | Likely hot-path (structural) | Crossover-dependent | Open question | Accepted tradeoff | Measurement gap
  Evidence: <file:line, loop nesting, or design sentence>
  Shape: <current asymptotic cost, e.g. O(n^2) nested iequals scan>
  Rule: <asymptotic-shape | structure-choice | crossover | behavior-preservation | measurement>
  Recommended structure: <hash set/map | sorted vector + binary search | tree | flat vector | heap | side index>, and why it fits the dominant operation
  Crossover note: <N above which the change wins; or "always" / "N too small — keep flat scan">
  Behavior risk: <ordering/stability/duplicate/invalidation impact, or None — route lifetime questions to object-lifetime review>
  Test expectation: <benchmark across N, profile, regression test for preserved order, or N/A>

Checklist status:
- Asymptotic shape: covered | missing | n/a
- Structure choice: covered | missing | n/a
- Crossover and constants: covered | missing | n/a
- Behavior preservation: covered | missing | n/a
- Measurement: covered | missing | n/a

Residual risk: <remaining caveats, deferred lifetime/concurrency questions, or None>
```

`Rule:` values map to Decision Rules and Checklist sections as follows: `asymptotic-shape` -> Asymptotic shape (Decision Rule 1); `structure-choice` -> Structure choice (Decision Rule 2); `crossover` -> Crossover and constants (Decision Rules 3 and 5); `behavior-preservation` -> Behavior preservation (Decision Rules 4 and 6, including ordering/stability/duplicates and the ABI/format safety constraint); `measurement` -> Measurement (no numbered Decision Rule; it maps to the Measurement checklist section and the measurement-gap severity guidance). A pure missing-context finding uses `Rule: required-context`, which maps to no Decision Rule.

When no material issues exist, write exactly `Findings: None` (allowed only with `CLEAN`) and list assumptions under Residual risk. For design-stage targets that earn `CONCERNS` solely because measurement cannot exist yet, emit one `Measurement gap` finding with `Rule: measurement` listing the required evidence instead of an empty findings list.

Insufficient-context mode: when the dominant access pattern cannot be established, or all size information is unknown, emit exactly this reduced template and stop; do not emit a structure recommendation or checklist with guessed values:

```text
Verdict: BLOCK
Target: <files, function, loop, or container in scope>

Findings:
1. <missing-context short title>
  Severity: LOW
  Classification: Open question
  Evidence: <which required context is missing — access pattern or all sizes>
  Shape: <unknown — why no safe conclusion is possible>
  Rule: required-context
  Recommended structure: <what context must be supplied to choose>
  Crossover note: N/A
  Behavior risk: N/A
  Test expectation: N/A
```

## Examples

- **O(n²) dedup by re-scan**: building a deduplicated header list with `for (field : raw) { if (find_if(output, same_name) == end) output.push_back(field); }` is O(n²) in header count because each element rescans the growing output. For unbounded, caller-controlled header counts this is `HIGH`/`CRITICAL`. Behavior-preserving fix: keep the output `vector` (preserves insertion order callers rely on) but add a side `unordered_set`/`unordered_map` of normalized names to make the membership test O(1) average → O(n). State the crossover: below a few dozen headers the flat scan may win, so gate the change on the realistic and worst-case counts and measure.
- **Tree where a flat scan suffices**: a `std::map<std::string,std::string>` for 3–5 fixed config entries pays per-node allocation and pointer-chasing for a set that never grows. Below the crossover a `vector<pair<>>` with a linear scan is faster and lighter; `MEDIUM`/`LOW`. Keep the map only if ordered iteration is a real requirement.
- **Hash on small bounded N (anti-fix)**: replacing an 8-element linear `any_of` over a fixed name list with an `unordered_set` adds hashing and allocation for no asymptotic gain at that size. Leave the scan; mark any proposed swap a `Measurement gap` unless a benchmark across N shows a win.
- **Sorted vector vs tree**: a lookup table built once at startup then queried per request is better as a sorted `vector` + `std::ranges::binary_search` (O(log n) lookup, contiguous, no per-node allocation) than a `std::map`, unless inserts continue at runtime.

## Definition Of Done

A data-structure change is ready only when:

- The dominant operation and the current asymptotic shape are named, and the chosen structure makes that operation O(1)/O(log n) where N warrants it — or the existing structure is justified as already optimal for the realistic N.
- Expected and worst-case N are stated, and the crossover is reasoned so small-N cases keep the flat scan and large/unbounded-N cases get the better structure.
- Every ordering, stability, duplicate-key, and reference-invalidation guarantee callers depend on is preserved, or the change is explicitly flagged as behavioral and routed to object-lifetime review.
- Hot-path changes carry a benchmark or profile across the expected N range; a swap justified only by Big-O at small N is recorded as a measurement gap, not a confirmed win.
- Any deferred lifetime, concurrency, or ABI/format question raised by the swap is named and routed rather than silently assumed safe.
