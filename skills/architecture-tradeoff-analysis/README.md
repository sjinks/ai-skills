# architecture-tradeoff-analysis

> Use when: comparing two or more candidate architectures, designs, or technical approaches against weighted quality attributes: performance, consistency and correctness, operability, cost, evolvability, team fit — making what each option worsens explicit before the choice is made.

This skill is aimed at choices between candidate architectures, designs, or technical approaches that need a structured comparison before the decision is made.

It helps an assistant:

- score each option per attribute as `strong`, `adequate`, `weak`, or `unknown`, with rationale for non-adequate cells
- require every option to carry at least one `weak` or `unknown` cell and a concrete makes-worse line
- treat constraints as pass/fail eliminations rather than scores, and keep eliminated options visible in the table
- use supplied weights verbatim, mark missing weights `unstated`, and report a deciding question instead of forcing a winner
- map every `unknown` cell to the cheapest evidence that would settle it
- end with a recommendation or deciding question — the decision stays with the owner

## Files

- [`SKILL.md`](SKILL.md) — the full skill definition.
