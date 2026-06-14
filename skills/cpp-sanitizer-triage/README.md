# cpp-sanitizer-triage

> Use when: triaging, interpreting, or acting on AddressSanitizer, ThreadSanitizer, UndefinedBehaviorSanitizer, MemorySanitizer, or LeakSanitizer reports, including heap-use-after-free, heap-buffer-overflow, stack-use-after-return, data race reports, ODR violation reports, suppression files, sanitizer flags and runtime options, symbolization problems, false-positive claims, and deciding whether a report is real, its root cause frame, and the fix owner.

This skill is aimed at sanitizer reports (ASan, TSan, UBSan, MSan, LSan) that need disciplined triage: real or not, where the root cause is, and whether the action is a fix, a scoped suppression, or a configuration change.

It helps an assistant:

- read report anatomy: error kind, faulting access, allocation/free/previous-write stacks, shadow bytes, mutex and thread annotations
- separate the symptom frame from the root-cause frame and route fixes to the contract violation, not the faulting access
- classify reports as true positives, named tool limitations, or configuration artifacts (partial MSan instrumentation, uninstrumented synchronization for TSan)
- reject timing/rarity-based false-positive claims and require a named happens-before mechanism
- enforce suppression discipline: narrowest matcher, comments with issue links, third-party orientation, review notes
- keep sanitizer configurations compatible and verified (separate builds for TSan/MSan, symbolization working, regression tests under the sanitizer)
- return `BLOCK`, `CONCERNS`, or `CLEAN` with classification, root cause vs symptom, findings, checklist status, and an insufficient-context template

## Files

- [`SKILL.md`](SKILL.md) — the full skill definition.
