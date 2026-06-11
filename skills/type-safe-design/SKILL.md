---
name: type-safe-design
description: 'Use when: designing, reviewing, refactoring, or test-planning type-safe architecture, compiler-enforced contracts, validation-as-types, explicit interfaces, generic misuse, reflection boundaries, polymorphic factories, closure-based extension, SOLID change complexity, or change-locality risks.'
argument-hint: 'Describe the design, code, refactor, or review target where type safety and change locality matter.'
user-invocable: true
---
# Type-Safe Design

Use this skill when a task needs architecture that makes invalid states hard to express, keeps change localized, and lets the compiler or a narrow runtime boundary enforce contracts.

## Routing

- Use this skill for architecture, design review, refactoring, and test-planning tasks where type-level contracts, validation states, generic boundaries, runtime metadata, factories, or change-locality risks are central to the answer.
- Prefer a language- or framework-specific skill when the hard part is syntax, library mechanics, build errors, runtime debugging, or framework convention rather than contract design.
- Prefer security, filesystem, auth-claim, SSRF, dependency, or web-app review skills when the primary risk is a specialized security contract; use this skill only for the type-safety portion of that review.
- Do not use this skill for routine type errors, generic style advice, or broad architecture critique that does not involve enforceable contracts or change-locality behavior.

## Read This First

- Treat type safety as a design discipline, not as a request to add more generic parameters. The goal is to encode intent, validity, construction rules, and behavior contracts where the language and tests can check them.
- Start from change behavior: ask how many isolated edits a future feature, subtype, validation rule, or API change will require as the system grows.
- Prefer explicit contracts over undocumented assumptions. A function signature that accepts a broad type but assumes a validated, authenticated, readable, serializable, or behavior-capable subset is lying.
- Keep generated flexibility below the domain layer. Generics, reflection, registries, and factories can be excellent infrastructure tools, but they should not obscure business behavior.
- Stop and ask when the target language, runtime, or codebase constraints are unknown and the recommendation depends on features such as sealed types, runtime metadata, macros, dependency injection, or reflection.
- Stop and ask when the user asks to "make this type safe" but does not provide the current contract boundary, allowed language/runtime features, or the kind of invalid state the design must prevent.

## Workflow

1. Classify the task mode: design, implementation, review, refactor planning, debugging, or test planning.
2. Map the contract boundary. Identify raw inputs, validated/domain values, public interfaces, construction paths, subtype/factory registration, and runtime type checks.
3. Estimate change complexity. For the proposed change, name whether future edits look closer to `O(1)`, `O(k)`, `O(n)`, or worse across modules, clients, subtypes, and cases.
4. Look for structural smells: rigidity, fragility, immobility, viscosity, hidden validation assumptions, generic-heavy signatures, public API pollution, central type switches, unsafe casts, or reflection that bypasses checks.
5. Choose the smallest contract mechanism that makes the assumption enforceable: refined/wrapper type, smart constructor, explicit interface, role-specific protocol, strategy/decorator/adapter, chain of responsibility, factory, enum registry, closure carrier, or constrained reflection boundary.
6. Preserve dependency direction. Stable core code should depend on stable abstractions, not ad hoc client logic or low-level implementation details.
7. Plan verification where the contract lives: compile-time failures, constructor/factory tests, boundary validation tests, substitution tests, registration completeness tests, and regression tests for change-locality risks.
8. For broad refactors, think globally and act locally: define the target architecture first, then use compiler errors as a work queue instead of trying to keep every affected file mentally loaded.

## Decision Rules

- When data can be raw or trusted, model the trusted state as a separate type. Validate at the boundary through a factory, parser, smart constructor, or refinement step, then let downstream functions accept only the trusted type.
- When a function accepts `T` but depends on behavior, replace the bare generic with a behavioral interface or protocol. Generics generalize data; interfaces generalize behavior.
- Use generics for collections, containers, low-level utilities, DI/serialization/query infrastructure, and closed internal contexts where behavior is irrelevant or separately constrained.
- Avoid generic-heavy domain APIs when type parameters become a substitute for modeling. If readers cannot describe what the abstraction does without reciting its type parameters, introduce named domain contracts.
- When a new behavior requires editing central generic code, runtime type checks, or many clients, prefer OCP-friendly composition such as Strategy, Decorator, Adapter, or a role-specific interface.
- When the case set is closed and data-centric, such as protocol tags or binary deserialization, an enum plus fixed registry or static constructor table can be appropriate. Add completeness checks and fail fast on missing registration or constructor signatures.
- Use reflection only as a disciplined bridge from untyped runtime data into typed structures. Keep it at boundaries, validate against metadata or generated schemas, cache expensive lookups, and never let reflective access become an unchecked backdoor.
- For one-off access to internals, do not add broad getters or pollute public interfaces. Prefer a scoped operation. If a raw closure would invert dependency direction, wrap it in a small, stable action interface or closure carrier.
- For action systems such as abilities, commands, or interactions with reusable preconditions and deferred execution, separate precondition checks from execution requests. Compose reusable checkers, place execution in a terminal step, and keep metadata/composition separate from validation and execution logic.
- Treat access modifiers as low-level guardrails. When different clients need different views of the same object, explicit interfaces and factories usually communicate roles better than relying only on `private`, `protected`, or casts.
- Accept a temporary uncompilable state only during an intentional refactor with a known target shape, frequent builds, and tests ready at the boundaries that matter.

## Checklists

### Design Checklist

- Public signatures state the real preconditions through types, interfaces, or named factories.
- Raw, partially validated, and trusted domain values cannot be confused accidentally.
- Behavioral variation is expressed through contracts or composition, not broad generics plus conditionals.
- Generic abstractions stay in infrastructure or genuinely behavior-free containers.
- Reflection, deserialization, or dynamic data handling is isolated behind a typed boundary.
- New subtypes, cases, or features do not require edits across unrelated clients.
- Public APIs are not expanded for one-off access to private implementation details.
- Constructor, factory, registry, and serialization paths have completeness and failure-mode tests.

### Review Checklist

- Search for broad inputs with hidden assumptions: `Any`, `Object`, bare `T`, base classes, raw `File`, raw request DTOs, or unvalidated maps.
- Check LSP: does a method claim to accept a parent/interface while requiring a specific subtype or validity state?
- Check OCP: can new behavior be added by implementing a contract, or must existing central logic be edited?
- Check DIP: do high-level modules depend on low-level details, concrete `T`, reflection output, or client-provided callbacks?
- Check ISP/SRP: are clients forced to depend on interface members or responsibilities they do not need?
- Check viscosity: is the clean change more expensive than a shortcut such as copy-paste, casting, or another conditional branch?
- Check tests: would a missing validation step, missing subtype registration, or malformed runtime payload fail near the boundary?

## Output Format

For design or implementation advice, provide:

1. Current contract risk.
2. Recommended contract shape.
3. Change-locality impact.
4. Verification plan.

For reviews, lead with findings ordered by severity. Use this rubric:

- `high`: likely invalid states, data corruption, security/privacy exposure, production breakage, or broad `O(n)`/worse change cascades.
- `medium`: meaningful maintainability, testability, substitution, or public-contract risk that can become expensive as the system grows.
- `low`: localized clarity, naming, or modeling issue with limited current blast radius.

Finding format:

```text
Severity: high|medium|low
Evidence: <code, design note, or observed behavior>
Rule: <contract or change-locality rule violated>
Risk: <failure mode or scaling cost>
Recommendation: <smallest enforceable contract change>
Verification: <test, compiler check, or review evidence>
```

If there are no material issues, say `No material findings` and list residual risks, assumptions, and validation gaps instead of inventing findings.

## Examples

- Raw input boundary: replace `process(User)` plus defensive checks with `ValidatedUser` created by `ValidatedUser.tryCreate(rawUser)`; downstream code accepts `ValidatedUser` only.
- Generic behavior smell: replace `render<T>(item)` with `render(Renderable item)` when rendering behavior is required.
- Internal access exception: replace `getCache()` with `perform(CacheAction<R>)` when a narrow, controlled operation on private state is needed.
- Closed deserialization set: use `MessageType` plus a fixed constructor registry and tests that every enum value has a parser.

## Reference Files

- Use [source map](./references/source-map.md) for provenance from the source book and concept-to-line mapping.

## Quality Rules

- Optimize for enforceable contracts, not aesthetic purity.
- Prefer one named domain type or interface over a paragraph of documentation explaining an assumption.
- Do not recommend generics, reflection, closures, or factories without naming their boundary and failure path.
- Keep tradeoffs explicit: some prototypes should favor delivery speed, while long-lived or multi-team systems need stronger structural guarantees.
- When evidence is incomplete, report the missing language/runtime/codebase facts before choosing a pattern.