# refactoring-safety

> Use when: planning or executing a behavior-preserving refactor: characterization coverage before touching code, small reversible steps with a green check after each, strict separation of restructuring from behavior change, and a stop-and-reclassify tripwire when behavior shifts.

This skill is aimed at planned or in-flight behavior-preserving restructurings where the danger is the quiet slide from refactor into unreviewed behavior change.

It helps an assistant:

- define the preserved observable contract and map every behavior to a safety net: an existing check, an `unknown — verify` marker, a characterization step, or an explicit `accepted-uncovered` entry
- pin current behavior (bugs included) with characterization tests, recording discovered bugs as owner questions rather than in-flight fixes
- plan steps as single named transformations with a green check after each, separated mechanical vs hand edits, and revertibility status including `point-of-no-return` flags
- enforce the tripwire: changed test expectations or shifted behavior stop the work, get recorded, and are reclassified as separate behavior change
- block bare steps when coverage is too thin and no characterization seam exists
- emit a deterministic BLOCK template when no refactoring target is supplied

## Files

- [`SKILL.md`](SKILL.md) — the full skill definition.
