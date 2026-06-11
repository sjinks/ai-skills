---
name: cmake-build-review
description: "Use when: reviewing, designing, or refactoring CMake build configuration, CMakeLists.txt, target-based usage requirements, PUBLIC PRIVATE INTERFACE propagation, find_package vs FetchContent dependency policy, toolchain files, presets, generator expressions, install and package config files, sanitizer or LTO or warning configurations, or cross-platform build correctness."
argument-hint: "Describe the CMakeLists, build issue, dependency policy, target structure, or configuration under review."
user-invocable: true
---

# CMake Build Review

Use this skill when CMake code defines, links, installs, or configures targets and the question is whether the build is correct, propagates usage requirements properly, and stays maintainable across platforms, configurations, and dependency sources.

The goal is a target-centric build: every target declares its own requirements with correct visibility, consumes dependencies through imported targets, and nothing relies on directory-scoped global state.

**UTILITY SKILL.** INVOKES: read-only file access for supplied targets; no other tools or skills. FOR SINGLE OPERATIONS: use for focused CMakeLists review, target/visibility analysis, dependency-policy decisions, or install/package design.

## Scope

- Use this skill for target-based CMake: `target_link_libraries` visibility (`PUBLIC`/`PRIVATE`/`INTERFACE`), transitive usage requirements, include directories, compile definitions/options/features, generator expressions, imported and alias targets, `find_package` vs `FetchContent` policy, toolchain files and presets, install rules and package config files, and build-type/sanitizer/LTO/warning configuration.
- Apply it to CMakeLists diffs, new project skeletons, dependency-source migrations, install/export design, and "why does my consumer not inherit X" questions.
- Treat directory-scoped commands (`include_directories`, `link_libraries`, `add_definitions`, global `CMAKE_CXX_FLAGS` edits) in new code as findings with target-based replacements.

## DO NOT USE FOR:

- C++ source-level review (lifetime, concurrency, API design); compiler/linker bug diagnosis; package-manager-specific lockfile mechanics (Conan/vcpkg internals) beyond their CMake integration points.
- CI pipeline structure (stages, caching, runners) where CMake invocation is incidental.

## Required Context

Collect or infer before judging:

- Target: CMakeLists files, diff, or design under review, and the minimum CMake version in force.
- Project shape: library/executable targets, whether libraries are installed/exported for external consumers, static/shared policy.
- Dependency policy: system packages, `find_package` with config or module mode, `FetchContent`, vendored sources, or a package manager.
- Platforms and toolchains in scope (single Linux toolchain vs multi-platform), and which configurations matter (Debug/Release/multi-config generators).
- Consumers: same-build subdirectories only, or external projects via `find_package`.

If the target cannot be established, return `Verdict: BLOCK` with one open question; do not guess. When the target is supplied but policy items (dependency source, install intent, platforms) are unstated, analyze policy-independent findings normally, mark those fields `undeclared`, and record policy-dependent recommendations as open questions instead of guessing.

## Output Depth

Default to `standard`. `quick` still reports missing required context, blockers, unmitigated HIGH/CRITICAL findings, and target-specific concerns; it only omits non-applicable checklist expansion. `standard` covers the applicable checklist with concise evidence. `exhaustive` enumerates the full checklist only when asked or when the risk surface warrants it. Whenever the selected depth is `quick` or `exhaustive` — whether user-requested or risk-selected — state it on a `Depth:` line directly after `Target:` in the report.

## Workflow

1. Map the targets: what is built, what links what, and with which visibility.
2. Verify visibility semantics: `PRIVATE` for build-only needs, `INTERFACE` for header-only consumer needs, `PUBLIC` only when both apply; misdeclared visibility is the root of most propagation bugs.
3. Check global-state usage: directory-scoped commands, `CMAKE_<LANG>_FLAGS` mutation, cache-variable abuse, and order-dependent `include()` side effects.
4. Check dependency consumption: imported targets (`Foo::Foo`) rather than raw paths/variables; consistent policy between `find_package` and `FetchContent`; version constraints stated.
5. Check install/export correctness when the project is consumed externally: install targets with export sets, generated config/version files, `BUILD_INTERFACE`/`INSTALL_INTERFACE` generator expressions on include paths.
6. Check configuration hygiene: warnings/sanitizers/LTO applied per-target or via toolchain/presets, not hardcoded globally; multi-config generators not broken by `CMAKE_BUILD_TYPE`-only logic.
7. Classify findings by severity, map to a verdict, and state the verification each change needs (clean configure on a fresh build dir, consumer link test, preset matrix).

## Decision Rules

The Checklist below is the gating source of truth when these rules overlap; the rules explain rationale.

- When choosing visibility for `target_link_libraries` or `target_include_directories`, derive it from the header surface: if the dependency appears in the target's public headers, it is `PUBLIC` (or `INTERFACE` for header-only targets); if only in sources, `PRIVATE`. Defaulting everything to `PUBLIC` leaks flags and creates over-linking; defaulting to `PRIVATE` breaks consumers.
- When a CMakeLists in new code uses `include_directories`, `link_libraries`, `add_definitions`, `add_compile_options` at directory scope, or appends to `CMAKE_CXX_FLAGS`, replace it with the `target_*` equivalent on the narrowest target; directory scope applies to unrelated targets added later and does not propagate to consumers.
- When consuming a dependency, link the imported target (`OpenSSL::SSL`, `fmt::fmt`), never `${FOO_LIBRARIES}`/`${FOO_INCLUDE_DIRS}` variables when a target exists: imported targets carry usage requirements (includes, definitions, transitive deps) that variables drop.
- When both `find_package` and `FetchContent` are plausible, write the policy down: prefer `find_package` (config mode) for system/packaged deps and reproducible environments; use `FetchContent` for tightly version-pinned source builds; declaring with `FetchContent_Declare(... FIND_PACKAGE_ARGS ...)` or `OVERRIDE_FIND_PACKAGE` (both CMake 3.24+, mutually exclusive on one declaration) can bridge both. Mixing per-dependency without a rule causes ODR and diamond-version conflicts.
- When a library is installed for external consumers, install the targets with an export set, generate `<Pkg>Config.cmake` (or `configure_package_config_file`) plus a version file, and wrap public include paths in `$<BUILD_INTERFACE:...>`/`$<INSTALL_INTERFACE:...>`; absolute build-tree paths leaking into the export are a finding.
- When warnings are configured, put `-Wall -Wextra -Werror`-class flags on project targets via a helper (interface target or function), never force them on consumers via `PUBLIC`/`INTERFACE` options or global flags; `-Werror` exported to consumers breaks their builds on compiler upgrades.
- When sanitizers, coverage, or LTO are configured, make them togglable options applied per-target or via presets/toolchains; sanitizer flags must apply to both compile and link, and mixing sanitized/unsanitized static libraries is a finding. Prefer `CMAKE_INTERPROCEDURAL_OPTIMIZATION` (with `check_ipo_supported`) over raw `-flto` flags.
- When logic branches on `CMAKE_BUILD_TYPE`, it breaks multi-config generators (Visual Studio, Xcode, Ninja Multi-Config); use generator expressions (`$<CONFIG:Debug>`) or per-config properties instead.
- When `option()`/cache variables gate features, remember values persist in the cache: changed defaults do not apply to existing build dirs, and dependent options need `cmake_dependent_option` or explicit validation.
- When custom commands/targets generate sources, declare `BYPRODUCTS`/`OUTPUT` correctly and wire dependencies through `add_dependencies` or output-level dependencies, not configure-time file existence checks; configure-time generation (`execute_process`) should be reserved for information gathering, not artifact builds.
- When the minimum CMake version is declared, it must actually match the features used (presets, `FetchContent` arguments, generator expressions); a too-low `cmake_minimum_required` fails on the machines it claims to support, and versions below the tested floor silently change policy behavior.

## Checklist

### Targets And Visibility

- Every buildable unit is a target; no directory-scoped include/link/definition commands in new code.
- Visibility on every `target_*` call matches the header-surface rule (PRIVATE build-only, INTERFACE header-only, PUBLIC both).
- No `-Werror`-class or project-style flags exported to consumers via PUBLIC/INTERFACE.

### Dependencies

- All dependencies are consumed as imported/namespaced targets; no raw `*_LIBRARIES`/`*_INCLUDE_DIRS` variables where targets exist.
- The find_package/FetchContent policy is explicit and consistent; version constraints are stated; no same-dependency-two-sources conflicts.
- No reliance on flag or variable leakage into or out of FetchContent'd projects: `FetchContent_MakeAvailable` uses `add_subdirectory`, so parent directory properties and flags do inherit — treat that as a hazard to control, not isolation to assume.

### Install And Export

- Installed libraries export their targets with namespaced names and generate config + version files consumable by `find_package`.
- The installed config file calls `find_dependency()` for every dependency in the exported targets' link interface (PUBLIC or INTERFACE), so consumers resolve the transitive closure.
- Public include paths use BUILD_INTERFACE/INSTALL_INTERFACE; no build-tree absolute paths in the install export.
- Install rules cover everything a consumer needs (headers, targets, config files) and nothing internal.

### Configuration And Toolchains

- Build-type logic works on multi-config generators (generator expressions, not CMAKE_BUILD_TYPE branches).
- Sanitizers/coverage/LTO are opt-in, applied to compile and link consistently, per-target or via presets/toolchains.
- `POSITION_INDEPENDENT_CODE` is set where static libraries link into shared libraries; PIC mismatches are findings.
- `cmake_minimum_required` matches the features used, and policy-sensitive behavior does not depend on unstated defaults.

### Reproducibility

- A fresh build directory configures cleanly with documented options; no reliance on stale cache values or in-source builds.
- Generated files declare their outputs and dependencies; no configure-time artifact builds.
- Cache options have sane defaults and validation; toggling documented options does not require manual cache surgery.

### Tests

- Build-system fixes have verification: a fresh-configure run, a consumer `find_package` link test for export changes, or a preset/config matrix run, as applicable. If no build-system fixes are in scope, this item is n/a.

## Severity And Verdicts

- `CRITICAL`: a correctness break for consumers or builders — wrong visibility that produces ODR/flag conflicts, broken install exports (absolute paths, missing files), same-dependency-two-versions in one binary, or sanitizer flag mismatch across linked static libraries.
- `HIGH`: propagation bugs awaiting a consumer (misdeclared visibility on an exported target), multi-config-breaking logic in a project that claims multi-config support, or forced `-Werror`/style flags on consumers.
- `MEDIUM`: directory-scoped commands in new code, raw variable consumption where targets exist, undeclared dependency policy, cache-option hygiene gaps, or a verification gap on a risky change.
- `LOW`: style, naming, redundant code, or hardening with no current incorrect behavior.

Verdicts:

- `BLOCK`: the target cannot be established, any `CRITICAL`, or any unmitigated `HIGH`. Other missing Required Context items become open-question findings, not automatic blocks.
- `CONCERNS`: any unmitigated `MEDIUM`, or remaining `HIGH`/`MEDIUM` findings that each have a compensating control, accepted tradeoff, or bounded reachability.
- `CLEAN`: every applicable checklist item holds; `LOW`-only findings do not block `CLEAN` and are listed as findings. If no build-system fixes are in scope, Tests is n/a and does not block `CLEAN`. For design-stage targets with no CMake code yet, the best achievable verdict is `CONCERNS` with verification expectations recorded per finding.

## Output Format

```text
Verdict: BLOCK | CONCERNS | CLEAN
Target: <CMakeLists files, diff, or design>
Depth: <quick | exhaustive; include this line whenever the selected depth is not standard>
Project shape: <targets, install/export intent, static/shared, or undeclared>
Dependency policy: <find_package | FetchContent | package-manager | mixed-with-rule | vendored | undeclared>

Findings:
1. <short title>
  Severity: CRITICAL | HIGH | MEDIUM | LOW
  Classification: Confirmed issue | Likely risk | Open question | Accepted tradeoff | Test gap
  Evidence: <file:line, diff hunk, or design sentence>
  Rule: <targets-visibility | dependencies | install-export | configuration | reproducibility | tests>
  Risk: <what breaks, for whom (builder or consumer), and when>
  Required guard: <target-based or policy change>
  Test expectation: <fresh configure, consumer link test, preset matrix, or N/A>

Checklist status:
- Targets and visibility: covered | missing | n/a
- Dependencies: covered | missing | n/a
- Install and export: covered | missing | n/a
- Configuration and toolchains: covered | missing | n/a
- Reproducibility: covered | missing | n/a
- Tests: covered | missing | n/a

Residual risk: <remaining caveats or None>
```

`Rule:` values map to checklist sections as follows: `targets-visibility` -> Targets And Visibility; `dependencies` -> Dependencies; `install-export` -> Install And Export; `configuration` -> Configuration And Toolchains; `reproducibility` -> Reproducibility; `tests` -> Tests.

When no material issues exist, write exactly `Findings: None` (allowed only with `CLEAN`) and list assumptions under Residual risk. For design-stage targets that earn `CONCERNS` solely because verification cannot exist yet, emit one `Test gap` finding with `Rule: tests` listing the required verification instead of an empty findings list.

Insufficient-context mode: when the target itself cannot be established, emit exactly this reduced template and stop; do not emit project shape, dependency policy, or checklist status with guessed values (unstated policy items with a supplied target follow the undeclared rule in Required Context instead). The `BLOCK` verdict here is triggered by the missing target, not by the finding's `LOW` severity — the LOW-only-findings-are-CLEAN rule does not apply in this mode:

```text
Verdict: BLOCK
Target: <CMakeLists files, diff, or design>

Findings:
1. <missing-context short title>
  Severity: LOW
  Classification: Open question
  Evidence: <which required context is missing>
  Rule: <targets-visibility | dependencies | install-export | configuration | reproducibility | tests>
  Risk: <why no safe conclusion is possible>
  Required guard: <what context must be supplied>
  Test expectation: N/A
```

## Examples

- Visibility leak: `target_link_libraries(core PUBLIC OpenSSL::SSL)` when OpenSSL appears only in `core`'s `.cpp` files forces every consumer to link OpenSSL and inherit its include paths. Fix: `PRIVATE`.
- Broken export: `target_include_directories(widget PUBLIC ${CMAKE_CURRENT_SOURCE_DIR}/include)` on an installed target bakes the build-tree path into `widgetTargets.cmake`. Fix: `PUBLIC $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/include> $<INSTALL_INTERFACE:include>`.
- Multi-config break: `if(CMAKE_BUILD_TYPE STREQUAL "Debug") target_compile_definitions(app PRIVATE VERBOSE_LOG)` does nothing under Ninja Multi-Config or Visual Studio. Fix: `target_compile_definitions(app PRIVATE $<$<CONFIG:Debug>:VERBOSE_LOG>)`.

## Definition Of Done

A CMake change is ready only when:

- Every new requirement is declared on a target with header-surface-derived visibility (per Targets And Visibility).
- Dependencies are consumed as imported targets under a stated policy (per Dependencies).
- Export/install changes satisfy their checklist section and pass a consumer link test.
- Configuration logic survives multi-config generators and toolchain swaps (per Configuration And Toolchains).
- Verification per the Tests item is recorded for risky changes.
