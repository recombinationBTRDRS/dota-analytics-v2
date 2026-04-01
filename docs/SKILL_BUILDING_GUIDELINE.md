# 🎓 SKILL-BUILDING GUIDELINE
## Як розвиватися під час розробки Dota 2 Analytics v2.0

**Мета:** Ти пишеш код самостійно, я + CodeRabbit подаємо підказки, посилання на принципи і best practices.

**Результат:** На кінці проекту ти розумієш OOP, SOLID, REST API і можеш писати production-ready код.

---

# 📚 ПРАВИЛА ГРИ

## Для тебе (Developer)

```
1. Пиши КОД самостійно
2. Коли застряєш → питай MNE (меня)
3. Коли сумніваєшся в design → питай ДО того як писати
4. Читай посилання які дам
5. Запитуй пояснення ПРИНЦИПІВ, не готових розв'язків
```

## Для мене (AI Mentor)

```
1. Не писати готовий код (окрім прикладів)
2. Вказувати на ПРИНЦИПИ (SOLID, DRY, etc.)
3. Давати посилання на docs/articles
4. Питати "чому ти думаєш що це ОК?"
5. Пояснювати через прикладинки
```

## Для CodeRabbit (Code Review)

```
1. Перевіряти на SOLID violations
2. Пропонувати рефакторинг (не писати)
3. Вказувати на code smells
4. Посилатися на best practices
5. Бути constructive, не критичним
```

---

# 🏛️ ОСНОВНІ ПРИНЦИПИ (Які мають бути завжди на радарі)

## SOLID

| Принцип | Абревіатура | Коротке визначення | Де читати |
|---------|------------|-------------------|-----------|
| Single Responsibility | **S** | Клас робить ОДНЕ добре | [SRP Explanation](https://en.wikipedia.org/wiki/Single-responsibility_principle) |
| Open/Closed | **O** | Відкрито для розширення, закрито для змін | [OCP Article](https://stackify.com/solid-design-open-closed-principle/) |
| Liskov Substitution | **L** | Підклас = коректна заміна батька | [LSP Guide](https://en.wikipedia.org/wiki/Liskov_substitution_principle) |
| Interface Segregation | **I** | Багато малих interfaces краще, ніж один великий | [ISP Best Practice](https://www.geeksforgeeks.org/interface-segregation-principle/) |
| Dependency Inversion | **D** | Залежи від abstraction, не implementation | [DIP Pattern](https://refactoring.guru/design-patterns/dependency-injection) |

## REST API Принципи

| Принцип | Опис | Приклад |
|---------|------|---------|
| **Resources** | Сутності (nouns), не операції (verbs) | `GET /heroes` ✅ / `GET /get-heroes` ❌ |
| **HTTP Methods** | GET (read), POST (create), PUT/PATCH (update), DELETE | `POST /matches` ✅ / `GET /create-match` ❌ |
| **Status Codes** | 200 (OK), 201 (Created), 400 (Bad Request), 404 (Not Found), 500 (Server Error) | [HTTP Status Codes](https://httpwg.org/specs/rfc7231.html#status.codes) |
| **Versioning** | API версії в URL: `/api/v1/`, `/api/v2/` | `GET /api/v1/heroes` |
| **Idempotency** | GET, PUT, DELETE мають бути idempotent | [Idempotency Explanation](https://restfulapi.net/idempotent-rest-apis/) |

## Design Patterns (для цього проекту)

| Паттерн | Де використовується | Посилання |
|---------|-------------------|-----------|
| **Repository** | DB access layer | [Repository Pattern](https://martinfowler.com/eaaCatalog/repository.html) |
| **Service** | Business logic layer | [Service Layer Pattern](https://martinfowler.com/eaaCatalog/serviceLayer.html) |
| **DTO (Data Transfer Object)** | API communication | [DTO Pattern](https://en.wikipedia.org/wiki/Data_transfer_object) |
| **Factory** | Object creation | [Factory Pattern](https://refactoring.guru/design-patterns/factory-method) |
| **Dependency Injection** | Loose coupling | [DI Pattern](https://en.wikipedia.org/wiki/Dependency_injection) |
| **Event-Driven** | Service communication | [Event-Driven Architecture](https://www.confluent.io/blog/event-driven-architecture/) |

---

# 📖 ДОКУМЕНТАЦІЯ ЯКА ТРЕБА МАТИ ЗАВЖДИ ПІД РУКОЮ

## Python & FastAPI

| Ресурс | Що там | Посилання |
|--------|--------|-----------|
| FastAPI Official Docs | Все про FastAPI | [fastapi.tiangolo.com](https://fastapi.tiangolo.com/) |
| Pydantic Validation | DTO + validation | [docs.pydantic.dev](https://docs.pydantic.dev/) |
| SQLAlchemy ORM | Database queries | [sqlalchemy.org](https://docs.sqlalchemy.org/) |
| PyMongo Guide | MongoDB operations | [pymongo.readthedocs.io](https://pymongo.readthedocs.io/) |
| aioredis Async Redis | Redis operations | [aioredis.readthedocs.io](https://aioredis.readthedocs.io/) |
| Python Async/Await | async patterns | [docs.python.org/3/library/asyncio](https://docs.python.org/3/library/asyncio.html) |

## Testing

| Ресурс | Що там | Посилання |
|--------|--------|-----------|
| pytest Official | Unit testing | [pytest.org](https://pytest.org/) |
| pytest-asyncio | Async test support | [pytest-asyncio docs](https://pytest-asyncio.readthedocs.io/) |
| unittest.mock | Mocking | [docs.python.org/unittest.mock](https://docs.python.org/3/library/unittest.mock.html) |

## Architecture & Best Practices

| Ресурс | Що там | Посилання |
|--------|--------|-----------|
| Refactoring.Guru | Design patterns explained | [refactoring.guru](https://refactoring.guru/) |
| Clean Code (Martin) | Code quality principles | [Clean Code Book](https://www.amazon.com/Clean-Code-Handbook-Software-Craftsmanship/dp/0132350882) |
| REST API Best Practices | API design | [restfulapi.net](https://restfulapi.net/) |
| Microservices Patterns | Service architecture | [microservices.io](https://microservices.io/) |

---

# 🎯 ПО ЕПІКАХ: ЧТО ВЧИТИ ПЕРЕД КОЖНОЮ

## Epic 1: Foundation & Infrastructure

### Основні концепції
- **Dependency Injection** (як Spring, FastAPI's `Depends()`)
- **Configuration Management** (pydantic-settings, 12-factor app)
- **Logging** (structured logs, log levels)
- **Health checks** (readiness, liveness probes)

### Документація
1. [FastAPI Dependency Injection](https://fastapi.tiangolo.com/tutorial/dependencies/)
2. [12 Factor App - Config](https://12factor.net/config)
3. [Structured Logging Best Practice](https://www.kartar.net/2015/12/structured-logging/)
4. [Health Check Patterns](https://www.usenix.org/sites/default/files/login/articles/10_020-021_final.pdf)

### Завдання для тебе
- **1.1:** Create `main.py` (FastAPI app, lifespan)
  - Питай: "Як структурувати routes?"
  - Читай: [FastAPI Project Structure](https://fastapi.tiangolo.com/project-structure/)
  
- **1.5:** Create `config.py` (pydantic-settings)
  - Питай: "Де розташовувати .env?"
  - Читай: [pydantic-settings docs](https://docs.pydantic.dev/latest/concepts/pydantic_settings/)

---

## Epic 2: Data Ingestion Service

### Основні концепції
- **Repository Pattern** (abstraction for data access)
- **DTOs** (API contracts with Pydantic)
- **Error Handling** (custom exceptions, retry logic)
- **HTTP Client** (httpx, exponential backoff)

### Документація
1. [Repository Pattern Explained](https://martinfowler.com/eaaCatalog/repository.html)
2. [Pydantic DTO Validation](https://docs.pydantic.dev/latest/usage/models/)
3. [Exponential Backoff](https://aws.amazon.com/blogs/architecture/exponential-backoff-and-jitter/)
4. [httpx Advanced Usage](https://www.python-httpx.org/)

### Завдання для тебе
- **2.1:** OpenDota HTTP client
  - Питай: "Як правильно дизайнити HTTP client клас?"
  - Читай: [HTTP Client Design Patterns](https://www.youtube.com/watch?v=RSQvhrvxkZQ)
  - **Очікуючи результат:** клас з методами `fetch_match()`, retry/backoff вбудований
  
- **2.2:** Match Parser (Pydantic schema)
  - Питай: "Як валідувати складні nested objects?"
  - Читай: [Pydantic Validators](https://docs.pydantic.dev/latest/concepts/validators/)
  - **Очікуючи результат:** `MatchSchema` з custom validators
  
- **2.3:** Normalizer
  - Питай: "Де краще розташувати normalization logic?"
  - Читай: [Data Transformation Patterns](https://refactoring.guru/design-patterns/abstract-factory)
  - **Очікуючи результат:** utility функції або окремий клас?

- **2.4:** MongoDB Writer (Repository pattern)
  - Питай: "Як абстрагувати DB access?"
  - Читай: [Repository Pattern with MongoDB](https://github.com/mongodb-developer/python-quickstart)
  - **Очікуючи результат:** `MatchRepository` клас з `.insert()`, `.find()` методами

---

## Epic 3: Reference Data Service

### Основні концепції
- **Dependency Injection Container** (FastAPI's dependency system)
- **Service Layer** (business logic separation)
- **Caching Strategy** (Redis integration)
- **API Versioning** (URL prefixes)

### Документація
1. [Service Layer Pattern](https://martinfowler.com/eaaCatalog/serviceLayer.html)
2. [FastAPI with Redis](https://fastapi.tiangolo.com/advanced/background-tasks/)
3. [Cache Invalidation Strategies](https://www.danielrickli.com/posts/2023-04-16-cache-invalidation/)
4. [API Versioning Best Practices](https://restfulapi.net/versioning/)

### Завдання для тебе
- **3.1-3.2:** Hero/Item sync
  - Питай: "Як структурувати sync logic?"
  - Читай: [ETL Patterns](https://en.wikipedia.org/wiki/Extract,_transform,_load)
  - **Очікуючи:** `HeroService.sync_from_opendota()` метод
  
- **3.4:** Redis cache seeding
  - Питай: "Як правильно кешувати дані?"
  - Читай: [Redis Caching Patterns](https://redis.io/docs/latest/develop/use/patterns/cache/)
  - **Очікуючи:** `CacheWarmer` клас або service

- **3.6:** GET endpoints
  - Питай: "Як структурувати endpoint routes?"
  - Читай: [FastAPI Routers](https://fastapi.tiangolo.com/tutorial/bigger-applications/)
  - **Очікуючи:** `/api/v1/heroes/` з proper error handling

---

## Epic 4: Basic Analytics

### Основні концепції
- **Batch Processing** (aggregate, compute)
- **Data Aggregation** (MongoDB aggregation pipeline)
- **Event-Driven Architecture** (publish/subscribe)
- **Job Scheduling** (APScheduler)

### Документація
1. [MongoDB Aggregation Pipeline](https://docs.mongodb.com/manual/reference/operator/aggregation/)
2. [Event-Driven Architecture](https://www.rabbitmq.com/tutorials/amqp-concepts.html)
3. [APScheduler Documentation](https://apscheduler.readthedocs.io/)
4. [Batch Processing Best Practices](https://en.wikipedia.org/wiki/Batch_processing)

### Завдання для тебе
- **4.1:** rebuild_hero_stats batch job
  - Питай: "Як групувати та агрегувати MongoDB документи?"
  - Читай: [MongoDB Aggregation Stages](https://docs.mongodb.com/manual/reference/operator/aggregation-pipeline/)
  - **Очікуючи:** функція яка читає матчі → обраховує stats → пише у PostgreSQL
  
- **4.6:** Event handler (match.ingested → rebuild trigger)
  - Питай: "Як правильно дизайнити event-driven систему?"
  - Читай: [Pub/Sub Patterns](https://redis.io/docs/latest/develop/use/patterns/pub-sub/)
  - **Очікуючи:** Redis pub/sub consumer який слухає на events

---

## Epic 5: Draft Advisor

### Основні концепції
- **Business Logic Separation** (scorer classes)
- **Interface Segregation** (SOLID)
- **Composition over Inheritance**
- **Testability** (unit tests for scorers)

### Документація
1. [SOLID Design Principles](https://en.wikipedia.org/wiki/SOLID)
2. [Composition vs Inheritance](https://www.youtube.com/watch?v=wfMtDGfHsPE)
3. [Unit Testing Best Practices](https://docs.pytest.org/en/stable/goodpractices.html)

### Завдання для тебе
- **5.1-5.4:** Scorers (synergy, counter, meta weight)
  - Питай: "Як дизайнити scorer классы щоб вони були тестовані та reusable?"
  - Читай: [Strategy Pattern](https://refactoring.guru/design-patterns/strategy)
  - **Очікуючи:** Три окремих класи: `SynergyScorer`, `CounterScorer`, `MetaWeightScorer` (кожен робить одне)
  
- **5.5:** GET /draft/recommend endpoint
  - Питай: "Як структурувати endpoint який комбінує результати різних scorers?"
  - Читай: [Facade Pattern](https://refactoring.guru/design-patterns/facade)
  - **Очікуючи:** endpoint який інтегрує всі scorers та повертає рейтинговий список

---

## Epic 6: Frontend MVP

### Основні концепції
- **Component-based Architecture** (React)
- **State Management** (React hooks, TanStack Query)
- **API Client Layer** (abstraction for HTTP calls)
- **Error Handling** (UI feedback)

### Документація
1. [React Official Tutorial](https://react.dev/learn)
2. [TanStack Query Documentation](https://tanstack.com/query/latest)
3. [REST API Client Best Practices](https://www.builder.io/blog/api-patterns-in-frontend)

### Завдання для тебе
- **6.2:** API client layer
  - Питай: "Як абстрагувати HTTP calls від UI компонентів?"
  - Читай: [Separation of Concerns](https://en.wikipedia.org/wiki/Separation_of_concerns)
  - **Очікуючи:** `apiClient.ts` з методами `getHeroes()`, `getDraftRecommend()`, etc.

---

# 🔍 КОЛИ СУМНІВАЄШСЯ: ЧО ПИТАТИ

## Питання для мене

```
❌ ПОГАНО:
"Як написати это?"
"Который паттерн мне нужен?"

✅ ДОБРЕ:
"Я хочу щоб цей код робив X, Y, Z.
 Яки ПРИНЦИПИ мені слід розглянути?"

"Я бачу дублювання в коді [ссилка].
 Який паттерн мені може допомогти?"

"Я думаю використати [паттерн].
 Це SOLID-compliant? Чому/чому ні?"
```

## Питання для CodeRabbit

```
❌ ПОГАНО:
"Це погано?"
"Переписи це за мною"

✅ ДОБРЕ:
"Це порушує який SOLID принцип?"
"Як я можу рефакторити це без переписування всього?"
"На яку документацію я мав би розглянути?"
```

---

# 💡 ПРИМЕРЫ ПРАВИЛЬНОГО ЗАПИТУ

## Приклад 1: HTTP Client Design

```
ТИ: "Я хочу напісати OpenDota HTTP client.
     Яка архітектура буде найкраще? 
     Окремий клас? Utility функції? 
     А як мені обробляти retry/backoff?"

MNE: "Good question! Это кажется как необходимость для:
     1. Single Responsibility (клас тільки для HTTP)
     2. Dependency Injection (легко мокувати в тестах)
     3. Reusability (інші сервіси можуть його використовувати)
     
     Читай:
     - https://refactoring.guru/design-patterns/strategy
     - https://www.python-httpx.org/ (advanced usage)
     
     Погляди як інші проекти це роблять:
     - FastAPI HTTPClient example
     - aiohttp tutorial
     
     Потім напиши skeletон (0 логіки) і давай мені ревю"

TY: [пишу клас]

CODERABBIT: "Good! Но у мене є поради:
     1. Retry logic - це можна винести в окремий middleware
     2. Хардкодований timeout - краще в config
     3. Eksception handling - які исключения ви хочите ловити?
     
     Смотри https://aws.amazon.com/blogs/architecture/exponential-backoff-and-jitter/
     Потім давай оновлену версию"
```

---

# 📋 ЧЕКЛИСТ ПЕРЕД КОЖНОЮ TASK

Перед тим як писати код, переконайся:

```
[ ] Я прочитав документацію (посилання вище)
[ ] Я розумію ЯКИЙ ПРИНЦИП це стосується (SOLID, REST, etc.)
[ ] Я написав unit тест ПЕРШ ніж писати код (TDD)
[ ] Я питав "а чому це ОК дизайн?" перед тим
[ ] Я готовий до code review
[ ] Я додав comments для складних частин
[ ] Я перевірив error handling
[ ] Я не скопіював-вставив готовий код (написав свій)
```

---

# 🎓 ОЧІКУВАНІ НАВИЧКИ НА КІНЕЦЬ ПРОЕКТУ

## Python + FastAPI
- ✅ Async/await patterns
- ✅ Dependency Injection
- ✅ Error handling best practices
- ✅ Testing (unit, integration)
- ✅ Database operations (SQL + NoSQL)

## Architecture
- ✅ Repository Pattern
- ✅ Service Layer Pattern
- ✅ DTO/Validation patterns
- ✅ Event-driven design
- ✅ Microservices principles

## REST API
- ✅ Resource-oriented design
- ✅ HTTP methods + status codes
- ✅ API versioning
- ✅ Error responses
- ✅ Pagination + filtering

## SOLID Principles
- ✅ Single Responsibility
- ✅ Open/Closed
- ✅ Liskov Substitution
- ✅ Interface Segregation
- ✅ Dependency Inversion

## Testing
- ✅ Unit tests (pytest)
- ✅ Mocking
- ✅ Test coverage
- ✅ Integration tests

## React + Frontend
- ✅ Component composition
- ✅ State management
- ✅ API client layer
- ✅ Error handling
- ✅ Testing components

---

# 🚀 ПОЧНИ ЗВІДСИ

1. **Прочитай цей гайд повністю**
2. **Обери Epic 1** (Foundation)
3. **Для кожної task:**
   - Прочитай відповідні посилання
   - Напиши тест спочатку
   - Напиши код
   - Питай мене якщо заскочив
   - Чекай code review від CodeRabbit
4. **Коли finish → обираєш Epic 2** (Data Ingestion)
5. **Повторюєш**

---

**Ти готовий? Почнемо з Epic 1.1? 🚀**

Питай мене будь-коли, я тут щоб допомагати (не писати код за тебе).
