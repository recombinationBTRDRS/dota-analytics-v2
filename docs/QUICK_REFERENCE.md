# ⚡ QUICK REFERENCE (Шпаргалка)

**Користуй цей файл коли потрібна інформація швидко!**

---

# 📁 ФАЙЛИ ДОКУМЕНТАЦІЇ

| Файл | Для чого | Коли читати |
|------|----------|-----------|
| **README.md** | Початок роботи | День 1 (5 хв) |
| **SUMMARY.md** | Огляд документів | День 1 (10 хв) |
| **DOTA2_ANALYTICS_v2_TZ.md** | Повне ТЗ | День 1 (1 година) |
| **SKILL_BUILDING_GUIDELINE.md** | Як учитися | Перед кожною task |
| **ARCHITECTURE_DIAGRAMS.md** | Діаграми | Коли питаєш архітектуру |
| **QUALITY_ASSESSMENT_SERVICE.md** | Якість гри | Тиждень 5 (Phase 2) |

---

# 🏛️ 7 МІКРОСЕРВІСІВ (QUICK)

| :Port | Сервіс | Що робить | Endpoints |
|-------|--------|-----------|-----------|
| :8001 | **Data Ingestion** | Fetch → Parse → Validate → Store | POST /ingest/opendota |
| :8002 | **Reference Data** | Heroes, items, skills | GET /heroes, GET /items |
| :8003 | **Analytics** | Pre-computed stats + draft advisor | GET /meta/heroes, GET /draft/recommend |
| :8004 | **ML** (Phase 2) | Models + predictions | POST /ml/predict/* |
| :8005 | **Admin** | Overrides, logs, health | POST /admin/override* |
| :8006 | **Quality** (Phase 2) | Game quality scoring | POST /assess/* |
| :9000 | **WebSocket** | Live draft updates | ws://domain/ws/* |

---

# 🗄️ БД (QUICK)

| БД | Для чого | Таблиці / Collections |
|----|-----------|-----------------------|
| **PostgreSQL** | Relations + pre-computed | heroes, items, hero_stats_computed, matchups, synergies |
| **MongoDB** | JSON matches + logs | matches, ingestion_log |
| **Redis** | L1 cache (fast reads) | hero:*, item:*, draft:reco:*, counter:*, synergy:* |

---

# 📊 6 EPICS (MVP - Тижні 1-4)

| Epic | Tasks | SP | Week |
|------|-------|----|----|
| 1: Foundation | 1.1-1.8 | 30 | 1 |
| 2: Data Ingestion | 2.1-2.8 | 35 | 1-2 |
| 3: Reference Data | 3.1-3.8 | 25 | 2 |
| 4: Analytics | 4.1-4.7 | 30 | 2-3 |
| 5: Draft Advisor | 5.1-5.7 | 20 | 3 |
| 6: Frontend | 6.1-6.8 | 25 | 3-4 |
| **TOTAL MVP** | **~50 tasks** | **~165 SP** | **4 weeks** |

---

# 🎯 DRAFT SCORING FORMULA

```
score = 0.35 * synergy + 0.35 * counter + 0.30 * meta_weight

Де:
• synergy = avg([synergy(hero, pick) for pick in our_picks])
• counter = avg([counter_score(hero, enemy) for enemy in enemies])
• meta_weight = pickrate × winrate normalized to 0-1
```

---

# 🔗 ДАНІ FLOWS (QUICK)

### Flow 1: New Match
```
POST /ingest → Fetch OpenDota → Parse → Validate → Store MongoDB
→ Event: "match.ingested" 
→ rebuild (if 10+ matches in 5min)
→ Store PostgreSQL pre-computed
→ Warm Redis cache
```

### Flow 2: Draft Recommendation
```
GET /draft/recommend?picks=...&bans=... 
→ Check Redis cache
→ Load from PostgreSQL (pre-computed)
→ Score each hero
→ Return top 10
```

### Flow 3: Meta Stats
```
GET /meta/heroes?role=1&days=30
→ Check Redis cache
→ Load from PostgreSQL
→ Apply overrides
→ Return
```

---

# 📡 API ENDPOINTS (MVP)

## Reference Data Service (:8002)
```
GET  /heroes                          → All heroes + stats
GET  /heroes/{id}                     → Hero detail
GET  /items                           → All items
GET  /skills/{hero_id}                → Hero skills
```

## Analytics Service (:8003)
```
GET  /meta/heroes?role={r}&days={d}  → Hero stats by role
GET  /draft/recommend?picks=...&bans=... → Draft recommendations
GET  /draft/counters/{hero_id}        → Counter matchups
GET  /draft/synergies/{hero_id}       → Ally synergies
```

## Data Ingestion Service (:8001)
```
POST /ingest/opendota?match_id={id}   → Ingest from OpenDota
GET  /ingest/status/{match_id}        → Check ingestion status
```

---

# ✅ ACCEPTANCE CRITERIA (MVP)

```
✅ 500+ matches ingested
✅ Hero stats accuracy: ± 2% vs OpenDota
✅ API response: < 200ms (cached)
✅ API uptime: 99.5%
✅ Draft recommendations: top 10 heroes
✅ Frontend responsive
✅ All tests passing
✅ Docker compose working
```

---

# 🔑 KEY TECHNOLOGIES

### Backend
```
Python 3.11+ | FastAPI 0.115 | Pydantic v2 | SQLAlchemy 2.0
PyMongo | aioredis | pytest | httpx
```

### Frontend
```
React 19 | Vite 7 | TypeScript 5 | TanStack Query | Tailwind CSS
```

### DevOps
```
Docker | docker-compose | GitHub Actions | PostgreSQL 15 | MongoDB 6 | Redis 7
```

---

# 🚨 COMMON PATTERNS

## Repository Pattern
```python
class HeroRepository:
    async def get_all() -> List[Hero]
    async def get_by_id(id: int) -> Hero
    async def save(hero: Hero) -> None
```

## Service Layer
```python
class HeroService:
    def __init__(self, repo: HeroRepository):
        self.repo = repo
    
    async def sync_from_opendota() -> None:
        # high-level logic
```

## DTO (Data Transfer Object)
```python
class HeroDTO(BaseModel):
    id: int
    name: str
    primary_attr: str
    # validation rules
```

## Dependency Injection (FastAPI)
```python
@app.get("/heroes")
async def get_heroes(repo: HeroRepository = Depends()):
    return await repo.get_all()
```

---

# ❓ QUICK ANSWERS

| Питання | Відповідь | Де читати |
|---------|-----------|----------|
| Як структурувати HTTP client? | Окремий клас з retry/backoff | SKILL_BUILDING_GUIDELINE Epic 2 |
| Де написати validation? | Pydantic schemas | DOTA2_ANALYTICS_v2_TZ (DTO section) |
| Як дизайнити endpoints? | Resource-oriented (/heroes, не /get-heroes) | SKILL_BUILDING_GUIDELINE REST API |
| Як тестувати? | Unit tests (pytest) + integration tests | SKILL_BUILDING_GUIDELINE Testing |
| Який паттерн для DB access? | Repository Pattern | SKILL_BUILDING_GUIDELINE Patterns |
| Як організувати папки? | services/module/app/routers, db, tests | README Step 2 |
| Когда писати ML? | Phase 2 (тиждень 5) | QUALITY_ASSESSMENT_SERVICE |
| Когда качество матча? | Phase 2 (Epic 8) | QUALITY_ASSESSMENT_SERVICE |

---

# 🎓 SOLID QUICK CHECK

Перед тим як коммітити код:

- [ ] **S**: Клас робить одну роль? (не 3+ відповідальностей)
- [ ] **O**: Легко додати новий функціонал без змін старого кода?
- [ ] **L**: Підклас = коректна заміна батька?
- [ ] **I**: Інтерфейсам не клієнтам запропоновуємо тільки потрібні методи?
- [ ] **D**: Залежимо від abstraction, не implementation?

Якщо ❌ на якомусь — питай мене!

---

# 📍 WHERE TO FIND THINGS

```
Питаєш про:                           Дивись:
────────────────────────────────────────────────────────
Архітектура                          ARCHITECTURE_DIAGRAMS.md
API контракти                        DOTA2_ANALYTICS_v2_TZ.md (API section)
БД схема                             DOTA2_ANALYTICS_v2_TZ.md (Schema section)
Як писати код                        SKILL_BUILDING_GUIDELINE.md
SOLID принципи                       SKILL_BUILDING_GUIDELINE.md (Principles)
Посилання на документацію            SKILL_BUILDING_GUIDELINE.md (Epic sections)
Якість гри / Inting detection        QUALITY_ASSESSMENT_SERVICE.md
Чеклист перед стартом                README.md (Step 2)
Як питати мене правильно             SKILL_BUILDING_GUIDELINE.md (FAQ)
```

---

# 🔥 HOT COMMANDS

```bash
# Start development
docker-compose up

# Run tests
pytest services/

# Run linter
ruff check .

# Type checking
mypy services/

# Format code
ruff format .

# Create migration (later)
alembic revision --autogenerate -m "message"
alembic upgrade head
```

---

# 📈 PROGRESS TRACKING

```
Week 1:  Epic 1 (Foundation) + Epic 2 (Ingestion)    ✅ 30 SP
Week 2:  Epic 2 (rest) + Epic 3 (Reference)         ✅ 25 SP
Week 3:  Epic 4 (Analytics) + Epic 5 (Advisor)      ✅ 50 SP
Week 4:  Epic 6 (Frontend MVP)                      ✅ 25 SP
────────────────────────────────────────────────────────
TOTAL:   ~130 SP (MVP Working) 🎉
```

---

# 🎯 DEFINITION OF DONE

Task вважається DONE коли:

```
✅ Code написаний
✅ Unit тести passing
✅ Integration тест (E2E) passing
✅ Code review passed (CodeRabbit + мене)
✅ Документація updated
✅ Не має console.log / TODO comments
✅ Error handling на місці
✅ Merged до main
```

---

# 🚀 QUICK START

```bash
# 1. Clone & setup
git clone dota2-analytics-v2
cd dota2-analytics-v2

# 2. Copy docs
cp ../SKILL_BUILDING_GUIDELINE.md ./docs/

# 3. Create virtual env
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate (Windows)

# 4. Install deps
pip install -r requirements.txt

# 5. Start Docker
docker-compose up

# 6. Run tests
pytest

# 7. Start dev server
cd services/ingestion
python -m uvicorn app.main:app --reload --port 8001
```

---

# 💬 HELP COMMANDS

Коли потрібна допомога:

```
Питання:  "Як написати HTTP client?"
Краще:    "Я хочу fetch матчі з OpenDota з retry/backoff.
           Окремий клас? Service layer? 
           Які SOLID принципи розглянути?
           На яку документацію дивитися?"

Питання:  "Це добре дизайнено?"
Краще:    "Чи цей код відповідає SOLID?
           Як рефакторити?"

Питання:  "Я заскочив"
Краще:    "Я писав [код], але отримав [error].
           Я спробував [что-то], не допомогло.
           На що дивитися далі?"
```

---

# 📞 CONTACT

**Потрібна допомога?**
1. Дивись цей Quick Reference
2. Читай відповідний документ (див таблиця "WHERE TO FIND")
3. Гугли (StackOverflow)
4. Питай мене з хорошим контекстом

**Готовий? Почни з README.md!** 🚀

---

**Версія:** 1.0  
**Статус:** 🟢 Quick Reference  
**Останнє оновлення:** 2025-03-24
