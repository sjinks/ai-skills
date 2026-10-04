# iteration-retrospective

> Use when: reflecting on multi-attempt work to turn evidence from implementations, debugging, investigations, or review/fix chains into prevention decisions and an evidence-backed reusable-skill recommendation when warranted.

This skill reconstructs what was attempted, what actually happened, and what should prevent recurrence. It avoids generic self-critique and does not recommend a new skill when a validator, local instruction, or refactor is the smaller remedy.

Explicit retrospective requests with unavailable evidence reach the blocked path; generic reflection without attempt evidence remains excluded.

The report defines attempt statuses, evidence-bound cause grouping, skill candidates derived from selected prevention, and `CLEAN` / `CONCERNS` / `BLOCK` verdicts. Static report validation covers default and caller-selected labels and the blocked branch; live model behavior remains separate evidence.

Default report markers use the `Retrospective` prefix so negative evals permit ordinary status and review labels. Caller-selected labels remain supported for nonblocked reports. Invalid nonblocked labels produce a fixed two-line label clarification instead of a report; blocked reports ignore all replacements.

## Files

- [`SKILL.md`](SKILL.md) — the full skill definition.
- [`references/report-format.md`](references/report-format.md) — workflow, ordered status and candidate rules, row grammar, label replacement, and blocked reports.
