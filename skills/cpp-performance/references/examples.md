When to read: when an applicable finding needs a short illustration. These are partial C++ illustrations, not runnable programs; the core decision rules and safety constraints govern each transformation.

## Examples

- Expensive value parameter: `void store(std::string s) { m_name = s; }` copies an lvalue argument into `s`, then copies `s` into the member. If the member assignment is the only use of `s`, keep by value and move into the member; if the function only reads `s`, take `const std::string&`. (`performance-unnecessary-value-param`.)
- Const blocks return move: `const std::vector<int> v = build(); return v;` cannot implicitly move from `v` if copy elision does not occur. Removing `const` allows that fallback move; it does not guarantee an executed move. (`performance-no-automatic-move`.)
- Missing reserve: `for (int i = 0; i < n; ++i) out.push_back(f(i));` reallocates repeatedly. Add `out.reserve(n);` before the loop. (`performance-inefficient-vector-operation`.)
- Pointless move: `const std::string s; sink(std::move(s));` cannot move a `const`; the `std::move` is misleading and a silent copy still happens. Remove it only when overload resolution is unchanged. (`performance-move-const-arg`.)
- Missing noexcept: a potentially throwing `Widget(Widget&&)` may cause `std::vector<Widget>` to choose copying during growth when copying is available. Mark the move `noexcept` only if its operations cannot throw. (`performance-noexcept-move-constructor`.)
