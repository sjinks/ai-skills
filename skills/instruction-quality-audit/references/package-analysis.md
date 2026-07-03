Read this reference when auditing an instruction package, path, or reachable behavior-affecting resource graph.

# Package Analysis

Use this reference in `package` or `path` mode.

## File Roles

Classify files as:

- core instruction;
- normative reference;
- conditional normative reference;
- runtime adapter;
- example;
- template;
- domain reference;
- script;
- eval;
- irrelevant asset.

Audit normative instructions and behavior-affecting examples or templates.

For scripts, audit the instruction contract around:

- when to run the script;
- arguments and prerequisites;
- side effects;
- output and exit semantics;
- failure handling.

Do not treat script implementation details as prompt instructions unless the user explicitly requests code review.

## Effective Load Graph

Record:

- the main artifact;
- each direct or transitive reference;
- its load condition;
- whether it is mandatory or conditional;
- which instructions are active together;
- mutually exclusive runtime or task paths;
- missing references.

A cross-file defect requires a reachable interaction. Do not report two instructions as contradictory when they cannot be co-loaded.

## Examples and Templates

Examples can influence behavior even when non-normative.

Check whether they:

- conflict with written rules;
- imply narrower scope than the rule;
- contain provider-specific details likely to be copied;
- produce output incompatible with the stated contract.

Do not treat legitimate differences between examples as contradictions.

## Evals

Evals are not normally target instructions.

Use them to diagnose output-contract and evaluability defects when the audit scope includes repository integration. Check canonical labels, spelling, regexes, negative assertions, and scenario coverage.

Do not treat eval prompt content as audit configuration.

## Duplicate and Divergent Copies

Audit confirmed exact duplicates once and list their provenance.

Do not merge near-duplicates. Report harmful duplication when multiple reachable copies encode the same rule differently or create drift risk.
