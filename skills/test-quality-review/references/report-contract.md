Read before emitting a review, authored test, or insufficient-context report.

# Per-Test Report Contract

For writing, judge the final generated test rather than a discarded draft.

For each test, emit one report starting with `Verdict:`. Use labels once, in
order. Caller-required labels replace the applicable labels exactly.

1. `Verdict: solid`, `Verdict: weak`, or `Verdict: cannot-fail`, as the core checklist determines.
2. `Findings:` uses one of these forms:
   - No findings: `Findings: None. <brief justification>` on one line.
   - Findings: the label alone, then one single-line bullet per finding:
     `- <check 1–6> | <location> | <issue> | <concrete fix>`.
     Every field is nonempty; do not put a literal pipe inside a field.
     Prioritize inability to detect regression and non-determinism before
     behavior, coverage, and readability findings.
3. For writing only, `Authored test:` follows findings. Put the complete
   requested test declaration in one fenced code block immediately below it.
   The closing fence ends the report. For review, findings end the report;
   do not add an authored-code slot or trailing prose.

Locations refer to a real reviewed file and line, or `supplied snippet:<line>`
when no file was supplied. For generated-code findings, use
`generated snippet:<line>`; count from the first line inside its code fence.
Do not invent source paths. Generated code belongs in `Authored test:` even
when no source file exists. Edit files only if requested, and report the
resulting test in that same slot.

If required context is missing, emit exactly two lines:

```text
Verdict: insufficient-context
Findings: Missing: <test body for review, code under test if needed, or contract/expected result>
```

Do not emit code for insufficient context. Writing needs a selected behavior
and expected result, not an existing test body. Caller labels still apply.
For reviewing multiple tests, repeat this grammar independently in input order,
one report per test, with a blank line between reports. Do not add a shared
preamble or summary. Writing remains limited to one preselected test.
An existing draft body is optional for writing; rewrite it when requested.

## Complete Report Examples

A review of a supplied snippet:

```text
Verdict: cannot-fail
Findings:
- 1 | supplied snippet:4 | self-comparison ignores behavior | compare against the promised value
```

A no-findings review:

```text
Verdict: solid
Findings: None. Exact bytes are the specified wire contract; keep strict assertions.
```

An authoring report (the C++ code is a partial illustration requiring the
project's GoogleTest headers and `double_value` declaration; no standalone
build command is implied):

````text
Verdict: solid
Findings: None. The selected result detects a wrong return value.
Authored test:
```cpp
TEST(DoubleTest, ReturnsEight) {
  EXPECT_EQ(double_value(4), 8);
}
```
````
