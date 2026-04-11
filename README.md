# 🎮 DOTA 2 ANALYTICS PIPELINE v2.0
## 📌 ПОЧНИ ЗВІДСИ

**Ти отримав 4 документи. Це гайд як їх використовувати.**

---

# 📚 ЧТО ТИ ОТРИМАВ

```
📄 SUMMARY.md                      ← ТИ ТЕПЕР ЧИТАЄШ (цей файл)
📄 DOTA2_ANALYTICS_v2_TZ.md        ← Повне технічне завдання (архітектура)
📄 SKILL_BUILDING_GUIDELINE.md     ← Як учитися під час розробки
📄 QUALITY_ASSESSMENT_SERVICE.md   ← Новий сервіс (Phase 2)
```

---

# 🚀 ПЛАН (Що робити по порядку)

## ✅ ШАГ 1: ЧИТАННЯ (1-2 години)

Прочитай у цьому порядку:

### 1.1 Цей файл повністю (5 хв)
Ти вже читаєш його 😊

### 1.2 SUMMARY.md (10 хв)
- Короткий огляд всього
- 7 мікросервісів
- 3 фази розробки
- Важні посилання

### 1.3 DOTA2_ANALYTICS_v2_TZ.md (30-45 хв)
**Повне технічне завдання**

Розділи:
- Огляд продукту (vision)
- Архітектура (діаграми)
- Мікросервіси (責務, endpoints, API)
- БД схеми
- API контракти
- MVP scope (epics + tasks)

**Як читати:**
- Спочатку прочитай "Архітектура" + діаграму
- Потім 1-2 мікросервіси (не все)
- Дивись на примери endpoints
- Потім MVP scope

### 1.4 SKILL_BUILDING_GUIDELINE.md (20 хв)
**Як учитися під час кодування**

Розділи:
- SOLID принципи (з посиланнями)
- Документація для кожного Epica
- Завдання для кожного сервісу
- Чеклист перед кожною task
- Як питати мене

**Як користувати:**
- Читай перед Epic 1
- Зберегти собі для справки
- Коли пишеш код → див гайд для цієї task

### 1.5 QUALITY_ASSESSMENT_SERVICE.md (15 хв, опціонально)
**ФАЗА 2 (не для MVP)**

Для розуміння:
- Як виявляти inting, smurfs, unconventional builds
- Алгоритми для якості гри
- Це додаємо на тижні 5

---

## ✅ ШАГ 2: ПІДГОТОВКА (1 день)

### 2.1 Створи GitHub repository

```bash
git init dota2-analytics-v2
cd dota2-analytics-v2

# Структура
mkdir -p services/{ingestion,reference_data,analytics,ml,admin,quality_assessment}
mkdir -p frontend
mkdir -p docs
mkdir -p docker

# Скопіюй документи
cp DOTA2_ANALYTICS_v2_TZ.md docs/
cp SKILL_BUILDING_GUIDELINE.md docs/
cp QUALITY_ASSESSMENT_SERVICE.md docs/
```

### 2.2 Налаштуй .gitignore

```
__pycache__/
*.pyc
.env
.env.local
node_modules/
dist/
build/
.venv/
*.egg-info/
.pytest_cache/
.coverage
.mypy_cache/
```

### 2.3 Налаштуй базові конфіги

```
docker/
  ├── Dockerfile.backend
  ├── Dockerfile.frontend
  └── docker-compose.yml (skeleton)

.env.example
poetry.lock (буде згенерований)
```

---

## ✅ ШАГ 3: EPIC 1 BOOTSTRAP (Тиждень 1)

### 3.1 Перш за все
1. Прочитай **SKILL_BUILDING_GUIDELINE.md** section "Epic 1"
2. Прочитай посилання з гайду:
   - [FastAPI Dependency Injection](https://fastapi.tiangolo.com/tutorial/dependencies/)
   - [pydantic-settings](https://docs.pydantic.dev/latest/concepts/pydantic_settings/)
   - [Structured Logging](https://www.kartar.net/2015/12/structured-logging/)

### 3.2 Завдання

```
Task 1.1: Project bootstrap
  - Python 3.11+ структура
  - poetry для пакетів
  - базовий main.py (FastAPI)

Task 1.2: Config management
  - pydantic-settings
  - .env файл
  - environment variables

Task 1.3: Docker setup
  - Dockerfile для backend
  - docker-compose.yml (pg, mongo, redis)

Task 1.4: Logging
  - structlog config
  - JSON output

... і далі до 1.8
```

### 3.3 Як писати код

Для кожної task:

```
1. Прочитай гайд для цієї task (посилання в SKILL_BUILDING_GUIDELINE.md)
2. Напиши ТЕС (test-first)
3. Напиши КОД щоб тест пройшов
4. Push в git
5. CodeRabbit review
6. Merge
```

### 3.4 Питання мені

Коли застряєш:

❌ "Як написати HTTP client?"  
✅ "Я хочу fetch матчі з OpenDota з retry/backoff. 
   Яку архітектуру вибрати? 
   Окремий клас? Service layer? 
   Яки SOLID принципи мені розглянути?"

---

## ✅ ШАГ 4: DATA INGESTION & ANALYTICS (Тиждні 2-3)

### 4.1 Epic 2: Data Ingestion Service
- OpenDota HTTP client
- Match parser (Pydantic)
- MongoDB writer
- Deduplication

### 4.2 Epic 3: Reference Data Service
- Hero sync
- Item sync
- Redis caching
- GET /heroes endpoints

### 4.3 Epic 4: Basic Analytics
- rebuild_hero_stats batch job
- rebuild_matchups batch job
- rebuild_synergies batch job
- GET /meta/heroes endpoint

---

## ✅ ШАГ 5: DRAFT ADVISOR + FRONTEND (Тиждень 4)

### 5.1 Epic 5: Draft Advisor (Rule-based)
- Synergy scorer
- Counter scorer
- Meta weight scorer
- GET /draft/recommend endpoint

### 5.2 Epic 6: Frontend MVP
- React + Vite + TypeScript
- Hero stats table
- Draft advisor UI
- Responsive design

---

## ✅ РЕЗУЛЬТАТ (Кінець тижня 4)

```
✅ 500+ матчів ingested з OpenDota
✅ PostgreSQL + MongoDB + Redis working
✅ 6 API endpoints working
✅ Draft recommendations generating
✅ React frontend (hero stats + draft advisor)
✅ All tests passing
✅ Docker compose working
```

---

# 📖 КАК КОРИСТУВАТИ ДОКУМЕНТАМИ

## Когда питаєш АРХІТЕКТУРУ

```
→ Дивись DOTA2_ANALYTICS_v2_TZ.md
  - Architecture section
  - Microservices section
  - Diagram
```

## Коли питаєш КОД / DESIGN

```
→ Дивись SKILL_BUILDING_GUIDELINE.md
  - SOLID section
  - Design Patterns
  - Epic-specific links
```

## Коли питаєш API CONTRACT

```
→ Дивись DOTA2_ANALYTICS_v2_TZ.md
  - API контракти section
  - Endpoints по сервісам
```

## Коли питаєш DATABASE SCHEMA

```
→ Дивись DOTA2_ANALYTICS_v2_TZ.md
  - Схеми БД section
  - PostgreSQL schema
  - MongoDB collections
```

## Коли питаєш НА ЯКІСТЬ ИГРЫ

```
→ Дивись QUALITY_ASSESSMENT_SERVICE.md
  (це Phase 2, не для MVP)
```

---

# 🎯 ОСНОВНІ РІШЕННЯ (Які вже прийняті)

## Архітектура: Мікросервісна

**Чому:**
- Кожний сервіс робить одне добре (SOLID)
- Легко масштабувати
- Легко тестувати
- Легко розумівати код

## БД: PostgreSQL + MongoDB + Redis

**Чому:**
- PostgreSQL: реляційні дані (heroes, items, stats)
- MongoDB: flexible match JSON
- Redis: L1 cache для швидких read-only queries

## API: REST v1.0

**Чому:**
- Простої + стандартні
- Легко версіонувати
- Легко документувати (OpenAPI)

## Draft Scoring: Rule-based спочатку, потім ML

**Чому:**
- Rule-based швидко реалізувати (MVP)
- ML додамо на Phase 2 (коли є дані)

---

# ❓ ЧЕСТО ЗАДАВАНІ ПИТАННЯ

## Q: Я не розумію arquitecture. З чого почати?

A: Прочитай DOTA2_ANALYTICS_v2_TZ.md section "Архітектура". Там діаграма. Потім нарисуй її сам на папері.

## Q: Я не знаю як написати HTTP client. Що робити?

A: 
1. Прочитай SKILL_BUILDING_GUIDELINE.md section "Epic 2"
2. Читай посилання які там
3. Напиши test спочатку
4. Потім код
5. Питай мене якщо заскочив

## Q: Чому 3 БД? Не можна на одній?

A: Прочитай DOTA2_ANALYTICS_v2_TZ.md section "БД Стратегія". Там пояснення.

## Q: Сміртельно пропустити что-то?

A: Ні. Просто читай + пиши код + питай. Пропусків не буває 😊

## Q: Коли я готовий до Phase 2?

A: Коли Phase 1 (6 epics) закінчиться. Це ~ тиждень 4.

---

# 📋 ЧЕКЛИСТ ПЕРЕД СТАРТОМ

```
[ ] Ти прочитав SUMMARY.md
[ ] Ти прочитав DOTA2_ANALYTICS_v2_TZ.md
[ ] Ти прочитав SKILL_BUILDING_GUIDELINE.md
[ ] Ти розумієш архітектуру (7 мікросервісів)
[ ] Ти розумієш MVP scope (6 epics)
[ ] Ти готовий писати код (не копіювати)
[ ] Ти готовий питати (не просити готові розв'язки)
[ ] Ти готовий учитися (SOLID, REST, patterns)
```

Якщо всі ✅ — тоді ти готовий!

---

# 🚀 ПОЧАТОК

## Прямо тепер (5 хв)

```bash
cd dota2-analytics-v2
git status
git add .
git commit -m "initial: project setup + documentation"
```

## Завтра (напев)

```
1. Прочитай SKILL_BUILDING_GUIDELINE.md
2. Обери Epic 1, Task 1.1
3. Напиши перший тест
4. Питай мене якщо потрібна помічь
```

---

# 💬 КОНТАКТ

Коли у тебе питання:

1. Спочатку дивись **яку документацію** может допомогти
2. Прочитай посилання з гайду
3. Потім питай **мене** з **хорошим контекстом**

**Я готовий!** 💪

---

**Версія:** 1.0  
**Статус:** 🟢 Ready to Code  
**Автор:** recombinationBTRDRS + AI Assistant

**Давай кодити!** 🚀
