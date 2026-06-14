# nestjs-version-upgrade

> Use when: planning or executing a NestJS version upgrade or major migration; bumping @nestjs/* across majors, upgrading the underlying platform adapter (Express or Fastify), bumping RxJS or TypeScript, triaging breaking changes and deprecations, sequencing peer-dependency and ORM/Passport/config-package bumps, updating bootstrap and decorator usage, and producing a reversible, verifiable upgrade plan.

This skill is aimed at moving a NestJS app across versions safely: a major `@nestjs/*` bump, a platform-adapter swap, or a Nest-driven RxJS/TypeScript bump, with an ordered plan where every step is verifiable and reversible.

It helps an assistant:

- establish a green baseline, then read the official migration guides and CHANGELOGs for each major between current and target
- map breaking changes to this codebase's call sites and sequence the bumps one major at a time, framework plus first-party peers together
- plan each step as a reversible unit with a verification check and a rollback, and execute one step at a time
- check the surfaces Nest majors most often break — bootstrap, platform adapter, decorators/metadata, RxJS, TypeScript, microservices transports, first-party peers
- avoid anti-patterns such as one giant bump commit, jumping two majors at once, `@ts-ignore`-ing failing call sites, and declaring success on a clean typecheck without booting the app
- record residual risk: deferred deprecations, pinned-back packages, and follow-ups

## Files

- [`SKILL.md`](SKILL.md) — the full skill definition.
