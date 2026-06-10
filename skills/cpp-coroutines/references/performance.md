# Coroutine Performance And Allocation

Use this reference when coroutine frame size, allocation count, scheduler overhead, or hot-path latency matters.

## Frame Size Contributors

- Parameters copied into the coroutine frame.
- Locals that are live across suspension points.
- Promise object fields.
- Awaiter state stored across suspension.
- Alignment, padding, and compiler bookkeeping.

## Reducing Frame Size

- Keep large objects out of scope before `co_await` when they are not needed after resumption.
- Store large shared state outside the frame when ownership and lifetime are clear.
- Avoid capturing large lambdas or containers across suspension points.
- Split a coroutine when only a small part needs suspension.
- Measure before and after; intuitive frame-size changes are often wrong.

## Allocation Behavior

- Coroutine frames may allocate dynamically unless the compiler can elide allocation.
- Heap allocation elision is not guaranteed by the C++ language.
- Custom allocation can be provided through promise `operator new`, but pooling must respect frame lifetime, alignment, exceptions during construction, and thread safety.
- Avoid relying on allocation-free behavior without generated-code checks or allocation instrumentation in the target build.

## Measuring

- Inspect generated LLVM IR or assembly for coroutine frame allocation size and allocation calls.
- Use allocation counters in tests or benchmarks for hot paths.
- Benchmark with representative scheduler behavior; inline resume and posted resume have different costs.
- Check optimized builds. Debug builds often make coroutine frames and resume paths look much worse than release builds.

## Performance Review Questions

- Which locals survive each suspension point?
- Does the task/generator allocate per call?
- Does cancellation or exception storage add meaningful frame size?
- Can scheduler hops be coalesced without violating fairness or thread affinity?
- Is a coroutine still the simplest correct state machine for this path?