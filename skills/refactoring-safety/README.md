# refactoring-safety

> Use when: planning or executing a behavior-preserving refactor: characterization coverage before touching code, small reversible steps with a green check after each, strict separation of restructuring from behavior change, and a stop-and-reclassify tripwire when behavior shifts.

This skill is aimed at planned or in-flight behavior-preserving restructurings where the danger is the quiet slide from refactor into unreviewed behavior change.

It helps an assistant:

- distinguish planning from authorized execution, and plan completeness from completed refactoring
- define the preserved observable contract, inspect authorized repository evidence, and distinguish reported coverage, inspected tests, and executed checks
- record searched consumer surfaces, supplied versus discovered consumers, and remaining unknowns; an empty search result applies to the inspected scope
- block dependent restructuring until unknown coverage is verified, characterization passes, or a named user or accountable owner explicitly accepts the uncovered behavior; pending acceptance is not approval
- pin current behavior (bugs included) with characterization tests, recording discovered bugs as owner questions rather than in-flight fixes
- plan steps as single named transformations with a green check after each, separated mechanical vs hand edits, and revertibility status including `point-of-no-return` flags
- record actual baseline and after-step check results; failed or unavailable required checks prevent execution completion
- bind executed check results to the checked state, including uncommitted changes, and rerun affected checks when inputs change
- preserve pre-existing and concurrent work during rollback; stop when overlapping edits cannot be separated safely
- enforce the tripwire when preserved behavior or its expectations change; permit justified internal-assertion edits only with evidence that the original behavior remains checked
- record pre-existing suspected dead code as owner questions; permit deletion of code made redundant by the refactor only after checking consumers and behavior preservation
- inspect the complete refactor diff against preserved behavior and step boundaries before execution completion, and repeat that review after further refactor edits
- emit a deterministic BLOCK template when no refactoring target is supplied

## Files

- [`SKILL.md`](SKILL.md) — workflow, execution gates, final diff review, output contract, and completion criteria.
- [`references/examples.md`](references/examples.md) — a partial extraction plan and common mistakes.
