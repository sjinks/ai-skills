When to read: during every code-quality review or simplification, to select and apply the relevant checks.

# Contextual criteria

Apply the checks below within the target scope. A signal becomes a finding only under the evidence and consequence rules in `SKILL.md`. The examples illustrate those rules; they do not create automatic violations.

## Required reference loading

The design checks in this file apply to functions, data models, and module boundaries. For validation, errors, I/O, numeric or temporal values, encoding, shared state, tests, potentially costly work, public evolution, or proposed edits, read [correctness, verification, and change safety](correctness-and-boundaries.md). Apply each section only when its named subject exists in the target. Record other dimensions as not applicable with a reason.

| Dimension | Evidence to inspect | Useful correction and exception |
|---|---|---|
| Naming | Whether a reader can identify the value's domain meaning in its scope; inconsistent terms for the same concept | Rename ambiguous terms. Short names in formulas or narrow scopes can be clear. Established project vocabulary takes precedence over personal naming taste. |
| Comments | Whether prose adds rationale, constraints, public documentation, or information absent from the code | Remove stale narration or clarify the code. Keep required API documentation, licenses, generated annotations, and explanations of non-obvious behavior. Do not manufacture workaround comments. |
| Control flow | Nesting, repeated branches, mixed responsibilities, and the order of observable effects | Consider guards or extraction when they reduce backtracking. Preserve cleanup, lock lifetimes, evaluation order, and exception behavior. A cohesive long routine can be clearer than fragmented helpers. |
| Abstraction | Boundary role, policy enforcement, ownership, test seams, and actual callers | Remove a forwarding layer only when it adds no contract or boundary value. A single implementation can justify an interface; a single method can justify an object with state or lifecycle responsibilities. |
| Duplication | Shared meaning, consumers, and reasons for change | Reuse an existing helper only when its behavior fits. Co-locate related variant metadata when ownership and evolution align. Avoid a universal utility that couples unrelated domains. |
| API design | Call-site interpretation, parameter meaning, defaults, absence and failure contracts | Apply the design checks in this file. |
| Architecture | Public surface, dependency direction, representation boundaries, and mutable-state ownership | Apply the design checks in this file. |
| Validation | Input origin, invariant enforcement, mutation, deserialization, and re-entry into trusted code | Validate at trust boundaries. Remove repeated validation only after proving the earlier guarantee still holds. In dynamic languages, explicit checks may be the primary contract mechanism. A type escape or assertion is not proof of validity. |
| Errors | Expected absence, failure categories, propagation, diagnostic context, and caller recovery | Use the project's idiomatic error contract. Replace catch-and-ignore with intentional recovery or propagation. Retain logging at responsible boundaries; distinguish it from silently reporting success. |
| Side effects | Hidden I/O or state changes, dependency ownership, time/randomness, resource release, and retry behavior | Isolate decisions from effects when that makes the affected behavior easier to test. Make dependencies explicit when needed. Do not add layers solely to make every function pure. |
| Behavioral tests | Whether assertions detect wrong outputs, state transitions, errors, or external interactions relevant to the contract | Strengthen assertions with independent expected behavior. Mocking and snapshots can be useful evidence; counts are not quality scores. Do not remove a weak test without preserving its useful coverage. |
| Performance costs | Repeated work, data-size growth, resource limits, and measured tradeoffs | Apply correctness-and-boundaries.md; do not claim measured improvements without observations. |
| Change safety | Consumers, migration needs, scope, debugging artifacts, and existing behavioral evidence | Apply correctness-and-boundaries.md. |

## Non-normative examples

**Redundant wrapper:** a helper forwards arguments unchanged to another function. Check whether it anchors a public API or isolates an unstable dependency. Without such a role, inlining may reduce indirection; with that role, keep it.

**Repeated null guard:** a function receives a value checked by its caller. Establish that all entry points enforce the invariant and that the value cannot change before use. Otherwise, removing the guard is unsupported.

**Narration comment:** a comment merely repeats an obvious assignment. Removing it can reduce reading cost. A comment describing a required legacy encoding documents a constraint and remains useful.

**Mock-heavy test:** a test asserts only that a mocked helper was called. That assertion is useful when the invocation is the contract. When the contract is a transformed result, propose an assertion on that result instead.

**Pure cleanup versus bug fix:** flattening branches may preserve behavior. Adding a timeout or changing error propagation may change behavior. Report the latter as a separate correctness proposal unless authorized.


Apply these checks as contextual review criteria under the finding rules in `SKILL.md`. Do not redesign unrelated modules or impose one programming paradigm.

## Functions and caller ergonomics

- Check whether names communicate domain meaning without unnecessary narration, redundant type labels, or vague responsibility suffixes. Keep established role names, short local names, and descriptive names when they make the contract clearer.
- Inspect call sites for ambiguous positional arguments, boolean switches, and arguments whose relationship is unclear. Consider named arguments, a cohesive parameter record, or distinct operations when these clarify the actual contract. Do not impose a parameter-count limit.
- Check that a function's name describes its responsibility and observable effects. Separate orchestration from low-level mechanisms when the mixture forces readers to track unrelated details. Preserve cohesive algorithms and meaningful wrappers.
- Check that optional parameters and defaults agree with caller expectations. Keep business defaults with their policy owner and transport defaults with their transport owner. Flag repeated call-site settings only when they duplicate the same policy.
- Check return-shape consistency for related operations. For APIs with synchronous and asynchronous alternatives, make the distinction predictable to callers. Do not force every operation in a module to use the same execution model.
- Check that legitimate absence, invalid input, and operational failure are distinguishable using the project's idioms. Flag sentinels only when they collide with valid values or make callers guess. Preserve established public contracts during cleanup.
- Inspect deeply traversed structures for leaked implementation details. Move a decision to the owner when that reduces coupling; ordinary access to a public data record does not itself require a new method.

## Representations and abstraction

- Check whether representations permit invalid combinations, missing variant data, or confusion between distinct domain concepts. Use constructors, tagged states, value objects, static types, or runtime checks according to language and project capabilities. Static types do not replace boundary validation.
- Inspect variant dispatch and related labels, defaults, or properties for incomplete coverage and synchronized copies. Use a cohesive authoritative definition or explicit consistency checks when these represent one concept. Preserve independent ownership and deliberate exhaustive dispatch.
- Compare data-shape declarations with runtime validators and conversions. Derive or share definitions when their semantics match; otherwise document and check the mapping. Wire, domain, and storage shapes need not be identical.
- Check casts, unchecked conversions, suppressed diagnostics, and dynamic accesses for a documented enforcement point. Keep justified interoperability mechanisms, negative diagnostic tests, and documented migration exceptions; do not accept an escape merely because it makes a diagnostic disappear.
- Check generic algorithms and configuration layers against actual variation or a required extension boundary. Remove speculative flexibility only when it has no contract, lifecycle, or caller value. A single current caller is not sufficient evidence of redundancy.
- Before adding a dependency or helper, inspect compatible existing capabilities. Flag overlap when it duplicates maintenance or increases dependency costs without a required semantic, security, or operational benefit. Do not force reuse of an incompatible implementation.

## Modules, dependencies, and state

- Check whether exported helpers expose internals without a consumer contract. Keep the public surface intentional and arrange definitions so readers can find the entry point using project conventions. Do not mandate a particular file order or import syntax.
- Inspect dependency cycles and dependencies from stable policy to volatile implementations. Propose a boundary or shared concept only when it addresses concrete coupling or initialization problems; do not require a layered architecture universally.
- Check conversions at wire, domain, and persistence boundaries for leaked transport/storage assumptions. Keep separate shapes when responsibilities differ; avoid duplicate models that merely add forwarding work.
- Identify the owner of mutable state and permitted mutation paths. Check aliasing, lifecycle, and hidden coupling across consumers. Choose copying, immutability, or controlled mutation based on correctness and resource costs.
- Inspect import/load-time initialization for I/O, registration, configuration access, and order dependence. Use explicit initialization when implicit effects break isolation or lifecycle control. Required plugin registration is a legitimate exception when its contract is clear.
- Inspect decision logic entangled with I/O, clocks, randomness, identifiers, or configuration. Introduce a seam when it makes the affected behavior controllable without needless layers. Do not force all logic into pure functions.
