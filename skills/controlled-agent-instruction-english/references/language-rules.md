When to read: before authoring, rewriting, or auditing model-facing prose.

# Controlled-English Rules

These rules govern model-facing prose. Preserve literals and apply the scope and precedence defined in [the operational guide](operational-guide.md). Sentence-length thresholds are advisory diagnostics.

## Rules

### 1. Terminology

#### T1. Use one term for one concept

Use the same term every time you refer to the same concept.

Do not introduce synonyms for stylistic variety.

#### T2. Use one meaning for one term

Do not use the same term for different concepts in the same instruction set.

If two concepts differ, name them differently.

#### T3. Preserve established technical terminology

Use the terminology of the applicable tool, API, framework, protocol, project, or domain.

Do not replace an exact technical term with a simpler but less precise term.

#### T4. Preserve literals exactly

Write identifiers, tool names, paths, commands, field names, enum values, and other literals exactly as defined by their source.

Use code formatting when useful.

#### T5. Prefer specific terms

Prefer a narrow, concrete term over vague words such as `thing`, `stuff`, `item`, `data`, `object`, or `result` when a more precise term exists.

#### T6. Avoid unnecessary synonyms

Repeat the same noun when repetition makes the reference clearer.

#### T7. Avoid idioms and figurative language

Do not express requirements with slang, metaphors, humor, or culture-dependent phrases.

Established technical idioms are allowed when they are standard in the domain.

#### T8. Avoid ambiguous noun stacks

Rewrite long noun sequences when the relationship between the nouns is unclear.

Use prepositions or clauses to expose the relationship.

### 2. Normative language

#### N1. Use imperative verbs for agent actions

Write required actions as direct commands.

Prefer:

> Read the configuration file.

Do not write:

> The configuration file should be read.

#### N2. Use `must` for invariants and required outcomes

Use `must` when a requirement is clearer as a constraint than as a command.

Example:

> The final verdict must be the last line.

#### N3. Use `do not` or `must not` for prohibitions

State prohibited actions directly.

#### N4. Use `should` only for overridable defaults

`Should` means that the instruction is the default but a relevant reason can justify another choice.

Do not use `should` for mandatory behavior.

#### N5. Use `may` only for permission or genuine optionality

Use `may` when an action is permitted but not required.

#### N6. Use `can` only for capability or possibility

Do not use `can` to express permission or a requirement.

#### N7. Avoid weak requirements

Avoid phrases such as:

- `try to`;
- `aim to`;
- `preferably`;
- `ideally`;
- `where possible`;
- `as appropriate`;
- `if practical`.

Use them only when discretion is intentional. When discretion matters, define the decision criterion.

### 3. Sentences

#### S1. Put one operational requirement in each sentence

Do not combine independent required actions into one sentence.

Split independent actions into separate sentences or steps.

Actions that form one atomic operation may stay together.

#### S2. Use sentence-length review thresholds

Use 25 words as the review threshold for an instructional sentence.

Use 30 words as the review threshold for a descriptive sentence.

A sentence may exceed its threshold when splitting it would reduce precision, distort scope, or make the instruction harder to interpret.

Treat these thresholds as diagnostics, not hard lexical limits.

#### S3. Use complete sentences

Do not remove necessary subjects, objects, verbs, conditions, or qualifiers only to make text shorter.

Fragments are acceptable in headings, labels, tables, and compact lists.

#### S4. Prefer active voice

Name the actor when the actor matters.

Passive voice is acceptable when the actor is unknown, irrelevant, or intentionally unspecified.

#### S5. Use direct verbs

Prefer verbs that directly name the action.

Prefer:

> Analyze the patch.

Do not write:

> Perform an analysis of the patch.

#### S6. Avoid contractions in normative instructions

Prefer `do not` to `don't` and `it is not` to `isn't` in requirements.

Quoted text is exempt.

### 4. References and scope

#### R1. Make pronoun references unambiguous

Use `it`, `this`, `that`, `they`, and similar references only when there is one plausible antecedent.

Otherwise, repeat the noun.

#### R2. Prefer named references over positional references

Prefer stable references such as rule IDs, section names, artifact names, and field names.

Avoid `the rule above`, `the previous section`, and similar positional references when a stable reference is available.

#### R3. Keep qualifiers close to the rule they modify

Place restrictions, exceptions, and qualifiers next to the applicable requirement.

#### R4. Give modifiers explicit scope

Make the scope of words such as `only`, `always`, `never`, `except`, `also`, `otherwise`, and `instead` unambiguous.

#### R5. Repeat key nouns when repetition prevents ambiguity

Do not prefer pronouns or ellipsis merely to reduce repetition.

### 5. Conditions and control flow

#### C1. Put conditions before actions

Prefer:

> If the file does not exist, stop.

Do not write:

> Stop if the file does not exist.

Use the condition-first form especially when the condition controls multiple actions.

#### C2. Make boolean relationships explicit

Use `and`, `or`, and `not` deliberately when logical relationships affect behavior.

#### C3. Distinguish `all` from `any`

When several conditions exist, state whether all conditions must hold or whether any condition is sufficient.

#### C4. State the alternative branch when it matters

If behavior differs when a condition is false, state the `otherwise` behavior explicitly.

Do not add an empty alternative branch when no action is required.

#### C5. Avoid deeply nested conditions

Do not encode several levels of control flow in one sentence.

Use separate steps, nested lists, or a decision table.

#### C6. State prerequisites before dependent actions

Place setup, validation, and preconditions before the actions that depend on them.

#### C7. Put exceptions next to the rule

State an exception immediately after the rule that it changes.

Do not hide important exceptions in distant sections.

#### C8. Make precedence explicit

When instructions can conflict, state which instruction wins.

Use a defined precedence order when two or more rule classes can produce conflicting instructions.

Do not rely on document order unless the instruction set explicitly defines document order as precedence.

### 6. Procedures

#### P1. Use numbered steps only when order matters

Use a numbered list for sequential actions.

Use bullets for independent rules, alternatives, or properties.

#### P2. Put one primary action in each step

A step may contain supporting information, but it must have one clear primary action.

#### P3. State inputs before processing them

Identify required inputs before instructions that use those inputs.

#### P4. State outputs when they are not obvious

Specify the expected artifact, decision, value, or state when the procedure's output could otherwise be ambiguous.

#### P5. State termination conditions

For iterative procedures, define when the agent must stop.

Do not write unbounded instructions such as `continue improving the result`.

#### P6. Define fallback behavior

When an expected operation can fail and the agent must recover, state the required recovery behavior.

#### P7. Do not hide actions in notes

A note may explain a requirement.

A note must not introduce a required action.

Write required actions as normal instructions.

#### P8. Keep examples non-normative

Examples illustrate rules. They do not create requirements unless the instruction set explicitly says otherwise.

The rule must remain understandable without the example.

### 7. Descriptive information

#### D1. Present information from general to specific

State the governing concept before details, edge cases, implementation notes, and examples.

#### D2. State the rule before its rationale

Put the requirement first. Put the explanation after it.

#### D3. Keep one topic in each paragraph

Start a new paragraph when the subject or purpose changes.

#### D4. Keep paragraphs short

Prefer no more than six sentences in a prose paragraph.

Use lists or subsections when several independent facts are present.

#### D5. Make important logical relationships explicit

Use words such as `because`, `therefore`, `but`, `if`, `otherwise`, `before`, `after`, and `instead` when the relationship affects interpretation.

#### D6. Separate requirements from explanation

Make it clear whether text is:

- a requirement;
- a definition;
- a rationale;
- an example;
- background information.

Do not mix these roles in one sentence when doing so can blur normative meaning.

### 8. Completeness and determinism

#### E1. Define behavior-changing vague criteria

Do not leave words such as `relevant`, `significant`, `appropriate`, `sufficient`, `simple`, `complex`, `large`, or `small` undefined when they control behavior.

Define the criterion or give useful decision boundaries.

#### E2. Avoid open-ended normative enumerations

Do not use `etc.`, `and so on`, `among others`, or similar forms when omitted members can change behavior.

Use an exhaustive list or define the category.

#### E3. Distinguish examples from exhaustive sets

Introduce examples with phrases such as `for example` or `such as`.

Introduce exhaustive sets explicitly, for example:

> Use one of these values:

#### E4. Define discretionary choices

When the agent must choose, specify the selection criterion.

Also specify the available choices when the set is bounded.

Specify a default when the criterion can produce no clear winner.

#### E5. Require explicit failure instead of invention

When required information cannot be obtained, report the missing information or blocker.

Do not guess unless another rule explicitly permits estimation or inference.

#### E6. Avoid duplicate normative rules

Define a requirement once unless local repetition is necessary to prevent ambiguity.

Reference that requirement elsewhere instead of restating it with different wording.

#### E7. Keep intentional repetition semantically identical

When local repetition improves clarity, preserve the same terminology and meaning.

Do not paraphrase repeated normative rules in a way that can create a second interpretation.

#### E8. Require observable interpretation

Every normative rule must describe behavior that a reviewer can distinguish from materially different behavior.

Rewrite instructions such as:

- `Be careful.`
- `Use good judgment.`
- `Keep things simple.`
- `Do a thorough review.`
- `Handle edge cases properly.`

Replace them with a criterion, boundary, required action, default, or explicit grant of discretion.
