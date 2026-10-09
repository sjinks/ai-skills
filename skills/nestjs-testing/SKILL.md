---
name: nestjs-testing
description: "Use when: designing test strategy, writing, or fixing tests for NestJS applications; choosing unit vs integration vs e2e layering, building the testing module with @nestjs/testing, overriding providers, guards, interceptors, and pipes, mocking repositories and ORM tokens, writing Supertest e2e tests, testing async and error paths, faking transports for microservices, designing fixtures, and triaging flaky or coverage-gap tests."
argument-hint: "Describe what needs testing, the test layer, NestJS/Node version, ORM choice, auth strategy, transports, and existing test conventions."
---

# NestJS Testing

Use this skill when the task is to verify NestJS behavior with tests: choosing the right test layer, building a testing module, overriding dependencies, asserting behavior and error paths, and closing coverage gaps. The goal is a test plan and tests that catch real regressions, run deterministically, and reuse production wiring where it matters.

**UTILITY SKILL.** INVOKES: repository inspection and scoped edits/checks. FOR SINGLE OPERATIONS: Design, implement, or repair tests for specified NestJS behavior.

## Boundaries

- This skill is for verifying NestJS behavior with tests and reporting coverage gaps. Designing or implementing the feature under test is a separate build task, and judging an entire change with a severity-classified review report is a separate review task; both are out of scope here.
- Repairing a test that broke because of a logic or wiring change is in scope. A test failing because of a NestJS version or major-dependency bump is a version-upgrade task and out of scope here; fix the upgrade first, then return to test design.
- Match the project's existing test runner, layering, and conventions even when they differ from default NestJS docs. Do not migrate Jest to Vitest (or the reverse) unless asked.
- Do not enforce a single ORM (TypeORM, Prisma, Mongoose, Drizzle, MikroORM) or a single auth strategy; mock against the project's chosen stack.
- Do not weaken assertions, add `--forceExit`, or skip tests to make a suite pass. Fix the cause.
- Tests must not depend on a real database, real auth provider, or real network unless the test is explicitly an integration test with managed fixtures (test containers, ephemeral DB).
- Prefer additive tests. When changing an existing test, preserve the behavior it was protecting unless that behavior is the bug.

## Trigger Conditions

Use this skill when any of these apply:

- Adding or changing unit tests for services, providers, guards, interceptors, pipes, or custom decorators.
- Adding or changing integration or e2e tests for controllers, the request lifecycle, or full module wiring.
- Building a testing module: `Test.createTestingModule`, `overrideProvider`, `overrideGuard`, `overrideInterceptor`, `overridePipe`, `compile`.
- Mocking dependencies: repository tokens (`getRepositoryToken`, `getModelToken`), `ConfigService`, external clients, or custom provider tokens.
- Writing HTTP assertions with Supertest against `app.getHttpServer()`.
- Testing async behavior, rejected promises, thrown exceptions, or validation failures.
- Faking microservice transports or message handlers (Kafka, NATS, gRPC, RabbitMQ, Redis).
- Designing fixtures, factories, or seed data for tests.
- Triaging flaky tests, slow suites, or coverage gaps on high-risk flows.

## DO NOT USE FOR:

- Feature implementation, whole-change code review, or framework version upgrades.
- Test-runner migration unless requested.

## Required Input Context

Infer the following from the repository for the behavior under test. Do not request unrelated stack details. If a missing fact changes the test layer, wiring, or assertion, ask for that fact before writing the dependent test:

- What behavior must be verified, and the acceptance criteria or bug it guards.
- Target files and the modules/providers they depend on.
- Test runner and version (Jest, Vitest), and whether `ts-jest` or SWC is used.
- NestJS major version and Node.js version.
- ORM choice and version, or "none" — needed to pick the right repository-token mock.
- Authentication strategy and the guards/decorators that gate the code under test.
- Transports in use (HTTP, GraphQL, microservices, WebSocket).
- Whether the app enables a global `ValidationPipe`, `ClassSerializerInterceptor`, or global filters that the test must reproduce.
- Existing test layering, fixtures, factories, and naming conventions.

## Test Layer Decision

Choose the lowest layer that still exercises the risk. Use a higher layer only when the behavior lives in the wiring.

- **Unit** — service/provider business logic, branching, and error paths. Mock every injected dependency. Fastest; default for logic.
- **Integration** — a slice of real wiring: a service plus its real repository against an ephemeral DB, or a guard plus the decorator it reads. Use when the bug lives in the interaction, not the unit.
- **e2e** — the full HTTP path through `NestFactory`/`createTestingModule` + Supertest: routing, pipes, guards, filters, serialization. Use for contract behavior, validation rejection, auth enforcement, and status/shape of responses.

If a unit test proves the changed behavior and no wiring risk remains, add or update that unit test without adding an e2e smoke test. Add integration/e2e coverage only for a specific wiring or request-contract risk that lower layers do not exercise. Check existing coverage before adding a duplicate test.

## Test Plan Workflow

For plan-only requests, define cases, wiring, fixtures, and commands without editing files or running tests. Skip implementation and execution steps; report Run steps as proposed commands, not results. For test-writing or repair requests, follow all applicable steps below.

1. **Restate the behavior to verify** and its acceptance criteria in one or two sentences.
2. **Enumerate applicable cases:** happy path, each error path (not-found, conflict, forbidden, validation failure), boundary inputs, and async rejection. List idempotency/retry cases for message handlers.
3. **Assign a layer** to each case using the Test Layer Decision.
4. **Plan the testing module:** which real providers to keep, which to mock, and which guards/pipes/filters to override or reproduce.
5. **Plan fixtures:** factories or builders for entities/DTOs; deterministic clock and IDs where time or randomness matters.
6. **Write tests** at the assigned layer; assert observable behavior (return value, thrown exception type, HTTP status and body), not private call counts.
7. **Run the focused suite.** Fix failures at the layer that exposes them. Widen only when shared wiring, broader affected behavior, or repository-required checks need verification. Record commands and results; if execution is unavailable, report the reason and do not claim verified behavior.
8. **Report coverage gaps:** behaviors still unverified and why, with the layer each gap belongs to.

## Examples

Read [patterns](references/patterns.md) when implementing or testing a matching surface; it illustrates modules, providers, lifecycle wiring, and assertions. Examples do not expand the task scope.

## Anti-Patterns to Avoid

- Adding an e2e smoke test for unit-testable behavior without an additional wiring or request-contract risk.
- Asserting private method call counts or internal implementation instead of observable behavior.
- e2e tests that skip the production global `ValidationPipe`/filters, so validation and error-shape behavior is never actually exercised.
- Tests that hit a real database, real auth provider, or real network without an explicit integration-test reason and managed fixtures.
- Swallowing rejected promises: `service.create(...)` without `await expect(...).rejects` or a `try/catch` assertion.
- Not awaiting async expectations, so failures pass silently.
- `overrideGuard` that always returns `true` for tests whose whole point is to verify the guard denies access.
- Shared mutable fixture state between tests without reset (`jest.clearAllMocks()`, fresh module per test) causing order-dependent flakes.
- `any`-typed mocks that drift from the real provider's contract and hide breakage.
- Snapshotting large response bodies instead of asserting the few fields the behavior owns.

## Decision Hints

Use these only when the project has no established convention. Existing test layering and tooling always win.

- **Layer:** apply the Test Layer Decision section above; pick the lowest layer that proves the behavior.
- **Guard in e2e:** verifying the protected behavior → override the guard to allow; verifying the guard itself → keep the real guard and assert 401/403.
- **DB in integration tests:** prefer test containers or an ephemeral schema per worker over a shared dev database; reset state between tests.
- **Fixtures:** repeated entity shapes → a factory/builder with overridable fields; time- or randomness-dependent logic → inject a fake clock and seeded ID generator.
- **Microservices:** handler logic → unit test asserting idempotent handling of redelivered messages; transport contract → integration test against the project's broker fixtures covering delivery-failure, retry, and out-of-order cases the transport allows.

## Output Format

Return these labels in this order. For repository edits, link changed tests instead of repeating their complete contents; for a proposal, include the proposed test code:

1. **Behavior under test:** one or two sentences plus the acceptance criteria or bug it guards.
2. **Case list:** each case with its assigned layer (unit / integration / e2e).
3. **Testing module plan:** real providers kept, dependencies mocked, guards/pipes/filters overridden or reproduced.
4. **Tests:** code at the assigned layer, idiomatic and minimal, assertions on observable behavior.
5. **Fixtures:** factories, builders, fake clock/IDs introduced.
6. **Run steps:** focused commands and actual results, or proposed commands with reasons they were not run.
7. **Coverage gaps:** behaviors still unverified, the layer each belongs to, and why deferred.

## Error Handling

If the behavior or target is unavailable, stop dependent edits and report the missing input under the existing output labels. If only part of the task is blocked, complete independent authorized work and identify the blocked part. Record unavailable validation under the validation/run label; do not fabricate code, test results, or readiness.

## Definition of Done

For plan-only requests, these gates describe the planned coverage and checks; execution remains not run, and the plan does not establish tested behavior. For test-writing or repair requests, a NestJS testing task is not ready until:

- The behavior under test and its acceptance criteria are explicit.
- Each case is assigned the lowest layer that proves it.
- The testing module mocks external dependencies and reproduces the production pipes/filters that the assertions depend on.
- Applicable happy paths, error paths, and async rejection are asserted on observable behavior, not private internals. Do not invent paths outside the behavior under test.
- Async expectations are awaited; no floating rejected promises.
- Tests run deterministically, with reset state and no reliance on real DB/auth/network unless an explicit integration test with managed fixtures.
- Test commands and their results are recorded. If they cannot run, readiness remains unverified and the blocker is reported.
- Remaining coverage gaps are reported with the layer they belong to.
