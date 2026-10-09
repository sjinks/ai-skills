---
name: cpp-cert
description: "Use when: reviewing, designing, implementing, or debugging C/C++ for SEI CERT secure-coding violations detected by clang-tidy cert-* checks: unchecked standard-library return values, command injection via system()/popen(), raw memory operations on non-trivial types, pointer arithmetic on polymorphic objects, exception throw/copy safety, signal-handler async-safety, predictable or unseeded RNGs, deprecated unsafe C functions, and other undefined-behavior or security-sensitive constructs."
argument-hint: "Describe the code, API, bug, or review target where a CERT C/C++ secure-coding rule may be violated."
---

# C++ CERT Secure Coding

Use this skill when C or C++ code may violate a SEI CERT C/C++ Coding Standard rule: a construct that is undefined, unspecified, security-sensitive, or error-prone by the standard's secure-coding criteria, even when it compiles cleanly and appears to work.

The goal is to make every CERT-relevant construct either compliant or explicitly justified: standard-library errors are checked, exceptions are safe to throw and copy, special members defend against misuse, signal handlers and threads stay within async-safe bounds, and no deprecated or undefined-behavior-prone API is used without a documented exception.

**UTILITY SKILL.** INVOKES: read-only file access for supplied targets; no other tools or skills. FOR SINGLE OPERATIONS: use for focused CERT-rule review, secure-coding design, or violation triage.

The clang-tidy `cert-*` checks are the canonical catalog this skill encodes. Some are standalone `cert-*` checks; others are aliases of `bugprone-*`/`misc-*`/`concurrency-*` checks. Cite the canonical `cert-<id>` check name in findings (it resolves whether the check is standalone or an alias) alongside the CERT rule ID, so the reader can cross-reference the standard and optionally automate detection. Check names below are valid as of clang-tidy 18-20; confirm against the analyzer version in use.

## Scope

- Use this skill for the CERT rules clang-tidy can detect: modifying the `std`/`posix` namespaces (DCL58-CPP), reserved identifiers (DCL37-C/DCL51-CPP), paired allocation/deallocation overloads (DCL54-CPP), runtime `assert` where `static_assert` would work (DCL03-C), C-style variadic functions (DCL50-CPP), unnamed namespaces in headers (DCL59-CPP), non-uppercase literal suffixes (DCL16-C), unchecked standard-library return values (ERR33-C), unchecked string-to-number conversion (ERR34-C), `setjmp`/`longjmp` (ERR52-CPP), exceptions escaping before `main` (ERR58-CPP), throwing exception types whose copy constructor can throw (ERR60-CPP), throw-by-value/catch-by-reference (ERR09-CPP/ERR61-CPP), float loop counters (FLP30-C), signed-char-to-larger-integer conversion (STR34-C), comparing padding or object representations (EXP42-C/FLP37-C), assignments in selection statements (EXP45-C), inconsistent enumerator initialization (INT09-C), raw `memset`/`memcpy`/`memcmp` on non-trivial types (OOP57-CPP), default `operator new` for over-aligned types (MEM57-CPP), unguarded self-assignment (OOP54-CPP), copy constructors that mutate their argument (OOP58-CPP), move constructors that copy a base/member (OOP11-CPP), pointer arithmetic on polymorphic objects (CTR56-CPP), adding a scaled integer to a pointer (ARR39-C), copying `FILE`/`pthread_mutex_t` objects (FIO38-C), `system()`/`popen()` (ENV33-C), deprecated/unsafe C functions (MSC24-C/MSC33-C), `std::rand` for pseudorandom numbers (MSC50-CPP/MSC30-C), unseeded or constant-seeded RNGs (MSC51-CPP/MSC32-C), spurious-wakeup wait loops (CON54-CPP/CON36-C), signal-handler async-safety (SIG30-C/MSC54-CPP), terminating threads with signals (POS44-C), and asynchronous thread cancellation (POS47-C).
- Apply it to API boundaries, class special-member design, error-handling paths, exception types, signal handlers, threading/cancellation code, and any use of C standard-library or POSIX functions.
- Keep the review centered on CERT-rule compliance. A finding must map to a specific CERT rule and the concrete undefined/unsafe behavior the standard cites; general style preferences are out of scope.

## DO NOT USE FOR:

- Performance tuning with no security/correctness dimension (out of scope: general copy/allocation-cost work), general object-lifetime/dangling analysis not tied to a CERT rule (out of scope: ownership/lifetime review), or data-race and synchronization-correctness review beyond the specific CERT concurrency rules listed (out of scope: general concurrency review). Name the out-of-scope concern and route it instead of judging it here.
- CERT rules that clang-tidy cannot mechanically detect and that require full program analysis (e.g. complete taint tracking, integer-overflow proofs across translation units); name the rule and recommend dedicated analysis rather than asserting compliance.
- Coroutine mechanics, build/link configuration, or correctness review with no CERT-rule mapping.

## Required Context

Collect or infer before judging:

- Target: files, diff, API, class definition, or function under review, and the language/standard (C vs C++, and the C++ version, since some rules - e.g. signal-handler constraints - depend on it).
- Type and member shape: for classes, whether they own resources (raw pointers, `FILE*`, mutexes), have user-defined copy/move/assignment, are used as exception types, or are over-aligned.
- API surface in use: which C standard-library/POSIX functions are called, whether return values are consumed, and whether Annex K bounds-checked variants are available.
- Execution context: whether code runs in a signal handler, before `main` (static/global initializers), in a thread that may be cancelled or terminated, or as a condition-variable wait.
- Existing tests and any suppressions (`NOLINT`, cast-to-void) already applied to CERT findings.

If the target cannot be seen, or the language/standard cannot be established for a standard-dependent rule, return `Verdict: BLOCK` with one open question. Do not guess whether a type is trivially copyable, whether a function's return value matters, or whether code runs in a signal handler. Insufficient-context mode takes precedence over pattern-level decision rules: general rules may be cited as context, but no verdict other than `BLOCK` may rest on an unseen target or an undetermined execution context.

## Output Depth

Default to `standard`. `quick` still reports missing required context, blockers, unmitigated HIGH/CRITICAL findings, and target-specific concerns; it only omits non-applicable checklist expansion. `standard` covers the applicable checklist with concise evidence. `exhaustive` enumerates the full checklist only when asked or when the change surface warrants it. Name the selected depth when the user asks for `quick` or `exhaustive`.

## Workflow

1. Establish context: language, C++ standard, and whether any code runs in a signal handler, before `main`, or in cancellable/terminable threads.
2. Audit declarations and namespaces: `std`/`posix` modifications, reserved identifiers, paired `new`/`delete` overloads.
3. Audit error handling: unchecked library return values, unchecked string-to-number conversions, exception escape before `main`, exception copy-constructor safety, throw/catch value category, `setjmp`/`longjmp`.
4. Audit memory and object operations: raw `mem*` calls on non-trivial types, over-aligned `operator new`, self-assignment guards, copy constructors that mutate the source, pointer arithmetic on polymorphic objects, copying `FILE`/mutex objects.
5. Audit expressions and types: float loop counters, signed-char-to-int conversions, comparison of padding/object representations.
6. Audit concurrency and signals: spurious-wakeup wait loops, signal-handler async-safety, thread termination by signal, asynchronous cancellation.
7. Audit security-sensitive API: `system()`/`popen()`, deprecated/unsafe C functions, `std::rand`, unseeded/constant-seeded RNGs.
8. For each finding, map it to its CERT rule, classify by severity, map to a verdict, and state the regression test or suppression justification each fix needs.

## Decision Rules

The Checklist is the gating source of truth. Evaluate every applicable item; do not skip a category merely because its explanations are in a reference.

Cross-cutting suppression rule: a CERT finding may be downgraded only by a documented, rule-specific exception (a CERT "exception" clause, an explicit `NOLINT` with rationale, or a cast-to-void for an intentionally ignored return where the rule permits it). An undocumented suppression is itself a finding.

Read [the rule catalog](references/rule-catalog.md) for each applicable category before choosing a CERT mapping or compliant alternative. It supplies analyzer names, exceptions, and standard-dependent qualifications; it does not replace the Checklist.

## Checklist

### Declarations And Namespaces

- No declarations are added to `std`/`posix` except permitted user-type template specializations; no reserved identifiers are declared.
- Every non-placement `operator new`/`operator delete` overload has its matching partner in the same scope.
- Compile-time-constant assertions use `static_assert`, not runtime `assert`; no C-style variadic function definitions; no unnamed namespaces in headers; literal suffixes are uppercase.

### Error Handling And Exceptions

- Checked standard-library return values are consumed and errors handled, or intentionally discarded with a documented cast-to-void.
- String-to-number conversions check for failure; no `setjmp`/`longjmp`.
- Static/global initializers cannot throw uncaught before `main`; exception types have non-throwing copy constructors; exceptions are thrown by value and caught by reference.

### Memory And Object Operations

- No raw `mem*`/`str*` byte operations on non-trivial types; over-aligned types use aligned allocation.
- Copy assignment guards against self-assignment; copy constructors do not mutate their source; move constructors move (not copy) their bases and members.
- No pointer arithmetic on polymorphic-object pointers whose dynamic type may differ, and no `sizeof`/`offsetof`-scaled value added to a pointer; `FILE`/mutex objects are handled only by pointer.

### Expressions And Types

- Loop counters are integers, not floating-point.
- `signed char` is cast through `unsigned char` before widening; no representation/padding comparison via `memcmp` on padded/non-standard-layout/float types.
- No assignment in a selection/loop condition where comparison was intended; enumerator initialization is consistent (none, first only, or all).

### Concurrency And Signals

- Condition waits re-check the predicate in a loop or use a predicate-taking overload.
- Signal handlers are async-safe, plain C-linkage, and free of C++-only constructs (for the applicable standard); threads are not terminated with `SIGTERM`; cancellation type is deferred, not asynchronous.

### Security-Sensitive API

- No `system()`/`popen()` command-processor calls; deprecated/unsafe C functions are replaced with bounds-checked alternatives and checked.
- Non-security pseudorandom numbers use a seed policy and distribution suited to the application. Preserve intentional fixed seeds for reproducible tests, with a documented test-only rationale for any suppression. When unpredictability is required, use a seed source sufficient for that requirement. Security-sensitive randomness uses a generator documented as sufficient for the application; replacing `std::rand` with an arbitrary `<random>` engine or adding a seed is not a security proof.

### Suppressions And Tests

- Every downgraded or suppressed CERT finding has a documented, rule-specific justification.
- Each fixed violation has a regression test or static-analysis assertion that fails without the fix where one is feasible.

## Severity And Verdicts

Severity reflects the CERT risk class and exploitability/UB reachability, not just pattern presence.

- `CRITICAL`: a reachable violation that is undefined behavior or a direct security vulnerability in normal operation (command injection via `system()`, `longjmp` skipping destructors on a live path, `memcpy` over a polymorphic object, pointer arithmetic on a polymorphic pointer with differing dynamic type, signal handler calling non-async-safe functions).
- `HIGH`: a violation that is UB or a security weakness but requires a specific input, error path, or platform to manifest (unchecked allocation/return value on an error path, throwing exception copy constructor, over-aligned `operator new`, unseeded RNG used for a security decision, unsafe string function with attacker-influenced length).
- `MEDIUM`: a latent or context-bounded violation (self-assignment unguarded on a class that is unlikely to self-assign today, `signed char` widening on ASCII-only data, `std::rand` for non-security randomness) that future edits or inputs will amplify.
- `LOW`: a hardening or hygiene issue (reserved-identifier naming, throw-by-value/catch-by-reference style where copies are cheap) with no current UB or security path.

Verdicts (apply BLOCK first, then CONCERNS, otherwise CLEAN subject to the stated design-stage limitation):

- `BLOCK`: missing required context, any `CRITICAL`, or any unmitigated `HIGH`.
- `CONCERNS`: no BLOCK condition applies, but any finding remains or an applicable checklist item is missing. This includes unmitigated MEDIUM/LOW findings and compensated HIGH findings. Record the justification or required correction per finding.
- `CLEAN`: every applicable checklist item holds and fixed violations have regression coverage where feasible. For design-stage or definition-only targets with no tests yet, the best achievable verdict is `CONCERNS` with test expectations recorded per finding.

A CERT finding must never be silently dropped because a fix is inconvenient: if remediation conflicts with a hard external constraint, record the residual risk and the documented exception rather than asserting compliance.

## Output Format

```text
Verdict: BLOCK | CONCERNS | CLEAN
Target: <files, diff, API, class, or function>
Language/standard: <C or C++ and version, or unknown>
Execution context: <signal handler | pre-main init | cancellable thread | normal, or unknown>

Findings:
1. <short title>
  Severity: CRITICAL | HIGH | MEDIUM | LOW
  Classification: Confirmed violation | Likely violation | Open question | Documented exception | Test gap
  Evidence: <file:line, diff hunk, or design sentence>
  Rule: <declarations-namespaces | error-handling-exceptions | memory-object-operations | expressions-types | concurrency-signals | security-api | suppressions-tests>
  CERT: <CERT rule ID and clang-tidy check name, or N/A>
  Risk: <the undefined or unsafe behavior the standard cites, and when it triggers>
  Required fix: <the compliant construct>
  Test expectation: <regression test, static-analysis assertion, or N/A>

Checklist status:
- Declarations and namespaces: covered | missing | n/a
- Error handling and exceptions: covered | missing | n/a
- Memory and object operations: covered | missing | n/a
- Expressions and types: covered | missing | n/a
- Concurrency and signals: covered | missing | n/a
- Security-sensitive API: covered | missing | n/a
- Suppressions and tests: covered | missing | n/a

Residual risk: <remaining caveats, deferred cross-skill questions, or None>
```

`Rule:` values map to checklist sections as follows: `declarations-namespaces` -> Declarations And Namespaces; `error-handling-exceptions` -> Error Handling And Exceptions; `memory-object-operations` -> Memory And Object Operations; `expressions-types` -> Expressions And Types; `concurrency-signals` -> Concurrency And Signals; `security-api` -> Security-Sensitive API; `suppressions-tests` -> Suppressions And Tests.

When no material issues exist, write exactly `Findings: None` (allowed only with `CLEAN`) and list assumptions under Residual risk. For definition-only or design-stage targets that earn `CONCERNS` solely because tests cannot exist yet, emit one `Test gap` finding with `Rule: suppressions-tests` listing the required test expectations instead of an empty findings list.

Insufficient-context mode: when the target cannot be seen or a standard-dependent rule's language/context cannot be established, emit exactly this reduced template and stop; do not emit execution context or checklist status with guessed values:

```text
Verdict: BLOCK
Target: <files, diff, API, class, or function>

Findings:
1. <missing-context short title>
  Severity: LOW
  Classification: Open question
  Evidence: <which required context is missing>
  Rule: <declarations-namespaces | error-handling-exceptions | memory-object-operations | expressions-types | concurrency-signals | security-api>
  CERT: <CERT rule ID and clang-tidy check name, or N/A>
  Risk: <why no safe conclusion is possible>
  Required fix: <what context must be supplied>
  Test expectation: N/A
```

## Examples

Read [examples](references/examples.md) for partial illustrations of common findings. They do not add requirements or authorize a transformation without the core safety checks.

## Definition Of Done

A CERT-related change is ready only when:

- Every detected violation is fixed to the compliant construct or carries a documented, rule-specific exception with residual risk recorded.
- No standard-library error path is left unchecked, no exception can escape before `main` or throw during copy while propagating, and no banned API (`system`, unsafe C functions, `std::rand` for security, `setjmp`/`longjmp`) remains without justification.
- Special members defend against self-assignment and do not mutate their source; no raw byte operations run on non-trivial types; no pointer arithmetic crosses a polymorphic boundary.
- Signal handlers, thread termination, and cancellation comply with the applicable CERT concurrency rules for the target's language standard.
- Fixed violations have regression tests or static-analysis assertions where feasible; if none were feasible, the Suppressions and tests item is n/a and does not block `CLEAN`.
- Any CERT rule requiring analysis beyond clang-tidy's reach, or any cross-skill lifetime/concurrency question, is named and routed rather than assumed compliant.
