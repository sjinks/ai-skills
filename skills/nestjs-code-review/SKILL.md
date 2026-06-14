---
name: nestjs-code-review
description: "Use when: performing code review, pull request review, security review, architecture review, or change-impact review of NestJS applications; reviewing controllers, services, modules, providers, guards, interceptors, pipes, exception filters, DTOs, validation, configuration, ORM integration (TypeORM, Prisma, Mongoose, Drizzle, MikroORM, or similar), authentication, authorization, testing, or production readiness."
argument-hint: "Describe the NestJS change, affected files, modules, runtime/version, ORM choice, auth strategy, and tests or PR context."
user-invocable: true
---

# NestJS Code Review

Use this skill when reviewing a NestJS change: a pull request, a feature branch, a refactor, a security review, or an architecture validation. The goal is to turn NestJS review from ad-hoc style comments into a repeatable contract: scope, severity-classified findings, evidence, and concrete fixes.

## Boundaries

- This skill is for reviewing an existing NestJS change and returning classified findings. Designing or implementing a new feature from scratch is a separate build task and out of scope here.
- Review and reason about code only. Do not run production migrations, mutate live data, or hit production services.
- Prefer local inspection (read, grep, glob) and project-local tests over runtime probing.
- Do not enforce a single ORM (TypeORM, Prisma, Mongoose, Drizzle, MikroORM) or a single auth strategy (JWT, session, OAuth, mTLS); review against the project's chosen stack.
- Do not propose architectural rewrites unless critical issues warrant them.
- Respect existing project conventions even when they differ from default NestJS docs.
- Separate confirmed defects from style preferences, opinions, and defense-in-depth suggestions.

## Trigger Conditions

Use this skill if any of these are true:

- A change touches NestJS controllers, services, modules, providers, guards, interceptors, pipes, middleware, exception filters, or custom decorators.
- A change touches DTOs, validation, serialization, or OpenAPI/Swagger decorators.
- A change touches dependency-injection wiring: provider arrays, exports, custom providers, factories, `forwardRef`, scoped providers, dynamic modules.
- A change touches authentication, authorization, guards, or Passport strategies.
- A change touches ORM integration (TypeORM, Prisma, Mongoose, Drizzle, MikroORM, or similar) entities, repositories, transactions, or migrations.
- A change touches testing setup (`Test.createTestingModule`, mocks, `getRepositoryToken`, e2e harness, Supertest) and the task is to judge that change for findings. Authoring or repairing those tests is a dedicated testing task, not this skill.
- A change touches bootstrap, `main.ts`, global pipes/filters/interceptors, configuration, or environment loading.

## Required Input Context

Collect or ask for the narrowest useful context before reviewing:

- Affected files, modules, and feature area.
- NestJS major version and Node.js version.
- ORM choice and version (TypeORM/Prisma/Mongoose/Drizzle/MikroORM/none).
- Authentication strategy (JWT, session, OAuth, none).
- Transport (HTTP, GraphQL, microservices, WebSocket).
- Whether validation pipe is enabled globally and with which options.
- Whether the project uses CQRS, event-driven, or repository patterns.
- Existing testing conventions (unit, integration, e2e) and coverage expectations.
- PR description, linked issue, and explicit acceptance criteria when available.

## Review Contract

Before writing findings, restate the change in concrete terms:

- **Intent:** What the change is supposed to do, in one or two sentences.
- **Scope:** Which modules, files, and runtime surfaces are touched.
- **Risk surfaces:** DI graph, request lifecycle, security, persistence, public API, performance, observability, deployment.
- **Severity rubric:** Critical, Warning, Suggestion (see Output Format).
- **Out of scope:** What this review will not cover, to avoid scope creep.

## Review Checklist

### Module Architecture and Dependency Injection

- Each feature lives in its own module with clear `imports`, `controllers`, `providers`, and `exports`.
- No circular module dependencies. `forwardRef` is justified, scoped, and not masking a design flaw.
- A feature module's `exports` array lists the specific providers or tokens consumers need, rather than re-exporting the feature module itself. Re-exporting an imported infrastructure module (for example `TypeOrmModule`, `MongooseModule`, or a `*Module.forFeature(...)` result) when downstream modules genuinely need those providers is a legitimate pattern.
- Custom providers use proper injection tokens (`Symbol` or class) instead of bare strings when feasible.
- Provider scope (`DEFAULT`, `REQUEST`, `TRANSIENT`) matches the intended lifecycle and is not used to paper over hidden state.
- Dynamic modules expose `forRoot`/`forRootAsync` consistently and validate options.
- Global modules (`@Global()`) are rare, intentional, and documented.
- No direct `new SomeService()` for `@Injectable()` classes; constructor injection only.

### Controllers and Request Lifecycle

- Controllers are thin: parse input, call services, return DTOs.
- HTTP method, path, status codes, and content-types are correct and consistent.
- Parameters use typed pipes (`ParseUUIDPipe`, `ParseIntPipe`, custom pipes) instead of raw casts.
- Request bodies are typed DTOs validated by `class-validator`; raw `req.body` is not passed to services.
- Response shape is a typed DTO or serializer output, not a raw entity exposing internal fields.
- Cross-cutting concerns (logging, caching, transformation) live in interceptors, not controller bodies.
- Filter/guard/interceptor/pipe execution order is correctly understood and respected.

### DTOs, Validation, and Serialization

- Global `ValidationPipe` is configured with `whitelist: true`, `forbidNonWhitelisted: true`, and `transform: true` for public APIs unless documented otherwise.
- Every request DTO uses `class-validator` decorators; optional fields are marked explicitly.
- Response DTOs or serializers prevent leakage of passwords, secrets, tokens, audit columns, and internal IDs that should not be public.
- `class-transformer` decorators (`@Expose`, `@Exclude`, `@Type`) are consistent across the codebase.
- Enums and value objects are validated, not just typed.

### Guards, Auth, and Authorization

- Authentication is enforced by guards, not by inline `if` checks in controllers.
- Guards return `boolean` or throw typed exceptions; they do not silently mutate request state in ways callers cannot see.
- Coarse access control lives in guards; resource-level ownership and tenant checks live in services where the resource is known.
- JWT strategy imports `Strategy` from `passport-jwt`; secrets come from `ConfigService`/env, not literals.
- Token verification uses `secretOrKey` (or `secretOrKeyProvider` for JWKS); `JWT_SECRET` is required to boot, not silently optional.
- Authorization decorators (`@Roles`, custom decorators) are paired with the guard that reads them.
- Rate limiting, CSRF, CORS, and security headers are explicit on public endpoints.

### Exception Handling and Errors

- Domain errors use typed NestJS exceptions (`NotFoundException`, `ConflictException`, `ForbiddenException`, custom subclasses), not generic `HttpException(message, 500)`.
- A single, consistent error envelope is returned by global exception filters.
- Internal stack traces, ORM error messages, and secrets are not leaked to clients.
- Unexpected failures are logged with correlation IDs and a stable error code.
- Async paths in controllers, services, and interceptors are awaited or returned; no floating promises.

### Configuration and Bootstrap

- `ConfigModule` is loaded with `isGlobal: true` (or imported consistently) and validates env at boot (Joi/Zod/etc.).
- No hardcoded secrets, hostnames, ports, or credentials in source.
- Bootstrap configures global pipes, filters, interceptors, and security middleware once, not per route.
- App fails fast on invalid config instead of booting partially.
- Logger is set up before request handling; structured logging and request correlation IDs are enabled in production.

### Persistence and Transactions

- ORM code is hidden behind providers that speak domain language (repository/service).
- Entities use the correct decorators (`@Column()` not `@Column('description')` accidentally).
- Multi-step writes are wrapped in transactions owned by the service that owns the unit of work.
- N+1 query patterns are avoided (eager joins, relations, or DataLoader).
- Connection failures are handled with retries/backoff or explicit fail-open vs fail-closed decisions; one bad migration must not silently corrupt data.
- Migrations are present for schema changes; `synchronize: true` is not used in production code paths.

### Testing

- Services have unit tests with mocked dependencies via `Test.createTestingModule`.
- Controllers have integration or e2e tests using `@nestjs/testing` and Supertest where appropriate.
- ORM repositories are mocked with `getRepositoryToken(Entity)` or equivalent.
- Tests reuse the same global pipes/filters/interceptors as production where they exercise validation behavior.
- Async expectations use `await expect(...).rejects.toThrow(...)`/`resolves.toEqual(...)` rather than swallowing rejections.
- Tests assert behavior, not implementation details such as private method call counts.

### API Design and Documentation

- OpenAPI/Swagger decorators (`@ApiTags`, `@ApiOperation`, `@ApiResponse`, `@ApiProperty`) are present on public endpoints.
- API versioning strategy is consistent (URI, header, or media type) when present.
- Pagination, filtering, and sorting follow a single convention across endpoints.
- Backward compatibility is preserved or breaking changes are flagged explicitly.

### Performance and Observability

- Expensive endpoints have caching or memoization where appropriate; cache keys include tenant/user scoping where relevant.
- Compression, keep-alive, and timeouts are configured for production.
- Metrics, tracing, and structured logs include request IDs and key business attributes.
- Memory and connection cleanup happen in `onModuleDestroy`/lifecycle hooks for long-lived resources.

### Microservices and Messaging (when applicable)

- Transport-specific constraints are respected (Kafka, NATS, gRPC, RabbitMQ, Redis).
- Message handlers are idempotent or document why they are not.
- Health checks are exposed for orchestrators.
- Backpressure and consumer concurrency are explicit, not accidental.

## Common Anti-Patterns to Flag

- Fat controllers that contain business logic, DB calls, or domain rules.
- Direct ORM access from controllers; controllers should not coordinate multi-step writes.
- `new SomeService()` for an `@Injectable()` class.
- `forwardRef` used reactively instead of refactoring shared logic into a third module.
- `any` types on DTOs, return types, or request handlers.
- Catch-and-rethrow patterns that turn typed exceptions into `HttpException(error.message, 500)`.
- Authorization logic inside controller handlers instead of guards or services.
- Returning raw ORM entities that expose passwords, tokens, audit columns, or relations not intended for clients.
- Tests that import the real database or hit real external services without an explicit reason.
- A feature module exporting itself instead of its intended providers, e.g. a `UsersModule` that declares `exports: [UsersModule]` rather than `exports: [UsersService]`. Re-exporting an imported infrastructure module such as `TypeOrmModule` or `MongooseModule` from an infrastructure module is not the same anti-pattern when consumers genuinely need those providers.

## Review Procedure

1. Confirm intent, scope, and out-of-scope, in one or two sentences each.
2. Map the diff to risk surfaces: DI graph, request lifecycle, security, persistence, public API, performance, observability.
3. Walk the Review Checklist for each surface touched by the diff.
4. For each potential issue, capture file path, line range, the exact code snippet, the impact, and a concrete fix.
5. Validate findings: each Critical or Warning must have reproducible evidence and an actionable remediation. Demote or remove style-only or speculative items.
6. Acknowledge positive patterns: well-scoped modules, good DI, tight DTOs, good tests.
7. Produce the structured report (see Output Format).

## Output Format

Return:

- **Summary:** Intent, scope, and overall quality signal in two or three sentences.
- **Critical (must fix):** Security, correctness, data integrity, or production-breaking issues. Each item has location, evidence, impact, and a concrete fix.
- **Warnings (should fix):** Best-practice violations or maintainability risks likely to cause bugs. Same shape as Critical.
- **Suggestions (consider improving):** Readability, performance, or developer-experience improvements.
- **Positive observations:** Patterns worth keeping and amplifying.
- **Recommendations:** Prioritized next steps with code examples for the highest-impact items.
- **Residual risk:** Known gaps, deferred items, and follow-up work.

## Definition of Done

A NestJS review is not ready until:

- Intent, scope, and out-of-scope are explicit.
- Every Critical and Warning has file/line evidence and a concrete fix, not just a label.
- Findings are deduplicated and classified by severity.
- Speculative or purely stylistic comments are removed or moved to Suggestions.
- Positive observations are included so the report is not adversarial-only.
- The report distinguishes confirmed defects from defense-in-depth recommendations.
