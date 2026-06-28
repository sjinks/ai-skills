---
name: perf-measurement
description: "Use when: optimizing or investigating the throughput, latency, or per-request cost of a C++ network server (or similar hot-path service); deciding whether a change actually helped; choosing a metric that resists noise; isolating where time/allocations go with profiling and controls; or avoiding common measurement mistakes (noisy benchmarks, contaminated runs, blaming the wrong layer, custom-allocator cargo-culting)."
argument-hint: "Describe the server/hot path, the change you want to evaluate, or the throughput/latency/allocation question you need measured rather than guessed."
user-invocable: true
---

# Performance Measurement Methodology

Use this skill to make server/hot-path performance work **empirical** instead of speculative: pick a metric that survives noise, isolate the cost with controls and profiling, attribute it to the right layer, change one thing, and re-measure. The recurring failure mode this skill prevents is *plausible-but-wrong* optimization — a change that "should" help (smaller capture, faster allocator, fewer copies) but moves nothing, or a change credited by a contaminated benchmark.

The governing rule: **measure, do not guess; isolate, do not assume; change one thing, then re-measure.** A truthful "this did not help, and here is the number that proves it" is a successful outcome, not a failure.

**WORKFLOW SKILL.** INVOKES: terminal (build, run servers, load generators, profilers, allocation counters) and read-only file access. This skill decides *what to measure and whether a change worked*; route the source-level transformation itself, and stack-specific framework mechanics, to the relevant language/library review. FOR SINGLE OPERATIONS: use to choose a metric, design a control experiment, or sanity-check a benchmark result.

## Scope

- Use this skill for: choosing the right performance metric for a given change size; designing control experiments that isolate one layer's cost (e.g. a "no-serialization" or "no-parse" reference server); profiling under load and attributing cost to buckets; validating that an optimization actually moved the metric; and recognizing when a result is contaminated or a proposed fix is a known no-op.
- Apply it to: per-connection/per-request server hot paths, allocation-reduction work, serialization/parsing cost, concurrency scaling questions, and "is X faster than Y" comparisons.
- Keep findings tied to a number from a reproducible procedure. Every claim ("+9%", "−4 allocs/request", "now matches the baseline") names the metric, the tool, and the conditions.

## DO NOT USE FOR:

- The source-level transformation itself (unnecessary copy, missing `reserve`, `std::function` capture cost) — that is C++ source-level performance review. This skill decides *what to measure and whether it worked*; the source-level review decides *what to change*.
- Framework-specific behavior mechanics (Beast serializer/parser internals, Asio executor/strand semantics) — a networking-library concern.
- Correctness, lifetime, or concurrency-safety review of an optimization — an object-lifetime / concurrency review concern. A faster-but-wrong change is out of scope here; name the dependency when a finding rests on it.

## Core Principles

### 1. Pick a metric that matches the change size

- **Throughput (req/s) is noisy** — expect ~10% run-to-run variance, and it is sensitive to *any* competing CPU load on the machine.
  - A change >~15% is resolvable from a single before/after pair.
  - A change of 1–3% is below the noise floor; do not chase it with throughput at all — prefer a direct count (below) if the change is countable.
  - A change in the **3–15% middle band** needs repeated runs: take the median of 3–5 runs before and after under identical conditions, and treat the result as real only if the medians separate by more than the observed run-to-run spread. If a deterministic count exists for the change, prefer it instead.
- For small, countable changes (removing N allocations, one syscall, one copy), use a **direct, noise-free count** instead of throughput. Allocation count per request is deterministic and load-independent.
- Latency percentiles (p99) are more stable than mean throughput for tail-behavior changes; report them when the change targets latency.

### 2. Count allocations directly when the change is about allocations

- An `LD_PRELOAD` shim that overrides `malloc`/`calloc`/`realloc` and prints a total at exit gives an exact allocation count for a fixed workload (no profiler, no sampling error). Gotchas: handle `dlsym` calling `calloc` during bootstrap (serve early `calloc` from a small static arena), and make `free` skip bootstrap-arena pointers. Minimal skeleton (build with `gcc -O2 -shared -fPIC -o mallocount.so mallocount.c -ldl`, then `LD_PRELOAD=./mallocount.so <server>`):

  ```c
  #define _GNU_SOURCE
  #include <dlfcn.h>
  #include <stdatomic.h>
  #include <stdio.h>
  static atomic_ullong n;
  static void *(*real_malloc)(size_t);
  void *malloc(size_t s){ if(!real_malloc) real_malloc=dlsym(RTLD_NEXT,"malloc");
    atomic_fetch_add(&n,1); return real_malloc(s); }
  __attribute__((destructor)) static void rep(void){
    unsigned long long total = atomic_load(&n);
    fprintf(stderr,"allocs=%llu\n",total); }
  // Extend with calloc/realloc the same way; guard calloc against the dlsym
  // bootstrap (serve from a small static arena until real_calloc resolves) and
  // make free() ignore arena pointers.
  ```
- Isolate the **per-request** figure by differencing two fixed request counts over one keep-alive connection: `per_request = (allocs@N2 − allocs@N1) / (N2 − N1)`. The subtraction cancels process startup and first-request warm-up.
- This metric is the right gate for iterating allocation reductions: each step's effect is exact and immune to throughput noise.

### 3. Isolate cost with control experiments (reference servers)

- To learn how much a *layer* costs, build a minimal server that does everything except that layer, and compare. Examples: a "raw framework" server (no application abstraction) isolates your library's overhead; a "pre-formatted bytes" server that skips serialization isolates serializer cost; an "echo without parse" path isolates parser cost.
- Interpret against the right ceiling: the **realistic** ceiling for your stack is the raw-framework server (it still does the unavoidable parse/scheduler/syscall work), not the absolute no-work ceiling. "Matching the raw framework" is usually the real success criterion, because the gap above it is inherent to the stack and shared by every server on it.

### 4. Profile to attribute, then bucket

- Profile under sustained load (`perf record -g` with frame pointers: build with `-fno-omit-frame-pointer`, `-O2 -g`). User-space profiling works at the default `kernel.perf_event_paranoid = 2`; set it `<= 1` (e.g. `sudo sysctl kernel.perf_event_paranoid=1`) to also profile the **kernel** side (needed for the kernel-vs-user split below), and `kernel.kptr_restrict=0` to resolve kernel symbol names. Use the **flat self-time** view (`--no-children`) to find where cycles are actually spent, not just call frequency.
- Template-heavy C++ (Beast/Asio) produces enormous symbol names and diffuse hot spots with no single symbol above ~1%. **Bucket** self-time by category (allocation, refcount atomics, serialization, parsing, scheduler/executor, syscall, string/memcpy) to see the real distribution.
- Separate **kernel** from **user-space**: a network server spends much of its time in the kernel TCP/syscall path, which is inherent and not addressable in your code. Rank the **user-space** buckets to find what *you* can change.
- Re-profile after a change: a successful optimization should visibly shrink its target bucket and shift the bottleneck elsewhere.

### 5. Change one thing, re-measure, keep or revert

- Apply one optimization, re-run the same metric under the same conditions, and record before/after. If the metric did not move, **revert** — an unhelpful change is churn and risk for no benefit.
- A measured negative result is valuable: it disproves a hypothesis and prevents the same idea being re-attempted. Record *why* it did not help.

## Known No-Ops And Traps (measure before believing these "fixes")

- **A custom allocator (tcmalloc/jemalloc) rarely gives the *big* win you expect when there is no cross-thread allocation contention.** Their headline advantage is multi-threaded arena contention; a one-thread-per-`io_context` (e.g. `SO_REUSEPORT` fleet) model has none, so any remaining difference (a faster fast-path or less fragmentation) is small and must be measured, often neutral-to-slightly-slower. The large lever is *fewer* allocations, not swapping `malloc`. Test it in 2 minutes with `LD_PRELOAD=…/libjemalloc.so.2` before committing to the dependency.
- **Shrinking a `std::function`'s capture to fit the small buffer does nothing if the capture is non-trivially-copyable** (e.g. captures a `shared_ptr`): libstdc++ only uses its small-buffer for trivially-copyable callables, so it heap-allocates regardless of size. (A source-level type-erasure/callable concern.)
- **A contaminated benchmark is worse than no benchmark.** If a CPU-intensive job is running on the machine, every throughput number is depressed and the *relative* ranking can also distort. Discard contaminated runs; only benchmark on an otherwise-idle host. A tell: the known-baseline server comes in well below its established number.
- **Docker NAT/bridge networking inflates latency** and distorts proxy-vs-origin comparisons; use host networking for a fair loopback path.
- **Use the optimized build.** Benchmarking a `RelWithDebInfo`/`-O2` (or worse, debug) build understates real performance; build `-O3 -DNDEBUG` for the numbers you report (keep a separate frame-pointer build for profiling).

## Scaling Note (server concurrency)

- A single shared acceptor + shared `io_context` across N threads serializes accept/dispatch work and plateaus well before all cores. For multi-core throughput, prefer **N independent reactors**, each with its own `io_context`/thread and `SO_REUSEPORT`, so the kernel load-balances accepts with near-zero shared-state contention (the nginx worker-process model). This is a deployment/topology change, often with no library code change, and frequently the single largest throughput lever. Route the async-library mechanics to a networking-library concern.

## Workflow

1. State the question and the change to evaluate. Identify whether it is large (throughput-resolvable) or small (needs a count).
2. Choose the metric: throughput/latency under a load generator for large/end-to-end changes; a direct allocation/syscall count for small countable changes.
3. Establish a clean baseline on an idle, optimized (`-O3`) build. For layer-cost questions, also build the relevant control/reference server.
4. Make exactly one change. Re-measure under identical conditions.
5. If it moved the metric meaningfully, keep it (with a regression test that the behavior is unchanged); if not, revert and record the negative result.
6. Re-profile to confirm the bottleneck shifted, and to choose the next target. Stop when the remaining cost is inherent to the stack (shared with the raw-framework control).

## Checklist

This checklist restates the Core Principles as a quick pass/fail verification; it adds no new obligations.

- The metric matches the change size: throughput for >~15% changes; the median of 3–5 repeated runs for the 3–15% band; a deterministic count for sub-~3% changes or whenever a countable change exists.
- Numbers come from an idle, `-O3` build; profiling uses a separate frame-pointer build.
- Allocation claims are backed by a direct count (e.g. `mallocount` differencing), not inferred from reading the code.
- Layer-cost claims are backed by a control/reference server that isolates that layer.
- The comparison ceiling is the realistic one (raw framework), not an unreachable no-work ideal.
- Each kept change has a before/after number and a behavior-preserving regression test; each rejected change is reverted with the negative result recorded.
- No "fix" from the Known No-Ops list was applied without measuring it first.
- A suspiciously low known-baseline number triggers a contamination check before the run is trusted.
