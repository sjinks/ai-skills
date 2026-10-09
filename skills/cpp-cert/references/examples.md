When to read: when an applicable finding needs a short illustration. These are partial C++ illustrations, not runnable programs; the core decision rules and safety constraints govern each transformation.

## Examples

- Unchecked return: `void* p = malloc(n); /* used without a failure check */` risks a null dereference if allocation fails and the caller dereferences `p`. Check the result before use; remove an unnecessary allocation instead of discarding its pointer. (ERR33-C.)
- Raw memcpy on a non-trivial type: `std::memcpy(&dst, &src, sizeof(Widget));` where `Widget` has a `std::string` member corrupts the destination. Use copy assignment `dst = src;`. (OOP57-CPP.)
- Throwing exception copy: an exception class with a `std::string` member copied by a throwing allocation can call `std::terminate` mid-propagation. Use a non-throwing copy representation, such as sharing an already-created message through `std::shared_ptr<const std::string>`, before declaring the copy constructor `noexcept`. (ERR60-CPP.)
- Command injection: `system(user_supplied)` runs a shell. Replace with `posix_spawn`/`exec*` and an argument vector, no shell. (ENV33-C.)
- Polymorphic pointer arithmetic: `Base* b = derived_array; b += 1;` strides by `sizeof(Base)`, not the dynamic type, giving UB. Iterate as the concrete `Derived` type. (CTR56-CPP.)
