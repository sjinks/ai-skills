# cpp-data-structure-selection

> Use when: choosing or replacing the C++ container/data structure behind a lookup, membership test, dedup, ordering, or accumulation, when a loop scans a collection that grows with input (linear scan, nested scan, repeated find), or when deciding between linear scan, hash map/set, sorted vector, balanced tree, or a small fixed table — including the crossover-size and measure-first reasoning.

This skill picks the container behind an operation so its work **scales correctly with input size**, and decides whether an existing structure should change. The canonical fix is replacing a per-element linear scan that runs once per element — an O(n²) shape — with a structure that makes the inner step O(1) or O(log n): a hash map/set, a sorted vector with binary search, or a balanced tree. The opposite is also a finding: a heavyweight node-based container used for a handful of elements where a flat array or linear scan is faster and lighter. The change must be **behavior-preserving** — same elements, same observable results and ordering guarantees, lower asymptotic or constant cost.

It helps an assistant:

- name the asymptotic shape first (nested scans over the same growing N are O(n²); one-shot O(n) scans are usually left alone) before proposing any swap
- match the structure to the dominant operation — membership → hash; ordered/range → tree or sorted vector; dedup → side set with ordered output; min/max → heap — accounting for expensive comparisons and precomputed keys
- respect the crossover, keeping a flat linear scan for small bounded N and reserving hash/tree structures for large or unbounded N, and weigh build-and-discard cost against reserve-once reuse
- preserve ordering, stability, duplicate-key, and reference-invalidation guarantees callers depend on, flagging any behavioral change instead of asserting a free swap
- gate hot-path changes on a benchmark or profile across the expected N range, recording a measurement gap when a swap is justified only by Big-O at small N
- return `BLOCK`, `CONCERNS`, or `CLEAN` with severity-tagged findings, recommended structure, crossover note, behavior risk, checklist status, and a deterministic insufficient-context template

## Files

- [`SKILL.md`](SKILL.md) — the full skill definition.
