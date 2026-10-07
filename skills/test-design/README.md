# test-design

> Design and implement a small, risk-focused set of automated tests for a feature or module, or assess suite-level gaps.

This framework-independent skill derives feature or module case sets from observable behavior, requires each case to catch a plausible defect, follows repository test conventions, and reports verification honestly. A dedicated framework testing workflow takes precedence when available; isolated test-code quality, writing one preselected test, and flaky-test diagnosis remain outside its scope.

Route by the design task, including selecting a case set with one case. Modify tests only when explicitly requested; otherwise provide a read-only plan or requested suite-gap assessment. Writing one already-selected test belongs to the isolated test quality workflow. Honor explicit coverage requirements without using percentages as the sole selection criterion. A missing contract blocks selection only when no expected behavior is established; partial contracts permit supported cases. Changed tests may finish with a diagnosed failure or an explicit unavailable-run reason. Execution evidence must describe the final edited tests; diagnostic edits require another run. A local substitute must preserve the tested behavior and observation.

## Files

- [`SKILL.md`](SKILL.md) — workflow, decisions, output, and completion checklist.
- [`references/test-selection.md`](references/test-selection.md) — detailed guidance for choosing cases and assertions.
