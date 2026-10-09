# nestjs-testing

> Use when: designing test strategy, writing, or fixing tests for NestJS applications; choosing unit vs integration vs e2e layering, building the testing module with @nestjs/testing, overriding providers, guards, interceptors, and pipes, mocking repositories and ORM tokens, writing Supertest e2e tests, testing async and error paths, faking transports for microservices, designing fixtures, and triaging flaky or coverage-gap tests.

This skill is aimed at verifying NestJS behavior with tests: picking the right layer, building a testing module, overriding dependencies, asserting behavior and error paths, and closing coverage gaps so the suite catches real regressions and runs deterministically.

It helps an assistant:

- identify the behavior to verify, enumerate applicable cases, and assign each the lowest test layer that proves it without mandatory e2e smoke tests
- build a testing module with `@nestjs/testing`: keep real providers where needed, mock repositories via `getRepositoryToken`/`getModelToken`, and override guards, pipes, interceptors, and filters
- use idiomatic patterns for service unit tests, Supertest e2e tests, async-rejection assertions, and idempotent message-handler tests
- avoid anti-patterns such as asserting private call counts, skipping the production `ValidationPipe` in e2e, hitting a real database without managed fixtures, and unawaited async expectations
- report remaining coverage gaps with the layer each belongs to

## Files

- [`SKILL.md`](SKILL.md) — operational workflow, decision rules, output contract, and completion gates.
- [`references/patterns.md`](references/patterns.md) — partial implementation and test illustrations.
