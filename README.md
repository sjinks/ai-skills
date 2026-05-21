# ai-skills

Small repository of reusable AI assistant skills.

Each skill is stored as a Markdown document with YAML frontmatter and is intended to give an assistant a focused workflow, checklist, and output format for a specific engineering task.

## Repository Structure

```text
skills/
  <skill-name>/
    SKILL.md
```

At the moment, the repository contains one skill:

- `ssrf-outbound-fetch-review`: guidance for reviewing, designing, implementing, and testing SSRF protections around outbound HTTP fetches, from egress policy contracts through transport and redirect behavior.

## Included Skill

### `ssrf-outbound-fetch-review`

This skill is aimed at code paths that accept or derive URLs from untrusted or semi-trusted input and then perform outbound requests, especially when policy, parsing, DNS, proxy, transport, redirect, and trusted private-target opt-in behavior all need to line up.

It helps an assistant:

- define explicit egress and port policy contracts before implementation
- review URL parsing, normalization, IP classification, and DNS handling, including connection-time lookup and rebinding risks
- reason about proxy behavior and transport semantics such as SNI, Host, and certificate verification
- assess redirect safety, sensitive-header handling, and trusted private-target opt-ins
- build realistic adversarial tests for SSRF-related edge cases
- return findings in a consistent, review-ready format

The skill covers both implementation concerns and review discipline, including boundaries, required input context, a definition of done, and a structured output contract.

## Skill Format

Each skill file follows the same high-level pattern:

1. YAML frontmatter for metadata such as name, description, and invocation hints.
2. A task-focused body describing when to use the skill.
3. Concrete procedures, checklists, and expected outputs.

The current skill uses frontmatter fields such as:

- `name`
- `description`
- `argument-hint`
- `user-invocable`

## How To Use

Use this repository as:

- a source of reusable skill definitions
- a reference for writing additional task-specific AI skills
- a place to keep security and review workflows in a consistent format

When adding a new skill, prefer:

- one directory per skill under `skills/`
- a single `SKILL.md` entry point
- a narrow, well-defined trigger condition
- concrete checklists and output expectations instead of generic advice

## Next Additions

Natural follow-ups for this repository would be more narrowly scoped engineering skills in adjacent areas, for example request validation, archive safety, egress deployment policy, language-specific secure coding workflows, or review-specific secure coding workflows.
