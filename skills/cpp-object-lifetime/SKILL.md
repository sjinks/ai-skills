---
name: cpp-object-lifetime
description: "Use when: reviewing, designing, implementing, or debugging C++ object lifetime, dangling pointers or references, iterator invalidation, reference invalidation, string_view or span escaping its owner, temporaries bound to references, lambda captures outliving scope, use-after-move, use-after-free, returning references to locals, container reallocation, or RAII ownership boundaries."
argument-hint: "Describe the code, API, bug, or review target where object lifetime, ownership, or invalidation is in question."
user-invocable: true
---

# C++ Object Lifetime

Use this skill when C++ code creates, stores, passes, captures, or returns a pointer, reference, view, iterator, or callback whose validity depends on another object's lifetime, and that dependency is not enforced by construction.

The goal is to make every lifetime dependency explicit: who owns the storage, how long the borrower may use it, and which operations invalidate it.

**UTILITY SKILL.** INVOKES: read-only file access for supplied targets; no other tools or skills. FOR SINGLE OPERATIONS: use for focused lifetime review, ownership design, invalidation analysis, or test planning.

## Scope

- Use this skill for dangling pointers/references, iterator and reference invalidation, view types (`string_view`, `span`, `initializer_list`, ranges) escaping their owner, temporaries bound to references, lambda capture lifetime, use-after-move, use-after-free, double-free, returning references to locals, and ownership-boundary design (`unique_ptr`, `shared_ptr`, `weak_ptr`, raw pointers, references).
- Apply it to API signatures (parameter and return lifetime contracts), data members that borrow, callback registration, container mutation during iteration, and cross-thread object handoff where the lifetime question is who-outlives-whom.
- Keep the review centered on lifetime and ownership. Treat data-race and synchronization questions as residual context unless the race is itself a lifetime bug (object destroyed while another thread uses it).

## DO NOT USE FOR:

- Coroutine frame, promise, or awaiter lifetime mechanics; algorithmic or style review with no lifetime dependency; build/link errors; pure performance tuning.
- Interpreting sanitizer reports when the task is triage of tool output rather than reasoning about ownership in code under review.

## Required Context

Collect or infer before judging:

- Target: files, diff, API, or design sketch under review.
- Owners and borrowers: which objects own storage; which pointers, references, views, iterators, captures, or callbacks borrow it.
- Lifetime events: construction, move, reallocation, container mutation, `reset`/`release`, scope exit, destruction order, thread or callback boundaries that the borrowed data crosses.
- Concurrency exposure: whether any borrower can outlive the owner via another thread, queued callback, timer, or detached work.
- Existing tests and sanitizer/CI coverage relevant to lifetime.

If the target or the owner/borrower relationship cannot be established, return `Verdict: BLOCK` with one open question. Do not guess ownership. Insufficient-context mode takes precedence over pattern-level decision rules: general rules may be cited as context, but no verdict other than `BLOCK` may rest on an unseen target.

## Output Depth

Default to `standard`. `quick` still reports missing required context, blockers, unmitigated HIGH/CRITICAL findings, and target-specific concerns; it only omits non-applicable checklist expansion. `standard` covers the applicable checklist with concise evidence. `exhaustive` enumerates the full checklist only when asked or when the risk surface warrants it. Name the selected depth when the user asks for `quick` or `exhaustive`.

## Workflow

1. Map ownership: for each piece of storage, name the owner (stack scope, container, smart pointer, singleton, caller).
2. Map borrows: every raw pointer, reference, view, iterator, capture, and callback that refers into owned storage, and the interval it is used.
3. Check each borrow against the owner's lifetime events: can a move, reallocation, erase, reset, scope exit, or destruction occur inside the borrow interval?
4. Check API contracts: do signatures state lifetime expectations (borrowed parameter must outlive call vs. outlive object), and do call sites honor them?
5. Check captures and callbacks: what does each lambda capture by reference or pointer, and can it run after those objects are gone?
6. Check move semantics: which objects are used after `std::move`, and is the moved-from state actually valid for that use?
7. Classify findings by severity, map to a verdict, and state the regression tests or sanitizer coverage each fix needs.

## Decision Rules

The Checklist below is the gating source of truth when these rules overlap; the rules explain rationale.

- When a function returns a reference, pointer, or view, name the owner whose lifetime backs it. If the owner is a local, a temporary, or a parameter taken by value, the return dangles - return by value or restructure ownership.
- When a class member is a reference, raw pointer, `string_view`, or `span`, the class borrows. Document the outlives-contract in the type, prefer constructor injection of stable owners, and forbid construction from temporaries (delete rvalue overloads or take ownership instead).
- When `string_view` or `span` parameters are stored beyond the call, treat the signature as wrong: storing requires owning (`std::string`, `std::vector`) or a documented outlives-contract enforced at every call site.
- When code mutates a container during iteration, use the erase-remove idiom, the iterator returned by `erase`, index-based loops with explicit adjustment, or collect-then-apply. Apply each container's invalidation rules exactly: vector insertion invalidates iterators, references, and pointers at or after the insertion point even without reallocation, and all of them when reallocation occurs; unordered-container insertion may invalidate iterators on rehash but never invalidates references or pointers to surviving elements, while `erase` invalidates iterators, references, and pointers to the erased elements only; node-based containers (map, set, list) keep iterators, references, and pointers to surviving elements valid.
- When a lambda captures `this`, a reference, or a pointer and is stored, posted, or detached, prove the captured object outlives every possible invocation; otherwise capture by value, capture a `shared_ptr`/`weak_ptr`, or unregister deterministically before destruction.
- When an object is used after `std::move`, allow only operations valid on a moved-from object of that exact type: destruction, assignment, precondition-free operations, and specified post-move states (`unique_ptr`/`shared_ptr` are null/empty); reads that depend on unspecified value state are findings.
- When `shared_ptr` cycles are possible (parent-child, observer lists, callbacks capturing owners), break the cycle with `weak_ptr` and define which side is owning.
- When `this` is handed to asynchronous work, prefer `enable_shared_from_this` plus `weak_from_this` checks, or a cancellation/unregistration step in the destructor that is proven to run before the callback can fire.
- When a temporary is bound to a reference, rely on lifetime extension only for direct binding to a local `const&`/`&&` (including via prvalue conditional expressions); extension does not apply to references returned from functions, reference members initialized in a mem-initializer, or function parameters.
- When a pointer or sub-object reference is taken from a temporary (`c_str()`/`data()` of a temporary string, a stored `std::initializer_list`, range-for over a temporary's sub-object before C++23), the backing object dies at the end of the full expression or statement; copy into owned storage instead.
- When destruction order matters across translation units or threads (statics, singletons, thread-locals, detached threads), make the order explicit with owned composition or controlled shutdown; do not rely on link order or accident.

## Checklist

### Returns And Parameters

- No function returns a reference, pointer, iterator, or view backed by a local, temporary, or by-value parameter.
- Lifetime contracts of returned borrows (valid until next mutation, valid while owner lives) are documented and honored at call sites.
- Parameters stored beyond the call are owned (by value or moved-in), or the borrowed contract is explicit in the API and checked at call sites.

### Members And Construction

- Borrowing members (`T&`, `T*`, `string_view`, `span`) have an explicit outlives-contract; constructors cannot silently accept temporaries.
- Order of member initialization matches declaration order where members depend on each other.
- Self-registration in constructors has a matching deterministic unregistration in the destructor, and no callback can fire between destructor start and unregistration.

### Containers And Iterators

- No iterator, reference, or pointer into a container is used across an operation that may invalidate it (insert, erase, reallocation, rehash) per that container's rules.
- Erase-during-iteration uses a valid idiom; algorithms receiving iterator pairs cannot mutate the underlying container.
- References into a vector are not retained across `push_back`/`emplace_back`/`reserve`; keys/values in node-based containers are only assumed stable where the standard guarantees it.

### Captures, Callbacks, And Async Handoff

- Every stored or posted lambda's captures are owned, refcounted, or proven to outlive all invocations.
- `this` captured into async work is protected by `weak_ptr`/`shared_from_this`, cancellation, or join-before-destroy.
- Detached threads and fire-and-forget tasks do not reference stack frames or objects with narrower lifetime.

### Moves And Smart Pointers

- Uses of moved-from objects are limited to operations valid for that exact type: destruction, assignment, and precondition-free operations such as `clear()` re-initialization. For standard containers and strings the moved-from state is valid but unspecified, so calling `empty()` is allowed but relying on its result is a finding; `unique_ptr`/`shared_ptr` are guaranteed null/empty after move and may be tested.
- `unique_ptr`/`shared_ptr` ownership boundaries are explicit; raw pointers are non-owning observers only.
- `shared_ptr` cycles are broken with `weak_ptr`; `get()` results never outlive the smart pointer that produced them.

### Tests

- Regression tests (or sanitizer-exercised paths) exist for each fixed lifetime bug class: the invalidating operation runs inside the borrow interval and the test fails without the fix.

## Severity And Verdicts

- `CRITICAL`: a reachable code path uses a dangling pointer/reference/view/iterator or moved-from state in a way that corrupts memory or violates invariants in normal operation.
- `HIGH`: a lifetime violation exists but requires a specific reordering, container growth, timing, or shutdown path to trigger.
- `MEDIUM`: a missing lifetime contract, undocumented borrow, or test gap that future edits are likely to convert into a dangling use.
- `LOW`: clarity or hardening issue (naming, comment, redundant ownership) with no current dangling path.

Verdicts:

- `BLOCK`: missing required context, any `CRITICAL`, or any unmitigated `HIGH`.
- `CONCERNS`: remaining `HIGH`/`MEDIUM` findings each have a compensating control, accepted tradeoff, or bounded reachability.
- `CLEAN`: every applicable checklist item holds and existing regression tests cover the fixed classes. For design-stage targets with no code or tests yet, the best achievable verdict is `CONCERNS` with test expectations recorded per finding.

## Output Format

```text
Verdict: BLOCK | CONCERNS | CLEAN
Target: <files, diff, API, or design>
Owners: <storage owners in scope>
Borrowers: <pointers/references/views/iterators/captures in scope>

Findings:
1. <short title>
  Severity: CRITICAL | HIGH | MEDIUM | LOW
  Classification: Confirmed issue | Likely risk | Open question | Accepted tradeoff | Test gap
  Evidence: <file:line, diff hunk, or design sentence>
  Rule: <returns/parameters | members/construction | containers/iterators | captures/callbacks | moves/smart-pointers | tests>
  Risk: <what dangles, when, and what the use-after does>
  Required guard: <ownership or API change>
  Test expectation: <regression test or N/A>

Checklist status:
- Returns and parameters: covered | missing | n/a
- Members and construction: covered | missing | n/a
- Containers and iterators: covered | missing | n/a
- Captures, callbacks, and async handoff: covered | missing | n/a
- Moves and smart pointers: covered | missing | n/a
- Tests: covered | missing | n/a

Residual risk: <remaining caveats or None>
```

`Rule:` values map to checklist sections as follows: `returns/parameters` -> Returns And Parameters; `members/construction` -> Members And Construction; `containers/iterators` -> Containers And Iterators; `captures/callbacks` -> Captures, Callbacks, And Async Handoff; `moves/smart-pointers` -> Moves And Smart Pointers; `tests` -> Tests.

When no material issues exist, write exactly `Findings: None` (allowed only with `CLEAN`) and list assumptions under Residual risk. For design-stage targets that earn `CONCERNS` solely because tests cannot exist yet, emit one `Test gap` finding with `Rule: tests` listing the required test expectations instead of an empty findings list.

Insufficient-context mode: when the target or owner/borrower relationship cannot be established, emit exactly this reduced template and stop; do not emit owners, borrowers, or checklist status with guessed values:

```text
Verdict: BLOCK
Target: <files, diff, API, or design>

Findings:
1. <missing-context short title>
  Severity: LOW
  Classification: Open question
  Evidence: <which required context is missing>
  Rule: <returns/parameters | members/construction | containers/iterators | captures/callbacks | moves/smart-pointers>
  Risk: <why no safe conclusion is possible>
  Required guard: <what context must be supplied>
  Test expectation: N/A
```

## Examples

- Escaping view: `std::string_view name() { std::string s = build(); return s; }` returns a view of a destroyed local. Fix: return `std::string` by value.
- Reallocation invalidation: `auto& first = v.front(); v.push_back(x); use(first);` - `push_back` may reallocate, leaving `first` dangling. Fix: take the reference after mutation, or use an index.
- Capture outliving owner: a member function posts `[this]{ flush(); }` to a timer queue; the object can be destroyed before the timer fires. Fix: capture `weak_from_this()` and lock before use, or cancel the timer in the destructor and prove cancellation completes first.

## Definition Of Done

A lifetime change is ready only when:

- Every borrow has a named owner and a stated interval, and no lifetime event can occur inside that interval.
- API signatures express their lifetime contracts; storing a borrowed parameter requires ownership or an explicit documented contract.
- Stored or posted callbacks cannot run after their captured objects are destroyed.
- Moved-from usage satisfies the Moves And Smart Pointers checklist items.
- Regression tests exercise the invalidating operation inside the borrow interval for each fixed bug class; if no bug classes were fixed, the Tests item is n/a and does not block `CLEAN`.
