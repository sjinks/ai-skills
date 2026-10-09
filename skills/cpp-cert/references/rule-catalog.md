When to read: when an applicable Checklist category needs its CERT rule ID, analyzer mapping, standard-dependent qualification, or compliant alternative. The core Checklist remains the gating source; apply the core suppression rule to every finding.

# CERT Rule Catalog

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
- When a type is thrown as an exception, require genuinely non-throwing copy construction: verify member/base copies and the constructor body, and change the representation if necessary before declaring `noexcept`. The specifier alone does not prevent a throwing operation; an exception escaping a non-throwing function or a throwing copy invoked by the exception-handling mechanism while handling an uncaught exception calls `std::terminate` (ERR60-CPP, `cert-err60-cpp`; [exception specifications](https://eel.is/c++draft/except.spec), [exception propagation](https://eel.is/c++draft/except.throw)).
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

- If a condition wait uses neither a predicate-checking loop nor a predicate-taking overload, add a predicate re-check so spurious wakeups cannot proceed past an unmet condition (CON54-CPP/CON36-C, `cert-con54-cpp`/`cert-con36-c`; [analyzer guidance](https://clang.llvm.org/extra/clang-tidy/checks/bugprone/spuriously-wake-up-functions.html)).
- When a signal handler calls non-async-signal-safe functions, uses C++-only constructs, or has non-C linkage, restrict it to async-safe functions and a plain C-linkage POD function (SIG30-C/MSC54-CPP, `cert-sig30-c`/`cert-msc54-cpp`; some C++-specific diagnostics are standard-dependent, so confirm the check's behavior for the target standard rather than assuming it is fully active or fully off).
- When a thread is terminated by sending `SIGTERM` via `pthread_kill`, it kills the whole process - use a different mechanism or signal (POS44-C, `cert-pos44-c`).
- When `pthread_setcanceltype` sets `PTHREAD_CANCEL_ASYNCHRONOUS`, switch to `PTHREAD_CANCEL_DEFERRED`; async cancellation can interrupt at an unsafe point (POS47-C, `cert-pos47-c`).

### Security-Sensitive API

- When `system()` or `popen()`/`_popen()` runs a command processor (with a non-null command), replace it with a direct exec API that does not invoke a shell - it is a command-injection vector (ENV33-C, `cert-env33-c`).
- When a deprecated or non-bounds-checked C function (`strcpy`, `strcat`, `sprintf`, `gets`, `asctime`, ...) is used, replace it with its bounds-checked Annex K variant or a safe alternative and check the result (MSC24-C/MSC33-C, `cert-msc24-c`/`cert-msc33-c`).
- Replace `std::rand()`/`rand()` with a generator and distribution sufficient for the application. For non-security use, a suitable `<random>` engine is an option. For security-sensitive use, require documented security suitability rather than assuming any standard engine is sufficient ([MSC50-CPP](https://cmu-sei.github.io/secure-coding-standards/sei-cert-cpp-coding-standard/rules/miscellaneous-msc/msc50-cpp/), MSC30-C, `cert-msc50-cpp`/`cert-msc30-c`).
- If unpredictability is part of the application contract, replace default, constant, or absent seeds with a source sufficient for that requirement ([MSC51-CPP](https://cmu-sei.github.io/secure-coding-standards/sei-cert-cpp-coding-standard/rules/miscellaneous-msc/msc51-cpp/)/MSC32-C, `cert-msc51-cpp`/`cert-msc32-c`). Preserve intentional fixed seeds in deterministic tests that require reproducibility; document the test-only rationale for any suppression. Do not assume `std::random_device` guarantees nondeterminism on every implementation ([standard limitations](https://eel.is/c++draft/rand.device)).
