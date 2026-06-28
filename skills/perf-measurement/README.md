# perf-measurement

> Use when: optimizing or investigating the throughput, latency, or per-request cost of a C++ network server (or similar hot-path service); deciding whether a change actually helped; choosing a metric that resists noise; isolating where time/allocations go with profiling and controls; or avoiding common measurement mistakes (noisy benchmarks, contaminated runs, blaming the wrong layer, custom-allocator cargo-culting).

This skill makes server/hot-path performance work **empirical** instead of speculative: pick a metric that survives noise, isolate the cost with controls and profiling, attribute it to the right layer, change one thing, then re-measure. The governing rule: measure, do not guess; isolate, do not assume; change one thing, then re-measure — and a truthful "this did not help, and here is the number that proves it" is a successful outcome. It is standalone: it decides *what to measure and whether it worked*, routing the source-level transformation and framework mechanics to the relevant language/library review.

It helps an assistant:

- pick a metric that matches the change size: throughput (noisy, ~10% variance) only for >~15% changes; the median of repeated runs for the 3–15% middle band; a direct, deterministic count (allocations, syscalls) for single-digit-percent countable changes
- count allocations directly with a `malloc`-shim `LD_PRELOAD`, differencing two fixed request counts over one keep-alive connection to get an exact, noise-free per-request figure
- isolate a layer's cost with control/reference servers (raw-framework, no-serialization, no-parse) and judge against the realistic ceiling, not an unreachable no-work ideal
- profile under load with flat self-time, bucket diffuse template-heavy hot spots by category, and separate kernel from addressable user-space cost
- change one thing, re-measure under identical conditions, and keep or revert — recording negative results
- avoid the known no-ops and traps (custom allocators without cross-thread contention, small-buffer `std::function` myths, contaminated benchmarks, Docker NAT latency, non-optimized builds) by measuring before believing them

## Files

- [`SKILL.md`](SKILL.md) — the full skill definition.
