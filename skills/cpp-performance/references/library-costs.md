When to read: when the target includes container, string, algorithm, layout, callable, or related library costs. The core Checklist remains the gating source; apply the core behavior-preservation constraint to every candidate.

# Library Cost Explanations

### Containers, Strings, Algorithms

- When elements are appended to a `std::vector` (or vector-like type) inside a counted or range-based loop with a known final size, call `reserve` before the loop to avoid repeated reallocation (`performance-inefficient-vector-operation`).
- When building a string, prefer `+=`/`append` over chained `operator+` (which materializes temporaries), especially inside loops (`performance-inefficient-string-concatenation`).
- When passing a single-character string literal to `find`/`rfind`/`starts_with`/`ends_with`/`contains`/`operator+=` and friends, use a `char` literal instead of a length-1 string literal (`performance-faster-string-find`).
- When calling an STL algorithm (`std::find`, `std::count`, `std::lower_bound`, etc.) on an associative container that provides an equivalent method, call the method - it exploits the container's ordering (`performance-inefficient-algorithm`).
- When emitting a newline to a stream, use `'\n'`; reserve `std::endl` for the rare case where an explicit flush is required (use `std::flush` explicitly), because `std::endl` flushes every time (`performance-avoid-endl`).
- When a `std::string_view` would already satisfy a callee expecting `string_view`, do not wrap it in a temporary `std::string` (or `std::string(sv).c_str()`); pass the view directly. No dedicated `performance-*` check covers this; the redundant-`c_str()` sub-case is `readability-redundant-string-cstr` (cited under Related Checks), and the rest is manual review. The `std::string(sv).c_str()` form is only legitimate when an explicit null-terminated copy is intended.

### Types, Math, Layout

- When calling a C math function (`sin`, `asin`, ...) with a `float` argument, use the `std::` overload (or `*f` variant in C) to avoid an implicit `float`-to-`double` promotion and back (`performance-type-promotion-in-math-fn`).
- When defining an `enum`/`enum class`, choose the smallest fixed-width underlying type that holds the enumerator range to shrink memory footprint and improve cache behavior (`performance-enum-size`) - weighed against ABI stability and readability.
- When casting an integer to a pointer, recognize that provenance is lost and the optimizer is blinded; prefer pointer arithmetic on the original pointer when concealment is accidental (`performance-no-int-to-ptr`).

### Type Erasure And Callables (no clang-tidy check)

- A `std::function` heap-allocates its target unless the target fits the small-buffer **and** satisfies the implementation's small-object criteria, which are implementation- and version-specific. On current libstdc++, for example, the small-object optimization requires the callable to be **trivially copyable**, so a lambda that captures a non-trivial type - notably a `std::shared_ptr` - typically heap-allocates regardless of capture size, and shrinking such a capture below the buffer size does *not* remove the allocation (a common mistaken "fix"). Other standard libraries and future versions may differ, so confirm the behavior on the target toolchain by measuring rather than assuming. To actually avoid the allocation on a hot path, make the captured state trivially copyable (capture a raw pointer / `T*` / `string_view` whose lifetime is separately guaranteed), or avoid `std::function` entirely (a template callable parameter, `function_ref`-style non-owning view, or a hand-written type-erased class with its own inline storage). For example, `std::function<void()> f = [self]{ self->go(); };` (captures `shared_ptr` -> heap) becomes `std::function<void()> f = [raw = self.get()]{ raw->go(); };` (captures a raw pointer -> fits the small buffer, no heap) **only when the target's lifetime is separately guaranteed for the call** (otherwise this trades an allocation for a dangling pointer - an object-lifetime concern to resolve before applying the fix). Verify with an allocation count, not by reading the capture list. No lint check catches this - it requires measurement.
- Per-call `std::function` construction on a hot path (per-request/per-message handlers stored or rebuilt each iteration) multiplies this allocation; hoist a stable callable to a member or pass it by reference rather than reconstructing it.

### Related Checks Outside The performance-* Namespace

These clang-tidy checks live in other namespaces but address the same copy/allocation cost. Apply them, but cite the actual check name (not `performance-*`).

- When a container insertion (`push_back`/`push`/`push_front`) is given an explicitly-constructed temporary of the element type, use the `emplace`-family method and pass the constructor arguments directly, avoiding the temporary's move/copy (`modernize-use-emplace`). Do not transform when the argument is a `new` expression or bit-field (exception-safety / binding rules), matching the check's own exclusions.
- When a constructor takes a `const&` parameter only to copy it into a member, take it by value and `std::move` it into the member, letting callers move from rvalues (`modernize-pass-by-value`). This overlaps the sink-parameter rule under Copies; cite whichever check the reader runs. The transformation is only safe when the parameter is used exactly once and no hidden reference mutates the source before the init-list.
- When `std::remove`/`std::unique`/`std::remove_if` results feed a single-argument `erase`, only one element is removed and the algorithm's wasted shuffle is kept; use the two-argument `erase(first, last)` (erase-remove idiom) (`bugprone-inaccurate-erase`).
- When emptiness is tested with `size()`/`length()`/`std::size() == 0`, use `empty()`; it is O(1) for every container (e.g. `std::list::size` may be O(n) historically) and clearer (`readability-container-size-empty`).
- When membership is tested with `count()` or `find() == end()`, use `contains()` (C++20 associative containers, C++23 strings); `contains` avoids `count`'s extra work on multi-key containers (`readability-container-contains`).
- When `std::string::c_str()`/`data()` is passed to an API that already accepts `std::string`/`string_view`, drop the call to avoid a needless C-string round-trip (`readability-redundant-string-cstr`).
- Struct field ordering that wastes space to padding (hurting cache density) is detectable only by the path-sensitive Clang Static Analyzer (`clang-analyzer-optin.performance.Padding`), not by clang-tidy lint; flag the pattern but recommend running the analyzer rather than asserting a precise layout.
