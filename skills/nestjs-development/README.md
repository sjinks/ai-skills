# nestjs-development

> Use when: designing, scaffolding, implementing, refactoring, or debugging NestJS applications: modules, controllers, services, DI, request lifecycle, DTOs, ORM integration, auth, configuration, microservices, and production wiring, including tests that ship with a feature. Excludes dedicated test work, framework version upgrades, and review-only requests.

This skill is aimed at designing, scaffolding, implementing, refactoring, or debugging NestJS code that needs to be idiomatic, secure, testable, and consistent with the project's existing conventions. Dedicated test design, test repair, and coverage-gap work belong to a separate testing skill.

It helps an assistant:

- identify the requested behavior and update only the affected feature surfaces, preserving unrelated wiring
- apply architecture principles such as thin controllers, fat services, explicit DI, validation at the edge, typed errors, and configuration over code
- use idiomatic patterns for modules, controllers, services, DTOs, custom decorators, global pipes/filters/interceptors at bootstrap, and config validation, plus the test setup that ships with a feature using `@nestjs/testing`
- avoid common anti-patterns such as `new`-ing `@Injectable()` services, `any` on DTOs, hardcoded secrets, and `synchronize: true` in production
- prefer additive, reversible changes and call out breaking changes explicitly

## Files

- [`SKILL.md`](SKILL.md) — operational workflow, decision rules, output contract, and completion gates.
- [`references/patterns.md`](references/patterns.md) — partial implementation and test illustrations.
