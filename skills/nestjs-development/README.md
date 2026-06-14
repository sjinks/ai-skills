# nestjs-development

> Use when: designing, scaffolding, implementing, refactoring, or debugging NestJS applications; building modules, controllers, services, providers, guards, interceptors, pipes, exception filters, DTOs, validation, configuration, ORM integration (TypeORM, Prisma, Mongoose, Drizzle, MikroORM, or similar), authentication, authorization, the test setup that ships with a feature, microservices, or production wiring. Dedicated test design, repair, or coverage work belongs to a testing skill, not this one.

This skill is aimed at designing, scaffolding, implementing, refactoring, or debugging NestJS code that needs to be idiomatic, secure, testable, and consistent with the project's existing conventions. Dedicated test design, test repair, and coverage-gap work belong to a separate testing skill.

It helps an assistant:

- restate intent and acceptance criteria, then walk a feature-module-first build workflow
- apply architecture principles such as thin controllers, fat services, explicit DI, validation at the edge, typed errors, and configuration over code
- use idiomatic patterns for modules, controllers, services, DTOs, custom decorators, global pipes/filters/interceptors at bootstrap, and config validation, plus the test setup that ships with a feature using `@nestjs/testing`
- avoid common anti-patterns such as `new`-ing `@Injectable()` services, `any` on DTOs, hardcoded secrets, and `synchronize: true` in production
- prefer additive, reversible changes and call out breaking changes explicitly

## Files

- [`SKILL.md`](SKILL.md) — the full skill definition.
