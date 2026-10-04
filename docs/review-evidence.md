# Review evidence for instruction and eval changes

Use this workflow when changing decision rules or output contracts. It implements
contrastive verification and honest evidence reporting; it adds no new skill or
model evaluation task.

## Workflow

1. Inventory changed rules and their consumers. Include validators, task graders,
   templates, references and documentation. Human review must confirm the scope
   includes every applicable consumer; the runner cannot discover omitted rules.
2. For each rule, provide a conforming input and a counterexample that changes
   only the asserted condition. Name that mutation and the expected diagnostic.
   Include valid unusual inputs to catch false rejection, such as marker literals
   inside code. Inspect each validator and both inputs before execution.
3. Inventory six dimensions: `defaults`, `optional-inputs`, `multiplicity`,
   `side-effects`, `payload-boundary`, `outcomes`. Every dimension must occur in
   a rule or have a concrete inapplicability reason, never both.
4. Stage the complete intended change and record its tree with `git write-tree`.
   Keep the manifest outside that tree to avoid a circular hash dependency.
   Supply a full tree object ID, not a moving branch or commit ID. Any scoped
   change requires a new tree and renewed review evidence.
5. Run the gate with the author-reviewed manifest. Only trusted local Python
   validators are supported. Arguments are passed literally without a shell;
   scripts can still perform arbitrary operations. Do not configure paid/live
   model calls, installs, or unapproved side effects. The runner is not a sandbox.
6. Obtain a fresh, read-only independent review when permitted by runtime/model
   constraints. The reviewer must not have authored the change or its checks;
   ask it to challenge false acceptance, false rejection and omitted dimensions.
   A local self-review is recorded as unavailable independent review with the
   specific constraint. Do not label it independent.
7. Record four separate evidence claims. No probe result promotes these claims:
   - `contract`: static acceptance/rejection and projection consistency;
   - `workspace`: observed state, identifying final-state versus trace coverage;
   - `execution`: the exact command, target and revision actually executed;
   - `model-behavior`: measured model invocation/output, or explicitly unverified.
8. Put the immutable tree, scope, contrastive results, evidence limits and review
   result in the PR description. Run native repository audits on that same tree.

## Manifest contract

The gate runs both inputs for each rule using the same command. Conforming input
must exit 0. Counterexample input must exit 1 and its stderr must match the
`rejection` Python regex. A timeout, wrong diagnostic or failed conforming case fails the gate. Standard
Python traceback headers (including exception groups) in either stream fail both
probe paths, even when the exit code and diagnostic otherwise match. This
rejects ordinary uncaught exceptions; a custom exception hook that suppresses
the traceback cannot be distinguished from intentional rejection by this
output protocol alone. Validators with a different rejection exit code need an
explicit adapter; do not weaken the expected failure into any nonzero code.

`scope` lists existing regular files relative to the repository root. Each must
exist in the tree and match the current working bytes and owner-executable bit.
Both pre- and post-probe comparisons disable external diff drivers and textconv
with `--no-ext-diff --no-textconv`; the meaning of those flags is defined in the
[Git diff documentation](https://git-scm.com/docs/git-diff). Raw blob bytes and the executable bit are checked separately so clean filters,
line-ending normalization and `core.fileMode` cannot conceal scoped changes.
A working file normalized by filters must actually match its tree bytes before
this gate can pass. Scope paths are literal, not Git wildcard pathspecs. Include the
validator script itself. Commands start with `python3`, followed by a scoped
`.py` script and optional literal arguments. The gate uses its own Python
interpreter. Directory-wide scope and symlink files are not supported.

Every claim has `status` equal to `verified`, `unverified` or `not-applicable`,
and nonempty `evidence`. These are author declarations, not independently
validated facts. Evidence should name logs/artifacts, commands and revisions, or
the concrete missing evidence. Independent review has `status` equal to
`completed` or `unavailable`, and nonempty `evidence`. `completed` also requires
a named `reviewer` and the same `tree`. The runner cannot authenticate reviewers
or decide independence. Existing native audit verdicts remain authoritative;
a gate pass alone is not a readiness verdict.

Example manifest template for a single report-cardinality rule. Replace the tree
placeholder and reasons with evidence for the actual change; expand scope and
rules before using it for a broader review:

```json
{
  "tree": "FULL_TREE_ID_FROM_GIT_WRITE_TREE",
  "scope": ["evals/test-quality-review/check-report.py"],
  "rules": [{
    "id": "review-verdict-cardinality",
    "source": "evals/test-quality-review/check-report.py",
    "dimensions": ["multiplicity"],
    "mutation": "append a second verdict marker outside the report",
    "command": ["python3", "evals/test-quality-review/check-report.py", "review"],
    "accept": "Verdict: solid\nFindings: None. Expected result is asserted directly.",
    "reject": "Verdict: solid\nFindings: None. Expected result is asserted directly.\nVerdict: solid",
    "rejection": "marker must occur exactly once"
  }],
  "not-applicable": {
    "defaults": "This example changes only marker cardinality.",
    "optional-inputs": "No optional input rule changes in this example.",
    "side-effects": "The example validator only reads stdin.",
    "payload-boundary": "This example is a review report without authored code.",
    "outcomes": "The verdict domain is unchanged in this example."
  },
  "claims": {
    "contract": {"status": "unverified", "evidence": "Run the contrastive probe first."},
    "workspace": {"status": "unverified", "evidence": "No workspace observation supplied."},
    "execution": {"status": "unverified", "evidence": "No target test run supplied."},
    "model-behavior": {"status": "unverified", "evidence": "No paid model run approved."}
  },
  "independent-review": {
    "status": "unavailable",
    "evidence": "Replace with the actual runtime/model constraint or completed review."
  }
}
```

```bash
python3 evals/_helpers/check-review-evidence.py /tmp/review-evidence.json --repo "$PWD"
python3 -m unittest discover -s evals/_helpers -p test_check_review_evidence.py
```

## Evidence limits

The runner checks only listed files against the tree and rechecks that scope after
probes. It cannot observe transient/restored changes, unlisted files or external
state. It executes trusted validators only after structural manifest validation;
it does not prove their purity or the semantic isolation of a counterexample.
Expected diagnostics and traceback checks are observable signals, not
authentication of how a validator terminated.
Review those properties separately. Successful probes produce
`contrastive-checks: passed` and preserve the supplied claims/review limitation;
they do not certify skill behavior on any model.
