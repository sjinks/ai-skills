# type-safe-design

> Use when: designing, reviewing, refactoring, or test-planning type-safe architecture, compiler-enforced contracts, validation-as-types, explicit interfaces, generic misuse, reflection boundaries, polymorphic factories, closure-based extension, SOLID change complexity, or change-locality risks.

This skill is aimed at architecture and code changes where correctness should be enforced through contracts, types, compiler feedback, or narrow runtime boundaries instead of scattered discipline and defensive checks.

Source material: [Type-Safe by Design: Explorations in Software Architecture and Expressiveness](https://github.com/SanQri/safe-by-design/blob/a6b7aa22160c2ee3d461df064c0161e87e6a7087/book.pdf) by Mykola Haliullin.

It helps an assistant:

- review change-locality risks using Big O-style reasoning for rigidity, fragility, immobility, and viscosity
- model raw, validated, trusted, authenticated, readable, serialized, or behavior-capable states as explicit contracts
- decide when generics are appropriate infrastructure tools and when behavior needs named interfaces or protocols
- evaluate reflection, deserialization, polymorphic factories, enum registries, and constructor contracts as constrained boundaries
- avoid public API pollution for one-off internal access by using scoped operations or dedicated closure-carrier abstractions
- plan compiler-guided refactors and verification through boundary tests, substitution tests, completeness checks, and fail-fast construction paths

## Files

- [`SKILL.md`](SKILL.md) — the full skill definition.
- [`references/`](references/) — extended workflow and reference material.
