# test-design

> Design and implement a small, risk-focused set of automated tests for a feature or module, or assess suite-level gaps.

This framework-independent skill derives feature or module case sets from observable behavior, requires each case to catch a plausible defect, follows repository test conventions, and reports verification honestly. A dedicated framework testing workflow takes precedence when available; isolated test-code quality work and flaky-test diagnosis remain outside its scope.

Route by the design task, including a case set with one case. Honor explicit coverage requirements without using percentages as the sole selection criterion. A missing contract blocks selection only when no expected behavior is established; partial contracts permit supported cases. Changed tests may finish with a diagnosed failure or an explicit unavailable-run reason. Execution evidence must describe the final edited tests; diagnostic edits require another run. A local substitute must preserve the tested behavior and observation.

## Files

- [`SKILL.md`](SKILL.md) — workflow, decisions, output, and completion checklist.
- [`references/test-selection.md`](references/test-selection.md) — detailed guidance for choosing cases and assertions.

The eval suite checks planning, implementation, assessment, missing input, and
activation boundaries, including review-finding plans. Its additional
`report_contract`, `changed_test_file`, and `production_unchanged` metrics validate
the report grammar, test-file edits, and unchanged production fixture. The
implementation profile requires `Ran: <command> => <passed|failed|exit N>` or an
explicit unavailable-run reason. Additional implementation edges distinguish
unavailable hardware without a faithful substitute from a diagnosed production
regression failure. Exact snapshots verify executable tests and unchanged
production files; semantic contrastive cases check success invariants and
offending-row reporting.
