---
name: nestjs-testing
description: "Use when: designing test strategy, writing, or fixing tests for NestJS applications; choosing unit vs integration vs e2e layering, building the testing module with @nestjs/testing, overriding providers, guards, interceptors, and pipes, mocking repositories and ORM tokens, writing Supertest e2e tests, testing async and error paths, faking transports for microservices, designing fixtures, and triaging flaky or coverage-gap tests."
argument-hint: "Describe what needs testing, the test layer, NestJS/Node version, ORM choice, auth strategy, transports, and existing test conventions."
user-invocable: true
---

# NestJS Testing

Use this skill when the task is to verify NestJS behavior with tests: choosing the right test layer, building a testing module, overriding dependencies, asserting behavior and error paths, and closing coverage gaps. The goal is a test plan and tests that catch real regressions, run deterministically, and reuse production wiring where it matters.

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

## Required Input Context

Collect before designing or writing tests:

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

If a behavior can be proven at the unit layer, do not promote it to e2e just for confidence; add a focused unit test plus one e2e smoke test for the path.

## Test Plan Workflow

1. **Restate the behavior to verify** and its acceptance criteria in one or two sentences.
2. **Enumerate cases:** happy path, each error path (not-found, conflict, forbidden, validation failure), boundary inputs, and async rejection. List idempotency/retry cases for message handlers.
3. **Assign a layer** to each case using the Test Layer Decision.
4. **Plan the testing module:** which real providers to keep, which to mock, and which guards/pipes/filters to override or reproduce.
5. **Plan fixtures:** factories or builders for entities/DTOs; deterministic clock and IDs where time or randomness matters.
6. **Write tests** at the assigned layer; assert observable behavior (return value, thrown exception type, HTTP status and body), not private call counts.
7. **Run the focused suite,** fix the lowest-layer failure first, then widen.
8. **Report coverage gaps:** behaviors still unverified and why, with the layer each gap belongs to.

## Common Patterns

### Service unit test with mocked repository

```typescript
describe('UsersService', () => {
  let service: UsersService;
  const users = { findByEmail: jest.fn(), create: jest.fn(), findById: jest.fn() };

  beforeEach(async () => {
    const moduleRef = await Test.createTestingModule({
      providers: [UsersService, { provide: UsersRepository, useValue: users }],
    }).compile();
    service = moduleRef.get(UsersService);
    jest.clearAllMocks();
  });

  it('throws ConflictException when the email is taken', async () => {
    users.findByEmail.mockResolvedValue({ id: '1' });
    await expect(service.create({ email: 'a@b.c', password: 'x' })).rejects.toThrow(ConflictException);
  });

  it('returns a response DTO on success', async () => {
    users.findByEmail.mockResolvedValue(null);
    users.create.mockResolvedValue({ id: '1', email: 'a@b.c' });
    await expect(service.create({ email: 'a@b.c', password: 'x' })).resolves.toMatchObject({ id: '1' });
  });
});
```

### Mocking an ORM repository token

```typescript
// TypeORM
const moduleRef = await Test.createTestingModule({
  providers: [
    UsersService,
    { provide: getRepositoryToken(User), useValue: { findOne: jest.fn(), save: jest.fn() } },
  ],
}).compile();

// Mongoose
//   { provide: getModelToken(User.name), useValue: { findById: jest.fn() } }
// Prisma
//   { provide: PrismaService, useValue: { user: { findUnique: jest.fn(), create: jest.fn() } } }
```

### Overriding a guard in an e2e test

```typescript
describe('UsersController (e2e)', () => {
  let app: INestApplication;

  beforeAll(async () => {
    const moduleRef = await Test.createTestingModule({ imports: [AppModule] })
      .overrideGuard(JwtAuthGuard)
      .useValue({ canActivate: () => true })
      .compile();

    app = moduleRef.createNestApplication();
    app.useGlobalPipes(new ValidationPipe({ whitelist: true, transform: true }));
    await app.init();
  });

  afterAll(async () => {
    await app.close();
  });

  it('rejects an invalid body with 400', () => {
    return request(app.getHttpServer()).post('/users').send({}).expect(400);
  });

  it('creates a user with 201', () => {
    return request(app.getHttpServer())
      .post('/users')
      .send({ email: 'a@b.c', password: 'sup3rsecret' })
      .expect(201);
  });
});
```

### Asserting async rejection and validation failure

```typescript
await expect(service.findOne('missing')).rejects.toBeInstanceOf(NotFoundException);
await expect(service.findOne('missing')).rejects.toThrow(/not found/i);
```

### Idempotent message-handler test

```typescript
it('processes a redelivered message exactly once', async () => {
  const msg = { id: 'evt-1', payload: { orderId: 'o-1' } };
  await handler.handle(msg);
  await handler.handle(msg); // redelivery
  expect(orders.markPaid).toHaveBeenCalledTimes(1);
});
```

## Anti-Patterns to Avoid

- Promoting a unit-testable behavior to e2e just for confidence instead of a focused unit test plus one smoke test.
- Asserting private method call counts or internal implementation instead of observable behavior.
- e2e tests that skip the production global `ValidationPipe`/filters, so validation and error-shape behavior is never actually exercised.
- Tests that hit a real database, real auth provider, or real network without an explicit integration-test reason and managed fixtures.
- Swallowing rejected promises: `service.create(...)` without `await expect(...).rejects` or a `try/catch` assertion.
- Not awaiting async expectations, so failures pass silently.
- `overrideGuard` that always returns `true` for tests whose whole point is to verify the guard denies access.
- Shared mutable fixture state between tests without reset (`jest.clearAllMocks`, fresh module per test) causing order-dependent flakes.
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

When proposing a test plan or tests, return in this order:

1. **Behavior under test:** one or two sentences plus the acceptance criteria or bug it guards.
2. **Case list:** each case with its assigned layer (unit / integration / e2e).
3. **Testing module plan:** real providers kept, dependencies mocked, guards/pipes/filters overridden or reproduced.
4. **Tests:** code at the assigned layer, idiomatic and minimal, assertions on observable behavior.
5. **Fixtures:** factories, builders, fake clock/IDs introduced.
6. **Run steps:** the focused command(s) to run, lowest layer first.
7. **Coverage gaps:** behaviors still unverified, the layer each belongs to, and why deferred.

## Definition of Done

A NestJS testing task is not ready until:

- The behavior under test and its acceptance criteria are explicit.
- Each case is assigned the lowest layer that proves it.
- The testing module mocks external dependencies and reproduces the production pipes/filters that the assertions depend on.
- Happy path, error paths, and async rejection are each asserted on observable behavior, not private internals.
- Async expectations are awaited; no floating rejected promises.
- Tests run deterministically, with reset state and no reliance on real DB/auth/network unless an explicit integration test with managed fixtures.
- Remaining coverage gaps are reported with the layer they belong to.
