---
name: cpp-cert
description: "Use when: reviewing, designing, implementing, or debugging C/C++ for SEI CERT Coding Standard violations - modifying std namespaces, reserved identifiers, paired new/delete, unchecked standard-library return values, unchecked string-to-number conversions, setjmp/longjmp, exceptions thrown before main or from exception copy constructors, throw-by-value/catch-by-reference, float loop counters, signed-char-to-int conversions, padding/representation comparison, raw memory calls on non-trivial types, over-aligned operator new, self-assignment, pointer arithmetic on polymorphic objects, copying FILE/mutex objects, system()/popen(), deprecated unsafe C functions, std::rand and unseeded RNGs, signal-handler safety, and unsafe thread cancellation or termination."
argument-hint: "Describe the code, API, bug, or review target where a CERT C/C++ secure-coding rule may be violated."
user-invocable: true
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

The Checklist below is the gating source of truth when these rules overlap; the rules explain rationale. Each rule names the CERT rule ID and the clang-tidy check it encodes. The subheadings match the Checklist sections so a rule and its gating item are found together.

Cross-cutting suppression rule: a CERT finding may be downgraded only by a documented, rule-specific exception (a CERT "exception" clause, an explicit `NOLINT` with rationale, or a cast-to-void for an intentionally ignored return where the rule permits it). An undocumented suppression is itself a finding.

### Declarations And Namespaces

- When code adds declarations to namespace `std` or `posix` (other than the permitted explicit specializations of user-defined-type templates), it is undefined behavior - remove the modification (DCL58-CPP, `cert-dcl58-cpp`).
- When an identifier uses a reserved form (leading underscore + uppercase or double underscore, or names reserved by the implementation), rename it (DCL37-C/DCL51-CPP, `cert-dcl37-c`/`cert-dcl51-cpp`).
- When a class overloads a non-placement `operator new`, it must overload the corresponding `operator delete` in the same scope, and vice versa - add the missing partner (DCL54-CPP, `cert-dcl54-cpp`).
- When a runtime `assert` tests a condition that is constant at compile time, use `static_assert` instead - it fails the build rather than at run time (DCL03-C, `cert-dcl03-c`).
- When a function is defined as a C-style variadic (`...`) function, replace it with a C++ variadic template / parameter pack, which is type-safe (DCL50-CPP, `cert-dcl50-cpp`).
- When an unnamed (anonymous) namespace appears in a header, every translation unit including it gets distinct symbols, risking ODR violations and bloat - move it to a source file or use `inline`/named entities (DCL59-CPP, `cert-dcl59-cpp`).
- When an integer or floating-point literal uses a lowercase `l`-family suffix (`l`, `ll`, `lu`, `llu`), uppercase it (`L`, `LL`, ...) so it cannot be misread as a digit `1` (DCL16-C, `cert-dcl16-c`).

### Error Handling And Exceptions

- When a checked standard-library function's return value is ignored, consume it and handle the error; if intentionally discarded and the rule permits, cast to `void` with a comment (ERR33-C, `cert-err33-c` - ships a CERT-specified function list; the related `bugprone-unused-return-value` is a separate, user-configured check with different defaults).
- When converting a string to a number with `atoi`/`atol`/`atoll`/`scanf`-family without error checking, use `strtol`-family (or C++ facilities) and check the result (ERR34-C, `cert-err34-c`).
- When `setjmp`/`longjmp` is used, replace it with structured control flow or C++ exceptions; `longjmp` across automatic objects does not run destructors and is undefined in many cases (ERR52-CPP, `cert-err52-cpp`).
- When a `static`/`thread_local` object's initializer can throw, an exception thrown before `main` cannot be caught and calls `std::terminate` - make the initializer non-throwing or defer it (ERR58-CPP, `cert-err58-cpp`).
- When a type is thrown as an exception, its copy constructor must not throw (a throwing copy during exception propagation calls `std::terminate`) - make the exception type's copy constructor `noexcept` (ERR60-CPP, `cert-err60-cpp`).
- When throwing, throw an anonymous temporary by value; when catching a non-trivial type, catch by reference, to avoid slicing and extra copies (ERR09-CPP/ERR61-CPP, `cert-err09-cpp`/`cert-err61-cpp`).

### Memory And Object Operations

- When `memset`/`memcpy`/`memmove`/`memcmp` (or `str*` equivalents) is applied to a non-trivial type, use the type's constructors, assignment, and comparison operators instead; raw byte operations bypass invariants and vtables (OOP57-CPP, `cert-oop57-cpp`).
- When allocating an over-aligned type (alignment greater than fundamental) via the default `operator new`, the returned storage may be under-aligned - provide an aligned allocation path (MEM57-CPP, `cert-mem57-cpp`).
- When a user-defined copy assignment operator on a class with a pointer/array/owning field does not guard against self-assignment, add a self-check or use copy-and-swap / copy-and-move (OOP54-CPP, `cert-oop54-cpp`).
- When a copy constructor mutates its source argument, the copy is not a copy - make the source parameter `const` and copy without modifying it (OOP58-CPP, `cert-oop58-cpp`).
- When a move constructor's mem-initializer list initializes a base or member through its copy constructor instead of its move constructor, it silently copies - move the base/member (OOP11-CPP, `cert-oop11-cpp`; the broader move-semantics-cost rationale is general performance work, mapped here only for the CERT rule).
- When pointer arithmetic is performed on a pointer whose static type declares a virtual function, the dynamic type may have a different size, giving undefined behavior - index through the correct dynamic type or make the leaf type `final` (CTR56-CPP, `cert-ctr56-cpp`).
- When a value already scaled by `sizeof`/`alignof`/`offsetof` is added to or subtracted from a pointer, the arithmetic scales it again by the pointee size, producing a doubly-scaled (often out-of-bounds) address - add the element count directly, not the byte count (ARR39-C, `cert-arr39-c`).
- When a `FILE` or `pthread_mutex_t` object is declared by value or dereferenced as a value, it must not be copied - hold and pass it only through a pointer (FIO38-C, `cert-fio38-c`).

### Expressions And Types

- When a floating-point variable is used as a loop counter, accumulated rounding makes the iteration count unpredictable - use an integer counter (FLP30-C, `cert-flp30-c`).
- When a `signed char` is converted to a wider integer (assignment, comparison with `unsigned char`, or array subscript), cast through `unsigned char` first so non-ASCII bytes do not become negative (STR34-C, `cert-str34-c`).
- When `memcmp` compares whole-object representations of types with padding, non-standard layout, or floating-point members, compare value representations field-by-field instead - padding and `-0.0/NaN` bits make the byte comparison wrong (EXP42-C/FLP37-C, `cert-exp42-c`/`cert-flp37-c`).
- When an assignment (`=`) appears inside an `if` condition where a comparison (`==`) was probably meant, use `==`, or wrap a deliberate assignment in extra parentheses (EXP45-C; clang-tidy's `bugprone-assignment-in-if-condition` covers `if` conditions only and there is no dedicated `cert-exp45-c` check, so loop-condition and logical-operand cases need manual review).
- When an enum mixes explicitly-initialized and implicitly-valued enumerators, two enumerators can silently collide; initialize none, only the first, or all enumerators consistently (INT09-C, `cert-int09-c`).

### Concurrency And Signals

- When `wait`/`wait_for`/`wait_until`/`cnd_wait`/`cnd_timedwait` is called outside a loop that re-checks the condition predicate (or without a predicate argument), wrap it so spurious wakeups cannot proceed past an unmet condition (CON54-CPP/CON36-C, `cert-con54-cpp`/`cert-con36-c`).
- When a signal handler calls non-async-signal-safe functions, uses C++-only constructs, or has non-C linkage, restrict it to async-safe functions and a plain C-linkage POD function (SIG30-C/MSC54-CPP, `cert-sig30-c`/`cert-msc54-cpp`; some C++-specific diagnostics are standard-dependent, so confirm the check's behavior for the target standard rather than assuming it is fully active or fully off).
- When a thread is terminated by sending `SIGTERM` via `pthread_kill`, it kills the whole process - use a different mechanism or signal (POS44-C, `cert-pos44-c`).
- When `pthread_setcanceltype` sets `PTHREAD_CANCEL_ASYNCHRONOUS`, switch to `PTHREAD_CANCEL_DEFERRED`; async cancellation can interrupt at an unsafe point (POS47-C, `cert-pos47-c`).

### Security-Sensitive API

- When `system()` or `popen()`/`_popen()` runs a command processor (with a non-null command), replace it with a direct exec API that does not invoke a shell - it is a command-injection vector (ENV33-C, `cert-env33-c`).
- When a deprecated or non-bounds-checked C function (`strcpy`, `strcat`, `sprintf`, `gets`, `asctime`, ...) is used, replace it with its bounds-checked Annex K variant or a safe alternative and check the result (MSC24-C/MSC33-C, `cert-msc24-c`/`cert-msc33-c`).
- When `std::rand()`/`rand()` is used to generate pseudorandom numbers, use a `<random>` engine with proper distribution; `rand` has poor statistical quality and is unsuitable for security (MSC50-CPP/MSC30-C, `cert-msc50-cpp`/`cert-msc30-c`).
- When a random-number engine is default-constructed, seeded with a constant, or left unseeded, seed it from a non-deterministic source (e.g. `std::random_device`) (MSC51-CPP/MSC32-C, `cert-msc51-cpp`/`cert-msc32-c`).

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

- Condition waits are wrapped in predicate-checking loops.
- Signal handlers are async-safe, plain C-linkage, and free of C++-only constructs (for the applicable standard); threads are not terminated with `SIGTERM`; cancellation type is deferred, not asynchronous.

### Security-Sensitive API

- No `system()`/`popen()` command-processor calls; deprecated/unsafe C functions are replaced with bounds-checked alternatives and checked.
- Pseudorandom numbers use `<random>` with a properly seeded engine, not `std::rand` or an unseeded/constant-seeded generator.

### Suppressions And Tests

- Every downgraded or suppressed CERT finding has a documented, rule-specific justification.
- Each fixed violation has a regression test or static-analysis assertion that fails without the fix where one is feasible.

## Severity And Verdicts

Severity reflects the CERT risk class and exploitability/UB reachability, not just pattern presence.

- `CRITICAL`: a reachable violation that is undefined behavior or a direct security vulnerability in normal operation (command injection via `system()`, `longjmp` skipping destructors on a live path, `memcpy` over a polymorphic object, pointer arithmetic on a polymorphic pointer with differing dynamic type, signal handler calling non-async-safe functions).
- `HIGH`: a violation that is UB or a security weakness but requires a specific input, error path, or platform to manifest (unchecked allocation/return value on an error path, throwing exception copy constructor, over-aligned `operator new`, unseeded RNG used for a security decision, unsafe string function with attacker-influenced length).
- `MEDIUM`: a latent or context-bounded violation (self-assignment unguarded on a class that is unlikely to self-assign today, `signed char` widening on ASCII-only data, `std::rand` for non-security randomness) that future edits or inputs will amplify.
- `LOW`: a hardening or hygiene issue (reserved-identifier naming, throw-by-value/catch-by-reference style where copies are cheap) with no current UB or security path.

Verdicts:

- `BLOCK`: missing required context, any `CRITICAL`, or any unmitigated `HIGH`.
- `CONCERNS`: remaining `HIGH`/`MEDIUM` findings each have a documented exception, compensating control, or bounded reachability.
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

- Unchecked return: `malloc(n); /* never tested */` ignores a NULL-on-failure result, risking a null dereference. Check the result before use, or cast to `void` only if the allocation is provably unnecessary. (ERR33-C.)
- Raw memcpy on a non-trivial type: `std::memcpy(&dst, &src, sizeof(Widget));` where `Widget` has a `std::string` member corrupts the destination. Use copy assignment `dst = src;`. (OOP57-CPP.)
- Throwing exception copy: an exception class with a `std::string` member copied by a throwing allocation can call `std::terminate` mid-propagation. Make the copy constructor `noexcept` (store the message in a `shared_ptr<const std::string>`). (ERR60-CPP.)
- Command injection: `system(user_supplied)` runs a shell. Replace with `posix_spawn`/`exec*` and an argument vector, no shell. (ENV33-C.)
- Polymorphic pointer arithmetic: `Base* b = derived_array; b += 1;` strides by `sizeof(Base)`, not the dynamic type, giving UB. Iterate as the concrete `Derived` type. (CTR56-CPP.)

## Definition Of Done

A CERT-related change is ready only when:

- Every detected violation is fixed to the compliant construct or carries a documented, rule-specific exception with residual risk recorded.
- No standard-library error path is left unchecked, no exception can escape before `main` or throw during copy while propagating, and no banned API (`system`, unsafe C functions, `std::rand` for security, `setjmp`/`longjmp`) remains without justification.
- Special members defend against self-assignment and do not mutate their source; no raw byte operations run on non-trivial types; no pointer arithmetic crosses a polymorphic boundary.
- Signal handlers, thread termination, and cancellation comply with the applicable CERT concurrency rules for the target's language standard.
- Fixed violations have regression tests or static-analysis assertions where feasible; if none were feasible, the Suppressions and tests item is n/a and does not block `CLEAN`.
- Any CERT rule requiring analysis beyond clang-tidy's reach, or any cross-skill lifetime/concurrency question, is named and routed rather than assumed compliant.
