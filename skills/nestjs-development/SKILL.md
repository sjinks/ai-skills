---
name: nestjs-development
description: "Use when: designing, scaffolding, implementing, refactoring, or debugging NestJS applications; building modules, controllers, services, providers, guards, interceptors, pipes, exception filters, DTOs, validation, configuration, TypeORM/Prisma/Mongoose integration, authentication, authorization, testing, microservices, or production wiring."
argument-hint: "Describe the feature or change, target module, runtime/version, ORM choice, auth strategy, transports, and existing project conventions."
user-invocable: true
---

# NestJS Development

Use this skill when designing or implementing NestJS code: a new feature, a new module, an architectural change, a refactor, or a bug fix that requires reasoning about the framework. The goal is to produce idiomatic, secure, and testable NestJS code that fits the project's existing conventions.

## Boundaries

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
- Integrating an ORM (TypeORM/Prisma/Mongoose), entities, repositories, transactions, or migrations.
- Adding or fixing tests: unit, integration, or e2e with `@nestjs/testing` and Supertest.
- Bootstrap changes: `main.ts`, global pipes/filters/interceptors, configuration, environment loading.
- Adding microservices transports, message handlers, or background workers.

## Required Input Context

Collect before generating or proposing code:

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

1. **Restate intent and acceptance criteria** in one or two sentences.
2. **Locate or create the module.** Place the feature in its own module; export only what other modules genuinely need.
3. **Define DTOs.** Request DTOs with `class-validator`; response DTOs or serializers.
4. **Implement the service.** Encapsulate business logic; depend on injected providers/repositories; throw typed exceptions.
5. **Wire the controller.** Bind HTTP method, path, status codes, validation, Swagger decorators, and guards. Keep it thin.
6. **Wire DI.** Add providers and exports; pick the right scope; avoid `forwardRef` unless modules truly cannot be split.
7. **Cover cross-cutting concerns.** Add or rely on existing guards, interceptors, pipes, and exception filters.
8. **Write tests.** Unit tests for services with mocked dependencies; integration/e2e for the controller path.
9. **Validate.** Run typecheck, lint, unit tests, then e2e if relevant. Resolve issues at the lowest layer that exposes them.
10. **Document.** Add Swagger annotations and brief module/endpoint docs if the project expects them.

## Common Patterns

### Feature module skeleton

```typescript
@Module({
  imports: [TypeOrmModule.forFeature([User])],
  controllers: [UsersController],
  providers: [UsersService, UsersRepository],
  exports: [UsersService],
})
export class UsersModule {}
```

### Thin controller with validation and OpenAPI

```typescript
@ApiTags('users')
@Controller('users')
export class UsersController {
  constructor(private readonly usersService: UsersService) {}

  @Post()
  @HttpCode(HttpStatus.CREATED)
  @ApiOperation({ summary: 'Create a new user' })
  @ApiResponse({ status: HttpStatus.CREATED, type: UserResponseDto })
  create(@Body() dto: CreateUserDto): Promise<UserResponseDto> {
    return this.usersService.create(dto);
  }

  @Get(':id')
  findOne(@Param('id', ParseUUIDPipe) id: string): Promise<UserResponseDto> {
    return this.usersService.findOne(id);
  }
}
```

### Service with typed errors

```typescript
@Injectable()
export class UsersService {
  constructor(private readonly users: UsersRepository) {}

  async create(dto: CreateUserDto): Promise<UserResponseDto> {
    if (await this.users.findByEmail(dto.email)) {
      throw new ConflictException('Email already registered');
    }
    const user = await this.users.create(dto);
    return UserResponseDto.from(user);
  }

  async findOne(id: string): Promise<UserResponseDto> {
    const user = await this.users.findById(id);
    if (!user) throw new NotFoundException(`User ${id} not found`);
    return UserResponseDto.from(user);
  }
}
```

### Custom decorator that composes guards and metadata

```typescript
export const Auth = (...roles: Role[]) =>
  applyDecorators(UseGuards(JwtAuthGuard, RolesGuard), Roles(...roles));
```

### Global pipes, filters, and interceptors at bootstrap

```typescript
async function bootstrap() {
  const app = await NestFactory.create(AppModule, { bufferLogs: true });

  app.useGlobalPipes(
    new ValidationPipe({
      whitelist: true,
      forbidNonWhitelisted: true,
      transform: true,
      transformOptions: { enableImplicitConversion: true },
    }),
  );
  app.useGlobalInterceptors(new ClassSerializerInterceptor(app.get(Reflector)));
  app.useGlobalFilters(new HttpExceptionFilter());

  await app.listen(process.env.PORT ?? 3000);
}
bootstrap();
```

### Config with schema validation

```typescript
ConfigModule.forRoot({
  isGlobal: true,
  load: [configuration],
  validate: validateEnv,
});
```

### Unit test for a service

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

  it('throws ConflictException when email exists', async () => {
    users.findByEmail.mockResolvedValue({ id: '1' });
    await expect(service.create({ email: 'a@b.c', password: 'x' })).rejects.toThrow(ConflictException);
  });
});
```

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

## Output Format

When proposing or generating an implementation, return in this order:

1. **Intent and scope:** one or two sentences.
2. **Module layout:** files to add or modify, with paths.
3. **Code:** module, controller, service, DTOs, and tests in that order; keep code idiomatic and minimal.
4. **DI and bootstrap notes:** any global pipe/filter/interceptor, config, or env additions.
5. **Tests:** unit tests for service logic; integration/e2e for the controller path.
6. **Validation steps:** typecheck, lint, unit tests, e2e (in this order).
7. **Risks and follow-ups:** anything intentionally deferred, with a short rationale.

## Definition of Done

A NestJS change is not ready until:

- Intent and scope are explicit.
- The module is feature-scoped with clear `imports`, `controllers`, `providers`, and `exports`.
- Inputs are validated through DTOs with `class-validator` and a global `ValidationPipe`.
- Services throw typed exceptions; controllers do not own business logic.
- Guards and decorators (not inline checks) enforce authentication and authorization.
- Configuration and secrets come from `ConfigModule` with validation.
- Unit tests cover service logic; integration/e2e tests cover the controller path where it matters.
- Typecheck, lint, and tests pass before the change is offered for review.
