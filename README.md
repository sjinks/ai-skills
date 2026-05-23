# ai-skills

Small repository of reusable AI assistant skills.

Each skill is stored as a Markdown document with YAML frontmatter and is intended to give an assistant a focused workflow, checklist, and output format for a specific engineering task.

## Repository Structure

```text
skills/
  <skill-name>/
    SKILL.md
```

At the moment, the repository contains these skills:

- `adversarial-review`: guidance for challenging specs, designs, implementations, workflows, and test plans with evidence-based failure-mode review and risk-focused verification.
- `ssrf-outbound-fetch-review`: guidance for reviewing, designing, implementing, and testing SSRF protections around outbound HTTP fetches, from egress policy contracts through transport and redirect behavior.
- `spock-voice`: guidance for adopting a Spock-inspired, precise, analytical, restrained, and lightly dry conversational register.
- `nestjs-code-review`: guidance for reviewing NestJS applications with severity-classified findings covering modules, DI, controllers, DTOs, guards, exception handling, persistence, testing, API design, performance, and microservices.
- `nestjs-development`: guidance for designing, scaffolding, implementing, refactoring, and testing NestJS features with idiomatic patterns, anti-patterns, and a structured build workflow.

## Included Skills

### `adversarial-review`

This skill is aimed at specs, designs, implementations, workflows, migrations, operational procedures, and test plans that need deliberate failure-mode review before they are trusted.

It helps an assistant:

- identify the target, intended behavior, assumptions, and evidence basis before judging
- apply optional review lenses for reliability, maintainability, security/privacy, user workflow, and verification
- classify failure modes with concrete categories, severity, and evidence standards
- distinguish confirmed issues, likely risks, open questions, accepted tradeoffs, and test gaps
- convert top risks into adversarial tests, mitigations, or acceptance criteria
- return `BLOCK`, `CONCERNS`, or `CLEAN` verdicts without inventing findings

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

### `spock-voice`

This skill is aimed at responses where the user explicitly asks for a Spock-inspired conversational register. It focuses on calm logic, scientific precision, disciplined curiosity, and understated dry humor while keeping the user's goal primary.

It helps an assistant:

- stay concise, analytical, and exact
- prefer evidence, probabilities, tradeoffs, and clearly stated assumptions
- use calm restraint rather than emotional flourish
- add light dry wit only when it improves warmth or clarity
- avoid impersonation, signature catchphrases, or style choices that override safety and accuracy
- apply the voice only to advisory commentary, leaving code, commit messages, PR text, and required structured output in a neutral register

### `nestjs-code-review`

This skill is aimed at NestJS pull requests, feature branches, security reviews, and architecture validations where a repeatable review contract is more useful than ad-hoc style comments.

It helps an assistant:

- restate the change as intent, scope, risk surfaces, severity rubric, and out-of-scope before judging
- walk a checklist covering module architecture and DI, controllers and the request lifecycle, DTOs and validation, guards and auth, exception handling, configuration and bootstrap, persistence, testing, API design, performance, and microservices
- flag NestJS-specific anti-patterns such as fat controllers, direct ORM access from controllers, `forwardRef` overuse, and modules exporting themselves
- return findings classified as Critical, Warning, or Suggestion, each with file/line evidence and a concrete fix
- stay stack-neutral on ORM and auth strategy while respecting existing project conventions

### `nestjs-development`

This skill is aimed at designing, scaffolding, implementing, refactoring, or debugging NestJS code that needs to be idiomatic, secure, testable, and consistent with the project's existing conventions.

It helps an assistant:

- restate intent and acceptance criteria, then walk a feature-module-first build workflow
- apply architecture principles such as thin controllers, fat services, explicit DI, validation at the edge, typed errors, and configuration over code
- use idiomatic patterns for modules, controllers, services, DTOs, custom decorators, global pipes/filters/interceptors at bootstrap, config validation, and unit tests with `@nestjs/testing`
- avoid common anti-patterns such as `new`-ing `@Injectable()` services, `any` on DTOs, hardcoded secrets, and `synchronize: true` in production
- prefer additive, reversible changes and call out breaking changes explicitly

## Skill Format

Each skill file follows the same high-level pattern:

1. YAML frontmatter for metadata such as name, description, and invocation hints.
2. A task-focused body describing when to use the skill.
3. Concrete procedures, checklists, and expected outputs.

The current skills use frontmatter fields such as:

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
