# Source Map

Read this file when you need provenance for the Type-Safe Design skill's rules, terminology, and recommended review lenses.

## Source Inventory

- Title: `Type-Safe by Design: Explorations in Software Architecture and Expressiveness`.
- Author: Mykola Haliullin.
- Source permalink: <https://github.com/SanQri/safe-by-design/blob/a6b7aa22160c2ee3d461df064c0161e87e6a7087/book.pdf>
- SHA-256: `779548d53f895d2e29ab2704fbd7c217b3e2914abe0e57ea1013b0f1ed8dca5e`.

## Concept Provenance

| Skill concept | Source location in extracted text | Confidence | Type |
|---|---:|---|---|
| Type-safe design as using language features, abstractions, and architecture to guide behavior and prevent failure | Introduction, lines 16-79 | high | source fact + synthesis |
| Change-locality review with Big O notation for modification effort | `Applying Big O Notation To Software Design`, lines 85-151 | high | source fact |
| Rigidity, fragility, immobility, and viscosity as scaling risks | Lines 154-329 | high | source fact |
| SOLID and design patterns as tools for reducing change complexity | Lines 330-466 | high | source fact + synthesis |
| Limits of asymptotic design analysis for early or exploratory work | Lines 466-493 | high | source fact |
| Validity contracts: separate raw data from valid/trusted subtypes | `What's Wrong with data validation`, lines 511-774 | high | source fact |
| Explicit interfaces as visible, composable access contracts | `Encapsulation Without Private`, lines 774-951 | high | source fact + synthesis |
| Generics belong in low-level utilities and infrastructure; behavior belongs in interfaces | `Why Generics Belong in Infrastructure, Not in Architecture`, lines 952-1522 | high | source fact |
| Ability/action architecture: checker chain, request object, terminal checker, and skill composition | `Designing a Flexible Ability System for Games`, lines 1522-1927 | high | source fact + generalized synthesis |
| Polymorphic construction through enum registries, static arrays, cached constructors, and fail-fast checks | `TYPE-SAFE POLYMORPHIC CONSTRUCTORS...`, lines 1930-2284 | high | source fact + synthesis |
| Closure-based extension without interface pollution, with a dedicated closure carrier to preserve dependency direction | `USING CLOSURES TO EXTEND CLASS BEHAVIOR...`, lines 2325-2767 | high | source fact |
| Reflection as a constrained runtime bridge for untyped external data | `REFLECTION IS NOT THE ENEMY OF TYPE SAFETY`, lines 2767-2939 | high | source fact + synthesis |
| Compiler-guided refactoring: think globally, act locally, and use compiler errors as a map | `The Compiler Is My Co-Author`, lines 2940-3044 | high | source fact + synthesis |

## Interpretation Notes

- The generated skill intentionally generalizes game ability examples into a broader action/command pattern because the source frames the example as reusable for any mechanic where preconditions gate execution.
- The generated skill treats Big O design analysis as a review lens, not as a precise metric, following the source's own limits around exploratory work and unstable system boundaries.
- The generated skill avoids reproducing long examples from the book and keeps examples short and paraphrased for operational use.