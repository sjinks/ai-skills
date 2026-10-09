When to read: when the target includes value passing, copies, moves, returns, special members, or noexcept decisions. The core Checklist remains the gating source; apply the core behavior-preservation constraint to every candidate.

# Copy and Move Explanations

### Copies (Parameters, Locals, Loops)

- When a function takes an expensive-to-copy type by value:
  - If the parameter is only read, pass it by `const&` (`performance-unnecessary-value-param`).
  - If the parameter is copied or assigned exactly once into longer-lived storage, keep it by value and `std::move` it into the sink (sink-parameter idiom) rather than passing `const&` and copying inside.
- When a local is copy-initialized from a `const&`-returning expression and used only as const, bind it as `const&` instead of copying (`performance-unnecessary-copy-initialization`). This is conditional on the reference not dangling: if a later mutation, `erase`, or scope exit can invalidate the source before the last use, the copy is required - flag the lifetime dependency as out-of-scope object-lifetime work and route it.
- When a range-for loop variable of expensive-to-copy type is used only as const, declare it `const&` (`performance-for-range-copy`).
- When a range-for loop variable's written type does not match the iterator's value type, an implicit per-iteration conversion copies; use `const auto&` so no conversion occurs (`performance-implicit-conversion-in-loop`).

### Moves And Returns

- When `std::move` produces no move, it is misleading and should usually be removed (`performance-move-const-arg`) - but confirm the removal does not change overload resolution (dropping `std::move` turns an rvalue into an lvalue, which can re-select a `const&` overload instead of a `T&&` one); remove it only when the selected overload is unchanged. It produces no move in each of these cases:
  - the argument is a `const` object (a move silently falls back to a copy);
  - the argument is a trivially-copyable type (move and copy are equivalent, so the `std::move` buys nothing);
  - the result is bound to a `const&` parameter (the rvalue cannot bind to a non-const sink, so no move occurs).
- When a local is copy-assigned out (e.g. `out = some;`) and is dead afterward, `std::move` it into the assignment to turn a copy into a move (no dedicated clang-tidy check; `bugprone-use-after-move` guards against doing this while the local is still read afterward).
- When returning a local lvalue eligible for the implicit move-on-return, do not declare it `const`: `const` blocks the automatic move when copy elision does not occur (`performance-no-automatic-move`). Return a non-const local; do not add an explicit `std::move` on a plain local return (that defeats copy elision).
- When a move constructor's mem-initializer list initializes a base or member, move it, not copy it; a missing `std::move` there silently copies (`performance-move-constructor-init`).

### noexcept And Special Members

- If a move constructor or move assignment cannot throw, mark it `noexcept`. If it can throw, retain an accurate exception specification and record the cost tradeoff; do not change throwing behavior merely to satisfy a diagnostic. Containers may choose copying when a move can throw ([performance-noexcept-move-constructor](https://clang.llvm.org/extra/clang-tidy/checks/performance/noexcept-move-constructor.html)).
- If a user-defined `swap` or `iter_swap` cannot throw, mark it `noexcept`; otherwise retain an accurate exception specification. A non-throwing swap can enable optimizations, but a diagnostic is not proof that adding the specification is safe ([performance-noexcept-swap](https://clang.llvm.org/extra/clang-tidy/checks/performance/noexcept-swap.html)).
- Inspect `performance-noexcept-destructor` diagnostics against actual destructor behavior. Preserve an accurate exception specification; do not promise non-throwing destruction without proving it.
- When an out-of-line defaulted destructor (`A::~A() = default;`) makes an otherwise trivially-destructible type non-trivial, remove the declaration so the type stays trivially destructible (`performance-trivially-destructible`).
