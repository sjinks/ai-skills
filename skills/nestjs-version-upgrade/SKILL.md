---
name: nestjs-version-upgrade
description: "Use when: planning or executing a NestJS version upgrade or major migration; bumping @nestjs/* across majors, upgrading the underlying platform adapter (Express or Fastify), bumping RxJS or TypeScript, triaging breaking changes and deprecations, sequencing peer-dependency and ORM/Passport/config-package bumps, updating bootstrap and decorator usage, and producing a reversible, verifiable upgrade plan."
argument-hint: "Describe the current and target NestJS versions, platform adapter, Node/TypeScript versions, ORM and auth packages, and how the app is tested and deployed."
user-invocable: true
---

# NestJS Version Upgrade

Use this skill when the task is to move a NestJS app across versions: a major `@nestjs/*` bump, a platform-adapter swap, an RxJS or TypeScript bump driven by Nest, or triaging the breaking changes that come with them. The goal is an ordered, reversible upgrade plan where each step has a verification check and a rollback path, so the app never sits in a half-migrated, unverifiable state.

## Boundaries

- This skill is for upgrading or migrating an existing NestJS app across versions. Designing a new feature, judging a change with a severity-classified review report, or writing the app's test suite are separate tasks and out of scope here.
- Triaging a test, build, or runtime failure that appeared because of a version or major-dependency bump is in scope. General test design, layering, or repairing a test that broke from a logic change is a dedicated testing task and out of scope here.
- Do not invent breaking-change facts. When the exact deprecation or removal for a target version is uncertain, say so and direct the user to the official migration guide and the package CHANGELOG rather than guessing.
- Respect the project's package manager, lockfile, and existing pinning policy. Do not switch package managers or unpin everything to force a resolve.
- Do not bump across more than one major at a time when intermediate majors exist; step through majors in order unless the project explicitly skips.
- Prefer reversible steps. Every step must be reversible via lockfile/VCS before the next step starts.
- Do not weaken or delete tests, types, or validation to make the build pass after a bump. Fix the call site or pin the dependency instead.

## Trigger Conditions

Use this skill when any of these apply:

- Bumping `@nestjs/core`, `@nestjs/common`, or other `@nestjs/*` packages across a major version.
- Upgrading the platform adapter: `@nestjs/platform-express` to a new Express major, or switching to / upgrading `@nestjs/platform-fastify`.
- Bumping RxJS, TypeScript, or Node.js because a NestJS upgrade requires it.
- Triaging build, type, or runtime errors that appear after a NestJS dependency bump.
- Updating peer dependencies that track NestJS majors: `@nestjs/config`, `@nestjs/swagger`, `@nestjs/typeorm`/`@nestjs/mongoose`, `@nestjs/passport`, `@nestjs/jwt`, testing utilities.
- Replacing deprecated bootstrap, decorator, or lifecycle APIs flagged by a new major.
- Planning a staged rollout of a framework upgrade across services or a monorepo.

## Required Input Context

Collect before planning the upgrade:

- Current and target NestJS major versions (and whether intermediate majors are being skipped).
- Platform adapter in use (Express or Fastify) and its version.
- Node.js and TypeScript versions, and the project's `tsconfig` strictness.
- Package manager and lockfile (npm, pnpm, yarn) and the pinning policy.
- ORM and version, auth packages (`@nestjs/passport`, `@nestjs/jwt`, Passport strategies), and other `@nestjs/*` peers in use.
- How the app is tested (unit, e2e) and the command that proves it green.
- How the app is built and deployed, and whether a staged rollout is possible.
- Any custom platform-adapter usage, raw `req`/`res` access, or framework internals the app reaches into.

## Upgrade Workflow

1. **Establish the baseline.** Confirm the suite is green and the build is clean on the current version before changing anything. If it is not, stop — fix or record that first.
2. **Read the official migration guide and CHANGELOG** for each major between current and target. Extract the breaking changes and deprecations that touch this app's surfaces.
3. **Map breaking changes to this codebase.** For each, find the call sites (bootstrap, decorators, adapter usage, peer-package APIs). List the ones that actually apply; mark the rest not-applicable.
4. **Sequence the bumps.** Step through majors in order. Within a step, bump `@nestjs/*` together with their matching peers (adapter, swagger, config, ORM/passport bridges) and the RxJS/TypeScript versions that major requires.
5. **Plan each step as reversible.** Each step bumps a coherent set, updates the affected call sites, and ends with a verification check (typecheck, build, unit, then e2e). Define the rollback (revert lockfile + the step's edits).
6. **Execute one step at a time.** Apply the bump, fix call sites at the lowest layer the error exposes, run the verification check, and only then move on.
7. **Re-verify peers and runtime.** After the framework is on the target major, confirm peer packages are on compatible majors and the app boots and serves a request, not just compiles.
8. **Record residual risk.** Note deprecations deferred (still working but slated for removal), pinned-back packages, and follow-up work.

## Sequencing Rules

- One major at a time. Do not jump two majors when an intermediate exists; verify green between majors.
- Bump the framework and its first-party peers in the same step — a `@nestjs/core` major with a mismatched `@nestjs/swagger` or `@nestjs/config` major is a common break source.
- Bump RxJS and TypeScript only to the versions the target Nest major requires; do not opportunistically jump them further in the same step.
- Upgrade the platform adapter deliberately. An Express major bump or an Express-to-Fastify swap changes request/response objects, body parsing, and middleware signatures — treat it as its own step with its own verification.
- Update lockfile-pinned transitive peers explicitly rather than relying on a broad range resolve.
- Keep deprecation fixes (replacing a still-working deprecated API) in a separate commit from the breaking bump, so a regression can be bisected.

## Common Breaking-Change Surfaces

Check these surfaces against the target version's migration guide — they are where Nest majors most often break apps. Do not assume the direction of a change; confirm each against the guide for the specific target.

- **Bootstrap (`main.ts`)** — global pipe/filter/interceptor registration, `NestFactory` options, adapter creation, body-parser and CORS configuration.
- **Platform adapter** — raw `req`/`res` typing and helpers differ between Express and Fastify; an adapter swap changes them.
- **Decorators and metadata** — `@nestjs/swagger`, custom-decorator and `Reflector` APIs, and `class-transformer`/`class-validator` peer ranges.
- **RxJS** — operator imports and behavior changes that ride along with a required RxJS bump.
- **TypeScript** — stricter inference or decorator-metadata changes surfacing as new type errors.
- **Microservices transports** — client/server option shapes and transport package versions.
- **First-party peers** — `@nestjs/config`, `@nestjs/typeorm`/`@nestjs/mongoose`, `@nestjs/passport`, `@nestjs/jwt`, testing utilities tracking the framework major.

## Example Ordered Step

One reversible step for a 9 → 10 → 11 upgrade. Version numbers are illustrative;
confirm the actual compatible ranges against each package's migration guide and
CHANGELOG.

```text
Step 1 of 2 — NestJS 9 → 10
  Bump together: @nestjs/core, @nestjs/common, @nestjs/platform-express,
    @nestjs/swagger, @nestjs/config, @nestjs/typeorm, @nestjs/passport
    (each to its 10-compatible major), plus the RxJS/TS versions Nest 10 requires.
  Call-site edits: migrate the breaking changes mapped earlier (e.g. main.ts
    global-pipe and CORS setup) — do not @ts-ignore them.
  Verify: typecheck → build → unit → e2e → boot the app and serve one request.
  Rollback: revert the lockfile and this step's edits via VCS; the app returns
    to the green 9 baseline.
(Only after this step is green, proceed to Step 2 — NestJS 10 → 11.)
```

## Anti-Patterns to Avoid

- Bumping every `@nestjs/*` package and its peers in one giant commit, so a failure cannot be bisected.
- Jumping two or more majors at once when intermediate majors exist.
- Bumping `@nestjs/core` while leaving `@nestjs/swagger`, `@nestjs/config`, or an ORM bridge on the old major.
- Deleting or `// @ts-ignore`-ing failing call sites instead of migrating them to the new API.
- Loosening or removing tests, types, or validation to get a green build after a bump.
- Treating an Express-to-Fastify swap as a drop-in dependency change rather than a request/response contract change.
- Declaring success on a clean typecheck without booting the app and serving a real request.
- Guessing a breaking-change behavior instead of confirming it in the official migration guide and CHANGELOG.

## Decision Hints

Use these only when the project has no established policy.

- **Adapter choice during an upgrade:** stay on the current adapter unless there is a concrete reason to switch; an Express-to-Fastify swap is a behavior migration, not a version bump, and belongs in its own change.
- **Skipping intermediate majors:** prefer stepping through each major and verifying green between them; skip only when the migration guides explicitly support a direct jump and the suite proves it.
- **Deferring deprecations:** a still-working deprecated API can be deferred to a follow-up if it is documented; a removed API must be migrated in the step that removes it.
- **Pinning vs ranges:** when a transitive peer breaks on the new major, pin it back to the last compatible version and record the pin, rather than unpinning the framework.

## Output Format

When proposing an upgrade, return in this order:

1. **Upgrade summary:** current → target versions, adapter, and the number of major steps.
2. **Baseline check:** confirmation the suite/build is green now, or what must be fixed first.
3. **Breaking-change map:** each applicable breaking change with its call sites in this codebase, plus the not-applicable ones noted briefly.
4. **Ordered steps:** each step lists the packages bumped (framework + peers + RxJS/TS), the call-site edits, the verification check, and the rollback.
5. **Code changes:** the concrete edits (bootstrap, decorators, adapter usage) per step, minimal and idiomatic.
6. **Verification:** the commands to run per step, lowest layer first, ending with a boot-and-serve check.
7. **Residual risk:** deferred deprecations, pinned-back packages, and follow-ups.

## Definition of Done

A NestJS upgrade is not ready until:

- Current and target versions, adapter, and major-step count are explicit.
- The baseline was green before the first bump.
- Each major is stepped through in order, with framework and first-party peers bumped together per step.
- Every breaking change that applies has its call sites migrated; not-applicable ones are noted.
- Each step has a verification check and a defined rollback, and steps were applied one at a time.
- The app boots and serves a request on the target version, not just compiles.
- Tests, types, and validation are intact — none weakened to force a green build.
- Deferred deprecations, pinned packages, and follow-ups are recorded.
