# requirement-sharpening

> Use when: sharpening a software requirement or requirement set so it is buildable and decidable rather than merely well-formed — replacing vague quality words and quantifiers with a measured threshold plus a named measurement method, eliminating requirements that defer their own observable behavior to a later decision, decoupling a requirement from named implementation files or symbols, making MUST/SHOULD/MAY rankings actually discriminate, adding a completeness matrix against a standard or dependency the spec leans on, and asserting a bidirectional traceability invariant as a mechanical gate.

This skill makes requirements **buildable and decidable**, not merely well-formed. A requirement can be singular, ranked, and traceable — passing a structural audit — and still be impossible to implement unambiguously or to assert a definite outcome for. The governing rule: every requirement must name a definite, observable outcome and a way to decide whether that outcome was met. It judges the content decidability of each requirement and preserves every stable ID and trace link rather than restructuring the document.

It helps an assistant:

- replace an unmeasurable quality word (*fast, efficient, gratuitous, bounded, reasonable*) with a measured threshold **and** a named measurement method, reusing the repo's existing benchmarks/profilers/counters and giving the default value the implementation will ship
- eliminate requirements that defer their own observable behavior ("or, if the design chooses, serialized") by folding the decided behavior in and demoting the alternatives to a resolved-decision log — after confirming the resolution in the sibling architecture, not guessing it
- decouple a requirement from named implementation files/symbols so it survives a refactor, moving the "how" to the architecture while keeping legitimate stable-artifact names (append-only enums, interface IDs) that are themselves the contract
- make MUST/SHOULD/MAY rankings discriminate instead of marking everything MUST, without ever down-ranking a fail-closed security or lifetime-correctness default
- add a compact completeness matrix mapping each case a leaned-on standard/dependency mandates to the requirement (or dependency) that covers it, surfacing the cases the dependency does not handle
- assert a greppable bidirectional traceability invariant (every AC ↔ requirement ↔ test case) so duplicate or dangling IDs are caught mechanically across the spec/architecture/test-plan trio
- return `BLOCK` / `CONCERNS` / `SHARP` with a findings table (quote, failing check, concrete rewrite), an open-items list of gaps it flags rather than fabricates, and a deterministic insufficient-context template

It complements document-structure and stable-ID work (singular decomposition, clause outline, honest conformance statement) and defers word-level ambiguity, acceptance-criterion verifiability, and test-code quality to their dedicated concerns.

## Files

- [`SKILL.md`](SKILL.md) — the full skill definition.
