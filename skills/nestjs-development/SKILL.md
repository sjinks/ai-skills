---
name: nestjs-development
description: "Use when: designing, scaffolding, implementing, refactoring, or debugging NestJS applications: modules, controllers, services, DI, request lifecycle, DTOs, ORM integration, auth, configuration, microservices, and production wiring, including tests that ship with a feature. Excludes dedicated test work, framework version upgrades, and review-only requests."
argument-hint: "Describe the feature or change, target module, runtime/version, ORM choice, auth strategy, transports, and existing project conventions."
---

# NestJS Development

Use this skill when designing or implementing NestJS code: a new feature, a new module, an architectural change, a refactor, or a bug fix that requires reasoning about the framework. The goal is to produce idiomatic, secure, and testable NestJS code that fits the project's existing conventions.

**UTILITY SKILL.** INVOKES: repository inspection and scoped edits/checks. FOR SINGLE OPERATIONS: Implement or propose scoped NestJS changes and their validation.

## Boundaries

- This skill is for producing NestJS code. Auditing an existing change and returning a severity-classified findings report is a separate review task and out of scope here.
- Writing the test setup that ships with a feature is in scope. A request whose primary goal is test design, test-layer strategy, repairing a failing test, or closing coverage gaps is a dedicated testing task and out of scope here.
- This skill is a guide, not a substitute for product, security, or platform decisions.
- Match the project's existing conventions even when they differ from default NestJS docs. Do not rewrite stable code to fit personal preferences.
- Do not enforce a single ORM (TypeORM/Prisma/Mongoose/Drizzle/MikroORM) or a single auth strategy; choose to match the project.
- Do not introduce new heavy infrastructure (queues, caches, brokers) unless the change clearly needs them.
- Prefer additive, reversible changes. Flag breaking changes explicitly with a migration path.
- Do not bypass safety checks (`--no-verify`, disabling validation, weakening auth) to make code compile or tests pass.

## Trigger Conditions

Use this skill when any of these apply:

- Building or modifying a NestJS module, controller, service, provider, guard, interceptor, pipe, middleware, exception filter, or custom decorator.
- Wiring dependency injection: provider arrays, exports, custom providers, factories, `forwardRef`, scoped providers, or dynamic modules.
- Adding or changing DTOs, validation, serialization, or OpenAPI/Swagger documentation.
- Adding or changing authentication or authorization (JWT, session, OAuth, Passport strategies, role/permission guards).
- Integrating an ORM (TypeORM, Prisma, Mongoose, Drizzle, MikroORM, or similar), entities, repositories, transactions, or migrations.
- Writing the test setup that ships alongside a feature being built here. A request focused on test strategy, repairing a failing test, or coverage gaps is a dedicated testing task, not this skill.
- Bootstrap changes: `main.ts`, global pipes/filters/interceptors, configuration, environment loading.
- Adding microservices transports, message handlers, or background workers.

## DO NOT USE FOR:

- Dedicated test-only work, framework version upgrades, or review-only requests.
- Changes outside the requested feature or defect.

## Required Input Context

Infer the following from the repository for the surfaces the task touches. Do not request unrelated context. If a missing fact changes the implementation or validation choice, ask for that fact before making the dependent change:

- Feature intent and acceptance criteria.
- Target module path and surrounding modules already in the codebase.
- NestJS major version, Node.js version, package manager, and TypeScript strictness.
- ORM choice and version, or "none".
- Authentication strategy and existing guards/decorators in use.
- Transports in use (HTTP, GraphQL, microservices, WebSocket).
- Existing patterns for DTOs, error handling, logging, and testing.
- Whether the project enables global `ValidationPipe`, `ClassSerializerInterceptor`, and a global exception filter.

## Architecture Principles

- **Feature modules, not technical layers.** Each module owns its controllers, services, repositories, DTOs, and tests for a single feature.
- **Thin controllers, fat services.** Controllers parse input and return DTOs; business logic lives in services.
- **Explicit DI.** Constructor injection only; no `new` on `@Injectable()` classes; no service locator. Inject through interfaces/tokens when the implementation is interchangeable.
- **Domain over framework.** Repositories and providers should expose domain operations, not raw ORM verbs leaked into the rest of the app.
- **Validate at the edge.** All inputs validated with `class-validator` DTOs and a global `ValidationPipe`. Never trust raw `req.body`.
- **Typed errors.** Use specific exceptions; one global exception filter shapes the response envelope.
- **Configuration over code.** Read environment via `ConfigModule`/`ConfigService` with schema validation; no hardcoded secrets or URLs.
- **Stable response contracts.** Use response DTOs/serializers so internal model changes do not leak into the API.

## Build Workflow

For proposal-only requests, specify the scoped implementation and planned checks without editing files or running checks. For implementation requests, follow the workflow below.

1. Identify the requested behavior and acceptance criteria. Inspect the existing implementation and project conventions.
2. Make the smallest coherent change within that scope. Use an existing feature module when it owns the behavior; create a module only for a new feature boundary. Preserve unrelated wiring.
3. Apply the architecture principles to each touched surface. If request/response contracts change, update their DTOs and controller bindings. If dependencies change, update DI. If authentication, validation, serialization, or error handling changes, update the corresponding lifecycle wiring. Do not create untouched components to fill a workflow.
4. Add regression coverage at the lowest layer that exercises the changed risk. Use integration/e2e coverage when the change depends on controller or module wiring; reuse existing coverage when it already proves the behavior.
5. Run the project's applicable typecheck, lint, and test commands. Respect command dependencies; independent checks need no fixed order. Record each command and result. If a check fails, diagnose it; if it cannot run, state the blocker and the behavior left unverified. Do not report attempted checks as passing.
6. If the public contract changes and the project maintains endpoint/module documentation, update that documentation. Stop when the scoped behavior is implemented and applicable checks pass, or report the remaining blocker.

## Examples

Read [patterns](references/patterns.md) when implementing or testing a matching surface; it illustrates modules, providers, lifecycle wiring, and assertions. Examples do not expand the task scope.

## Anti-Patterns to Avoid

- Fat controllers with business logic, DB calls, or domain rules.
- Direct ORM access from controllers; controllers should not coordinate multi-step writes.
- `new SomeService()` for an `@Injectable()` class.
- Using `forwardRef` to "fix" a circular dependency without considering a third shared module.
- `any` on DTOs, return types, or repository methods.
- Catching and rewrapping typed exceptions into a generic `HttpException(error.message, 500)`.
- Authorization inside controller handlers instead of guards.
- Returning raw ORM entities that expose passwords, tokens, or audit columns.
- Hardcoded secrets, hostnames, or ports.
- `synchronize: true` against a production database.
- Tests that depend on the real database, real auth provider, or real network without an explicit reason.

## Decision Hints

Use these only when the project has no established convention for the decision in
question. Existing project conventions, ADRs, and team standards always win; do not
propose a change of ORM, auth strategy, or test layering just to match a hint below.

- **ORM (greenfield only):** if the project has no ORM yet, candidates include
  Prisma (strong type-safety, first-class migrations), TypeORM (mature legacy
  schema and complex relational mapping), Mongoose (MongoDB), Drizzle, or
  MikroORM. Match the team's familiarity and operational constraints rather than
  picking by feature list.
- **Module shape:** simple CRUD → single module with controller and service;
  domain logic → domain module plus infrastructure; shared logic → dedicated
  shared module with explicit exports.
- **Auth (greenfield only):** if no auth strategy is in place, common shapes are
  stateless API with JWT and refresh tokens, multi-tenant with tenant claims, or
  service-to-service with mTLS or signed tokens. Follow whatever the project
  already uses.
- **Caching:** user-specific → Redis with user-key prefix; computed values →
  in-memory with TTL. Reuse the project's existing cache layer when one exists.
- **Testing:** services → unit tests with mocks; controllers and contracts → e2e
  with Supertest; long-running flows → focused integration tests. Match the
  project's existing test layering and tooling.
- **Microservices testing:** message handlers → unit tests that assert
  idempotent handling of redelivered messages; transport contracts (Kafka,
  NATS, gRPC, RabbitMQ) → integration tests against the project's existing
  broker fixtures or test containers, covering delivery-failure, retry, and
  out-of-order cases the transport allows. Document any handler that is
  intentionally not idempotent in a comment or docstring on the handler
  itself, plus the project's usual decision record (ADR or service README)
  when one exists.

## Output Format

Return these labels in this order. Include only components the task requires. For repository edits, link changed files under Code instead of repeating their complete contents; for a proposal, include the proposed code:

1. **Intent and scope:** one or two sentences.
2. **Module layout:** files to add or modify, with paths.
3. **Code:** changed or proposed components; keep code idiomatic and minimal.
4. **DI and bootstrap notes:** any global pipe/filter/interceptor, config, or env additions.
5. **Tests:** unit tests for service logic; integration/e2e for the controller path.
6. **Validation steps:** commands and results, or checks not run with reasons. Include integration/e2e only when the changed risk requires that layer.
7. **Risks and follow-ups:** anything intentionally deferred, with a short rationale.

## Error Handling

If the behavior or target is unavailable, stop dependent edits and report the missing input under the existing output labels. If only part of the task is blocked, complete independent authorized work and identify the blocked part. Record unavailable validation under the validation/run label; do not fabricate code, test results, or readiness.

## Definition of Done

For proposals, define how each applicable gate will be checked and report execution as not run; do not claim implementation readiness. For implemented changes, apply these gates to the surfaces the change touches. Unchanged components do not require new scaffolding. A NestJS change is not ready until:

- Intent and scope are explicit.
- The module is feature-scoped with clear `imports`, `controllers`, `providers`, and `exports`.
- Inputs are validated through DTOs with `class-validator` and a global `ValidationPipe`.
- Services throw typed exceptions; controllers do not own business logic.
- Guards and decorators (not inline checks) enforce authentication and authorization.
- Configuration and secrets come from `ConfigModule` with validation.
- Unit tests cover service logic; integration/e2e tests cover the controller path where it matters.
- Typecheck, lint, and tests pass before the change is offered for review.
