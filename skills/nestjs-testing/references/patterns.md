When to read: when a touched NestJS surface needs an implementation or testing example. These are partial illustrations; adapt them to the project and do not add components solely to match an example.

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
