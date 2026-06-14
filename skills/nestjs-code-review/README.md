# nestjs-code-review

> Use when: performing code review, pull request review, security review, architecture review, or change-impact review of NestJS applications; reviewing controllers, services, modules, providers, guards, interceptors, pipes, exception filters, DTOs, validation, configuration, ORM integration (TypeORM, Prisma, Mongoose, Drizzle, MikroORM, or similar), authentication, authorization, testing, or production readiness.

This skill is aimed at NestJS pull requests, feature branches, security reviews, and architecture validations where a repeatable review contract is more useful than ad-hoc style comments.

It helps an assistant:

- restate the change as intent, scope, risk surfaces, severity rubric, and out-of-scope before judging
- walk a checklist covering module architecture and DI, controllers and the request lifecycle, DTOs and validation, guards and auth, exception handling, configuration and bootstrap, persistence, testing, API design, performance, and microservices
- flag NestJS-specific anti-patterns such as fat controllers, direct ORM access from controllers, `forwardRef` overuse, and modules exporting themselves
- return findings classified as Critical, Warning, or Suggestion, each with file/line evidence and a concrete fix
- stay stack-neutral on ORM and auth strategy while respecting existing project conventions

## Files

- [`SKILL.md`](SKILL.md) — the full skill definition.
