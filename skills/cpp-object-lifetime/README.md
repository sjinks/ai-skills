# cpp-object-lifetime

> Use when: reviewing, designing, implementing, or debugging C++ object lifetime, dangling pointers or references, iterator invalidation, reference invalidation, string_view or span escaping its owner, temporaries bound to references, lambda captures outliving scope, use-after-move, use-after-free, returning references to locals, container reallocation, or RAII ownership boundaries.

This skill is aimed at C++ code where a pointer, reference, view, iterator, or callback borrows storage owned by another object and the outlives-relationship is not enforced by construction.

It helps an assistant:

- map owners and borrowers, then check every borrow interval against moves, reallocation, container mutation, scope exit, and destruction order
- catch escaping `string_view`/`span`, references returned to locals, references held across `push_back`/`erase`, and iterator invalidation per container rules
- review lambda captures, stored callbacks, and async handoff so `this` and references cannot be used after their owners are destroyed
- enforce move-semantics discipline (moved-from objects limited to destruction, assignment, precondition-free operations, and specified post-move states) and smart-pointer ownership boundaries with `weak_ptr` cycle breaks
- return `BLOCK`, `CONCERNS`, or `CLEAN` with owners/borrowers, findings, checklist status, test expectations, and an insufficient-context template

## Files

- [`SKILL.md`](SKILL.md) — the full skill definition.
