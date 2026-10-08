# iteration-retrospective

> Use when: reflecting on multi-attempt work to turn evidence from implementations, debugging, investigations, or review/fix chains into prevention decisions and an evidence-backed reusable-skill recommendation when warranted.

This skill reconstructs what was attempted, what actually happened, and what should prevent recurrence. It avoids generic self-critique and does not recommend a new skill when a validator, local instruction, or refactor is the smaller remedy.

Requests about multiple attempts or an explicitly abandoned approach reach the missing-evidence path even when evidence is unavailable. A single nonabandoned attempt and generic reflection remain excluded.

Environment-related failures are checked against existing safeguards, navigation, instruction usefulness, tool economy, and information access before prevention is selected. These lenses preserve the existing mechanism domains and cost ordering; missing checks alone do not establish a defect.

The report defines attempt statuses, evidence-bound cause grouping, skill candidates derived from selected prevention, and `CLEAN` / `CONCERNS` / `BLOCK` verdicts. Nonblocked failed or partially successful attempts require cause learnings, and `CONCERNS` requires next checks. Missing comparison costs leave the affected prevention unselected while preserving other selections.

Default report markers use the `Retrospective` prefix to distinguish them from ordinary status and review labels. Caller-selected labels remain supported for nonblocked reports. Labels containing C0/C1 controls (U+0000–U+001F and U+007F–U+009F) or Unicode line separators (U+2028/U+2029) are invalid. Invalid nonblocked labels produce a fixed two-line label clarification instead of a report; blocked reports ignore all replacements.

## Files

- [`SKILL.md`](SKILL.md) — the full skill definition.
- [`references/environment-prevention.md`](references/environment-prevention.md) — evidence-gated environment lenses and mapping to existing prevention mechanisms.
- [`references/report-format.md`](references/report-format.md) — workflow, ordered status and candidate rules, row grammar, label replacement, and blocked reports.
