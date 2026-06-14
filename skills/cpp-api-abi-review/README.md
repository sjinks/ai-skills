# cpp-api-abi-review

> Use when: reviewing, designing, or evolving C++ library public headers and binary interfaces, including ABI stability, ABI breaks, ODR violations, noexcept contracts, pimpl, inline functions and templates at API boundaries, default arguments vs overloads, extern "C" boundaries, symbol visibility, versioned or inline namespaces, header hygiene, and shared-library compatibility.

This skill is aimed at C++ library boundaries that other code compiles or links against, where the question is which changes break source compatibility, binary compatibility, or behavioral contracts, and how breaks are versioned.

It helps an assistant:

- identify the public/installed surface, the stated compatibility promise, and its toolchain assumptions before classifying any change
- classify changes as API-breaking, ABI-breaking, both, or neither, using accurate layout/vtable/signature rules and the safe-addition cases
- treat inline functions, templates, constexpr variables, and default arguments as compiled-into-consumers, with ODR and mixed-version analysis
- review boundary contracts: noexcept as a one-way promise, exceptions stopped at extern "C", export-macro and visibility discipline
- require a loud break mechanism (soname/major bump, inline-namespace version, symbol versioning) for every break, plus ABI-diff or link-test verification
- return `BLOCK`, `CONCERNS`, or `CLEAN` with the promise, findings, checklist status, verification expectations, and an insufficient-context template

## Files

- [`SKILL.md`](SKILL.md) — the full skill definition.
