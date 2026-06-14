# hypothesis-driven-debugging

> Use when: debugging a failure, bug, flaky test, or unexpected behavior with a disciplined loop: reproduce first, falsifiable hypothesis, cheapest discriminating experiment, evidence log, root-cause versus symptom decision, and a regression check before the fix counts as done.

This skill is aimed at failures, bugs, flaky tests, and unexpected behaviors that need structured investigation — fresh or rescued from a stalled guess-driven session.

It helps an assistant:

- establish reproduction status first and treat reproduction improvement as experiments in their own right
- separate observations (facts only) from hypotheses, each a falsifiable claim naming a mechanism
- run one-variable discriminating experiments with predictions and recorded `confirmed` / `refuted` / `inconclusive` / `proposed` verdicts
- classify inherited guesses from evidence before adding new hypotheses, and park speculation in an untested backlog
- gate the fix: explicit root-cause-vs-symptom call, all observations explained, and a regression check that fails before and passes after — or the fix is `unverified`
- record vanished failures as `not established (not reproduced — cause unknown)`, never as fixed

## Files

- [`SKILL.md`](SKILL.md) — the full skill definition.
