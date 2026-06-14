# cmake-build-review

> Use when: reviewing, designing, or refactoring CMake build configuration, CMakeLists.txt, target-based usage requirements, PUBLIC PRIVATE INTERFACE propagation, find_package vs FetchContent dependency policy, toolchain files, presets, generator expressions, install and package config files, sanitizer or LTO or warning configurations, or cross-platform build correctness.

This skill is aimed at CMake build configuration where target structure, usage-requirement propagation, dependency sourcing, and install/export correctness determine whether builders and consumers get a working, maintainable build.

It helps an assistant:

- derive PUBLIC/PRIVATE/INTERFACE visibility from the header surface and catch over-linking and propagation leaks
- replace directory-scoped commands and global flag mutation with target-based equivalents
- consume dependencies as imported targets under an explicit find_package/FetchContent policy with version constraints
- review install/export setups: export sets, config and version files, BUILD_INTERFACE/INSTALL_INTERFACE include paths
- keep configuration logic multi-config-safe with generator expressions and make sanitizers/LTO/warnings opt-in, per-target, compile-and-link consistent
- return `BLOCK`, `CONCERNS`, or `CLEAN` with project shape, findings, checklist status, verification expectations, and an insufficient-context template

## Files

- [`SKILL.md`](SKILL.md) — the full skill definition.
