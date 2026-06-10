# Debugging C++ Coroutines

Use this reference when coroutine code leaks, hangs, resumes twice, fails to resume, swallows exceptions, or crosses scheduler/thread boundaries unexpectedly.

## First Facts To Collect

- Coroutine return type and promise type.
- Whether `initial_suspend` is lazy or eager.
- Owner of the coroutine frame and when `destroy()` runs.
- Current suspension point and awaited object.
- Whether resumption is inline, scheduled, or callback-driven.
- Exception and cancellation path.

## Symptom Table

| Symptom | Likely causes | Confirming checks | Targeted fixes |
|---|---|---|---|
| Use-after-free after callback completion | Callback kept raw coroutine handle after owner destroyed frame | Find callback registration and task destructor | Shared state, unregister on cancel, or cancel-and-join |
| Coroutine never resumes | Awaiter lost continuation, scheduler stopped, cancellation path forgot resume | Inspect `await_suspend` and scheduler queue | Store continuation once and guarantee completion or cancellation resume |
| Coroutine resumes twice | Multiple callbacks, race between cancellation and success, reusable awaiter bug | Add continuation state logging/assertions | Atomic/state guard around completion |
| Exception disappears | `unhandled_exception` swallows or stores without `await_resume` rethrow | Inspect promise exception storage | Rethrow, translate, or report explicitly |
| Destroy leaks frame | Return object does not own handle or destructor misses `destroy()` | Track construction/move/destruction | Implement move-only ownership and destroy policy |
| Wrong thread resumes | Awaiter resumes inline or on callback thread unexpectedly | Log scheduler/thread at suspend/resume | Post through required scheduler/executor |

## Debugging Playbook

1. Trace coroutine creation, first suspend, each await suspend, resume, final suspend, and destruction.
2. Add temporary IDs to coroutine frames or promise objects when multiple instances overlap.
3. Assert single completion for callback-backed awaiters.
4. Inspect move constructors and destructors of task/generator objects.
5. Reduce to a minimal coroutine with one suspension point before debugging a full pipeline.

## Sanitizers And Tools

- Use ASan for dangling references and frame-after-destroy bugs.
- Use TSan when callbacks, cancellation, or schedulers cross threads.
- Use UBSan for invalid state assumptions around handles and moved-from objects.
- Add deterministic scheduler or fake callback completion before relying on timing-based tests.

## GDB Notes

Use debugger support as an aid, not as the only proof of correctness. Useful checks include:

```bash
(gdb) info locals
(gdb) bt
(gdb) info threads
```

When a coroutine handle is visible, inspect the promise through implementation-specific handle storage only as a debugging tactic. Layout details can vary by compiler and standard library, so avoid baking debugger-only assumptions into code or tests.

GDB versions and compiler support differ. If coroutine-specific commands are available in the local toolchain, use them to list suspended coroutines and inspect frames; otherwise rely on logged coroutine IDs, promise state, scheduler queues, and sanitizer evidence.