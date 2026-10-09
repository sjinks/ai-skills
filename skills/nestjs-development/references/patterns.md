When to read: when a touched NestJS surface needs an implementation or testing example. These are partial illustrations; adapt them to the project and do not add components solely to match an example.

## Common Patterns

### Feature module skeleton

The example below leaves the `imports` array empty and uses an inline
comment as a placeholder to stay ORM-agnostic. In a real project,
replace the comment with whatever the project already uses (for
example `TypeOrmModule.forFeature([User])`,
`MongooseModule.forFeature([{ name: User.name, schema: UserSchema }])`,
`PrismaModule`, or no ORM import at all if the repository is a
hand-rolled provider).

```typescript
@Module({
  imports: [
    // Project-specific ORM/feature wiring goes here. Examples:
    //   TypeOrmModule.forFeature([User])
    //   MongooseModule.forFeature([{ name: User.name, schema: UserSchema }])
    //   PrismaModule
    //   (omit entirely for a hand-rolled UsersRepository provider)
  ],
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
