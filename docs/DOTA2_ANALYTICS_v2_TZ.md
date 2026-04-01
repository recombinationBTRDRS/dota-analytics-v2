# 🎮 DOTA 2 ANALYTICS PIPELINE v2.0
## Технічне завдання

**Версія:** 2.0.0  
**Дата:** 2025-03-24  
**Статус:** Draft → Готове до перегляду  
**Автор:** recombinationBTRDRS + AI Assistant

---

# 📋 ЗМІСТ

1. [Огляд продукту](#огляд-продукту)
2. [Архітектура](#архітектура)
3. [Мікросервіси](#мікросервіси)
4. [Схеми БД](#схеми-бд)
5. [API контракти](#api-контракти)
6. [Data flows](#data-flows)
7. [MVP scope](#mvp-scope)
8. [Epics & Tasks](#epics--tasks)
9. [Метрики успіху](#метрики-успіху)
10. [Технологічний стек](#технологічний-стек)

---

# 🎯 ОГЛЯД ПРОДУКТУ

## Vision (Бачення)

**Dota 2 Analytics Platform v2** — система для глибокого аналізу матчів, яка:
- Збирає матчі з OpenDota API + завантаження користувачами
- Будує власну базу знань (MongoDB)
- Генерує аналітику (pre-computed таблиці в PostgreSQL)
- Рекомендує найкращі тактики, героїв, предмети, поведінку
- Надає insights в реальному часі під час драфту

## Target Users (Цільові користувачі)

1. **Casual гравці** — виховання, покращення гейм-плану
2. **Pro гравці / Стрімери** — контент, глибокий аналіз
3. **Команди / Клуби** — скаутинг опонентів, підготовка стратегій
4. **Платформа** — подальша монетизація (платні підписки, реклама)

## Основні фічі (Phase 1)

| # | Фіча | Обсяг | Пріоритет |
|---|------|-------|-----------|
| 1 | **Meta Stats** | Winrate/pickrate/KDA per hero/role | 🔴 Critical |
| 2 | **Draft Advisor** | Counter picks + synergies | 🔴 Critical |
| 3 | **Item Builds** | Рекомендовані предмети per hero/role | 🔴 Critical |
| 4 | **Economy Forecast** | Прогноз GPM/net_worth по фазах гри | 🟠 High |
| 5 | **Lane Advantage** | Scoring лінійних парів (early game) | 🟠 High |
| 6 | **Match Storage** | Власна база даних (MongoDB) | 🔴 Critical |
| 7 | **Admin Panel** | Ручні корекції + управління даними | 🟡 Medium |

---

# 🏗️ АРХІТЕКТУРА

## Діаграма високого рівня

```
┌──────────────────────────────────────────────────────────────┐
│                    FRONTEND LAYER                            │
│  React SPA (5173) + Telegram Bot + Mobile (далі)             │
└────────────┬──────────────────────────┬──────────────────────┘
             │                          │
    ┌────────▼────────────┐  ┌─────────▼────────────┐
    │   API Gateway       │  │  WebSocket Gateway   │
    │   (FastAPI:80)      │  │  (Live drafts:9000)  │
    │   Rate limit        │  │  (Broadcast updates) │
    └────────┬────────────┘  └─────────┬────────────┘
             │                         │
┌────────────┴────────────────────────┴────────────────────────┐
│                    BACKEND SERVICES                          │
│                                                               │
│ ┌──────────────────┐ ┌──────────────────┐ ┌──────────────┐  │
│ │ DATA INGESTION   │ │    ANALYTICS     │ │  REFERENCE   │  │
│ │  Service :8001   │ │  Service :8003   │ │ DATA :8002   │  │
│ │                  │ │                  │ │              │  │
│ │ • Parser         │ │ • Meta Stats     │ │ • Sync heroes│  │
│ │ • Validator      │ │ • Draft Advisor  │ │ • Sync items │  │
│ │ • Normalizer     │ │ • Recommendations│ │ • Skills tree│  │
│ │ • Deduplicator   │ │ • Item builds    │ │ • Image URLs │  │
│ └──────────────────┘ │ • Economy pred   │ │ • Static data│  │
│                      │ • Lane matchups  │ └──────────────┘  │
│ ┌──────────────────┐ │                  │ ┌──────────────┐  │
│ │ ML/INSIGHTS      │ │ • Cache warm     │ │CACHE WARMER  │  │
│ │ Service :8004    │ └──────────────────┘ │ (cronjob)    │  │
│ │                  │                      │              │  │
│ │ • Scoring        │ ┌──────────────────┐ │ • Precompute │  │
│ │ • Validation     │ │ ADMIN SERVICE    │ │ • TTL manage │  │
│ │ • A/B testing    │ │ :8005            │ │ • Invalidate │  │
│ └──────────────────┘ │                  │ └──────────────┘  │
│                      │ • Overrides      │                    │
│                      │ • DB integrity   │                    │
│                      │ • Logs           │                    │
│                      └──────────────────┘                    │
└────────────┬──────────────────────┬────────────┬──────────────┘
             │                      │            │
    ┌────────▼───────────┐ ┌────────▼─────┐ ┌───▼──────┐
    │   PostgreSQL 15+   │ │  MongoDB 6+  │ │ Redis 7+ │
    │   (relations)      │ │ (matches)    │ │ (L1)     │
    └────────────────────┘ └──────────────┘ └──────────┘
```

## Основні принципи

1. **Layered isolation** — кожний сервіс знає тільки свою бізнес-логіку
2. **Event-driven** — матчі інгестуються → trigger rebuild → теплий cache
3. **Pre-computed first** — не рахуємо в runtime, рахуємо в batch jobs
4. **Cache-first reads** — Redis → PostgreSQL → MongoDB
5. **Async operations** — APScheduler для batch jobs, Celery для важких задач

---

# 🔧 МІКРОСЕРВІСИ

## 1️⃣ DATA INGESTION SERVICE (:8001)

### Відповідальність

- Fetch матчів з OpenDota API або user-uploaded JSON
- Parse & validate (Pydantic schemas)
- Deduplicate (перевірка MongoDB ingestion_log)
- Normalize (стандартизація назв полів, enums)
- Store до MongoDB
- Trigger сигналів rebuild

### API Endpoints

```
POST /ingest/opendota
  Input:  { match_id: int }
  Output: { match_id, status, error? }
  
POST /ingest/upload
  Input:  multipart/form-data (JSON file)
  Output: { match_id, status, error? }

GET /ingest/status/{match_id}
  Output: { status, attempts, last_error?, stored_at? }

GET /admin/ingestion-log
  Query:  ?status=ingested&limit=100&offset=0
  Output: { total, items: [...] }
```

### Internal Flow

```python
@router.post("/ingest/opendota")
async def ingest_opendota(match_id: int):
    # 1. Check MongoDB ingestion_log
    if exists_and_success:
        return { status: "duplicate" }
    
    # 2. Fetch from OpenDota
    raw_json = await opendota_client.fetch_match(match_id)
    
    # 3. Parse & validate
    match_dto = MatchSchema(**raw_json)
    
    # 4. Normalize
    normalized = normalize_match(match_dto)
    
    # 5. Store to MongoDB
    await db.matches.insert_one(normalized.dict())
    await db.ingestion_log.update_one(
        { "_id": match_id },
        { "$set": { "status": "ingested", "stored_at": now() } }
    )
    
    # 6. Trigger rebuild
    await publish_event("match.ingested", { match_id })
    
    return { match_id, status: "ingested" }
```

### DB Writes

**MongoDB:**
- `matches` — normalized match data
- `ingestion_log` — dedup + retry tracking

### Error Handling

```
Якщо валідація не пройде:
  → Store error в ingestion_log
  → Не insert у matches
  → Return error details
  
Якщо OpenDota timeout:
  → Exponential backoff (3 retries)
  → Store у ingestion_log.attempts
  → Return error після 3-го неудачного спроби
```

### Залежності

- OpenDota HTTP client (з retry/rate limit)
- MongoDB driver (PyMongo/Motor)
- Pydantic schemas
- Event bus (Redis Pub/Sub)

---

## 2️⃣ REFERENCE DATA SERVICE (:8002)

### Відповідальність

- Управління master data (heroes, items, skills)
- Sync з OpenDota (на запит / за розписанням)
- Store у PostgreSQL
- Expose via REST API
- Генерація static URLs для зображень
- Seed Redis cache при запуску

### API Endpoints

```
GET /heroes
  Query: ?filter=strength&limit=50
  Output: { total, items: [{ id, name, icon_url, ... }] }

GET /heroes/{hero_id}
  Output: { id, name, roles: [1,2,3], primary_attr, ... }

GET /items
  Query: ?min_cost=2000&max_cost=6000
  Output: { total, items: [...] }

GET /skills/{hero_id}
  Output: { hero_id, skills: [{ slot, name, description, ... }] }

POST /admin/sync-heroes
  Output: { synced: 127, errors: 0, updated_at }

POST /admin/sync-items
  Output: { synced: 470, errors: 0, updated_at }

GET /reference/version
  Output: { heroes_version, items_version, last_sync }
```

### PostgreSQL Schema

```sql
-- Master data
CREATE TABLE heroes (
  id INT PRIMARY KEY,
  name VARCHAR(100) UNIQUE NOT NULL,
  localized_name VARCHAR(100),
  primary_attr VARCHAR(20),      -- "str" | "agi" | "int"
  attack_type VARCHAR(20),        -- "melee" | "ranged"
  icon_url VARCHAR(255),
  roles TEXT[],                   -- array: [1, 2, 3]
  created_at TIMESTAMP DEFAULT now(),
  updated_at TIMESTAMP DEFAULT now()
);

CREATE TABLE items (
  id INT PRIMARY KEY,
  name VARCHAR(100) UNIQUE NOT NULL,
  cost INT,
  icon_url VARCHAR(255),
  item_type VARCHAR(50),          -- "weapon" | "armor" | etc
  created_at TIMESTAMP DEFAULT now()
);

CREATE TABLE hero_skills (
  id SERIAL PRIMARY KEY,
  hero_id INT NOT NULL REFERENCES heroes(id),
  skill_slot INT,                 -- 0-3
  skill_name VARCHAR(100),
  description TEXT,
  icon_url VARCHAR(255),
  cooldown FLOAT,
  mana_cost INT,
  created_at TIMESTAMP DEFAULT now()
);

CREATE TABLE item_categories (
  id INT PRIMARY KEY,
  name VARCHAR(100),
  description TEXT
);

CREATE TABLE item_to_category (
  item_id INT REFERENCES items(id),
  category_id INT REFERENCES item_categories(id),
  PRIMARY KEY (item_id, category_id)
);
```

### URL Pattern для зображень

```
Heroes:      /static/heroes/hero_{id}.jpg
Items:       /static/items/item_{id}.jpg
Skills:      /static/skills/skill_{hero_id}_{slot}.jpg
Attributes:  /static/attr/{attr}.png  (strength, agility, intelligence)
```

### Cache Strategy

```
При запуску сервісу:
  1. Load всі heroes з PostgreSQL → Redis
  2. Load всі items з PostgreSQL → Redis
  3. Set TTL = 24 hours

Redis keys:
  hero:all        → list of all heroes (з stats)
  hero:{id}       → single hero detail
  item:all        → list of all items
  item:{id}       → single item detail
  skill:{hero_id} → hero skills
```

---

## 3️⃣ ANALYTICS SERVICE (:8003)

### Відповідальність

- Генерація analytics views (read-only на PostgreSQL)
- Побудова draft рекомендацій (rule-based)
- Прогнози економіки гри
- Пропозиції build предметів
- Cache warm популярних запитів

### API Endpoints

```
# Meta статистика
GET /meta/heroes
  Query: ?role=1&days=30&patch=7.35
  Output: { heroes: [{ id, name, winrate, pickrate, ... }] }

GET /meta/heroes/{hero_id}
  Query: ?role=1
  Output: { hero_id, stats_by_role: { 1: {...}, 2: {...} } }

# Draft advisor
GET /draft/recommend
  Query: ?picks=1,2,3&bans=5,6&remaining_roles=1,4,5
  Output: {
    recommendations: [
      {
        hero_id: 10,
        role: 1,
        score: 7.8,
        breakdown: {
          synergy: 0.9,
          counters: 0.7,
          meta_weight: 0.6
        }
      }
    ]
  }

GET /draft/counters/{hero_id}
  Query: ?limit=5
  Output: { counters: [{ hero_id, counter_score, winrate_vs }] }

GET /draft/synergies/{hero_id}
  Query: ?limit=5
  Output: { allies: [{ hero_id, synergy_score, winrate_with }] }

# Рекомендації предметів
GET /heroes/{hero_id}/items
  Query: ?role=1&against_heroes=2,3,4
  Output: {
    item_builds: [
      {
        build_order: [item_1, item_2, ...],
        frequency: 0.45,
        win_rate: 0.62
      }
    ]
  }

# Прогнози економіки
GET /forecast/economy/{hero_id}
  Query: ?role=1
  Output: {
    gpm_curve: [420, 580, 750, 920],
    net_worth_curve: [2000, 8000, 15000, 25000]
  }

# Лінійні парри (lane advantage)
GET /matchup/lane/{hero_id}
  Query: ?vs_hero_id=2&role=1
  Output: {
    lane_score: 0.65,
    kill_potential: 0.7,
    farm_safety: 0.6
  }

# Trending герої
GET /meta/trending
  Query: ?days=7&trend_type=picked_increase|win_increase
  Output: { heroes: [{ id, trend, change_pct }] }

# Cache статус
GET /admin/cache-status
  Output: { cached_items: 150, cache_size_mb: 45, next_warm_at }
```

### Pre-computed таблиці (PostgreSQL)

```sql
CREATE TABLE hero_stats_computed (
  id SERIAL PRIMARY KEY,
  hero_id INT NOT NULL REFERENCES heroes(id),
  role INT NOT NULL,                          -- 1-5
  patch VARCHAR(20),                          -- "7.35d" or NULL
  days_back INT,                              -- 7, 14, 30 or NULL
  region VARCHAR(20),                         -- "us_west" or NULL
  
  -- Computed metrics
  matches_count INT,
  picks INT,
  wins INT,
  bans INT,
  
  winrate FLOAT,
  pickrate FLOAT,
  banrate FLOAT,
  
  avg_kills FLOAT,
  avg_deaths FLOAT,
  avg_assists FLOAT,
  kda FLOAT,
  
  avg_gpm INT,
  avg_xpm INT,
  avg_duration INT,
  
  updated_at TIMESTAMP DEFAULT now(),
  
  UNIQUE(hero_id, role, COALESCE(patch, -1), COALESCE(days_back, -1))
);

CREATE TABLE hero_matchup_computed (
  id SERIAL PRIMARY KEY,
  hero_id INT NOT NULL REFERENCES heroes(id),
  opponent_id INT NOT NULL REFERENCES heroes(id),
  role INT,
  vs_role INT,
  
  matches INT,
  wins INT,
  winrate FLOAT,
  
  updated_at TIMESTAMP DEFAULT now(),
  
  UNIQUE(hero_id, opponent_id, role, vs_role)
);

CREATE TABLE hero_synergy_computed (
  id SERIAL PRIMARY KEY,
  hero_id INT NOT NULL REFERENCES heroes(id),
  ally_id INT NOT NULL REFERENCES heroes(id),
  
  matches INT,
  wins INT,
  synergy_score FLOAT,
  
  updated_at TIMESTAMP DEFAULT now(),
  
  UNIQUE(hero_id, ally_id)
);

CREATE TABLE item_build_computed (
  id SERIAL PRIMARY KEY,
  hero_id INT NOT NULL REFERENCES heroes(id),
  role INT NOT NULL,
  
  item_sequence TEXT[],           -- ordered array of item IDs
  frequency FLOAT,                -- % times this build was picked
  win_rate_with FLOAT,            -- win rate
  avg_game_duration INT,
  
  updated_at TIMESTAMP DEFAULT now(),
  
  UNIQUE(hero_id, role, item_sequence)
);
```

### Batch Job: Rebuild Pre-computed

```python
# Trigger від:
# 1. Event: match.ingested (після N матчів)
# 2. Scheduled: кожні 30 хвилин (якщо AUTO_REBUILD)

async def rebuild_hero_stats():
    """Compute hero stats з MongoDB матчів"""
    # Aggregate matches по (hero_id, role, patch, days_back)
    # Calculate: winrate, pickrate, KDA, GPM, etc.
    # Upsert into PostgreSQL hero_stats_computed
    
async def rebuild_matchups():
    """Compute counter matrix"""
    
async def rebuild_synergies():
    """Compute ally synergies"""
    
async def rebuild_item_builds():
    """Compute item build recommendations"""
```

### Recommendation Scoring Formula

```python
def score_draft_recommendation(
    hero_id: int,
    role: int,
    picks: List[int],               # наші герої
    bans: List[int],                # бани противника
    enemy_heroes: List[int]         # якщо відомі
) -> DraftRecommendation:
    
    # Synergy з союзниками
    synergy_score = avg([get_synergy(hero_id, pick) for pick in picks])
    
    # Counter проти ворогів
    counter_score = 0.0
    if enemy_heroes:
        counter_score = avg([get_counter_score(hero_id, enemy) for enemy in enemy_heroes])
    
    # Поточна мета (pickrate + winrate)
    meta_score = get_meta_score(hero_id, role)
    
    # Final score: 35% synergy + 35% counter + 30% meta
    final_score = (
        synergy_score * 0.35 +
        counter_score * 0.35 +
        meta_score * 0.30
    )
    
    return {
        hero_id,
        role,
        score: final_score,
        breakdown: {
            synergy: synergy_score,
            counter: counter_score,
            meta_weight: meta_score
        }
    }
```

---

## 4️⃣ ML/INSIGHTS SERVICE (:8004)

### Відповідальність

- Train/validate моделей на pre-computed stats
- Score рекомендацій з ML weights
- Predict item builds (classifier)
- Predict economy curves (regression)
- Win probability forecasts
- A/B test framework

### API Endpoints

```
POST /ml/predict/item-build
  Input: { hero_id, role, enemy_heroes, ally_heroes }
  Output: {
    primary_build: [item_ids],
    secondary_build: [item_ids],
    confidence: 0.78
  }

POST /ml/predict/economy
  Input: { hero_id, role, level }
  Output: {
    expected_gpm: 650,
    expected_net_worth: 12000,
    confidence: 0.82
  }

POST /ml/predict/win-probability
  Input: {
    radiant: [hero_ids],
    dire: [hero_ids],
    game_time?: 1200
  }
  Output: {
    win_probability: 0.62,
    confidence: 0.75,
    factors: {
      draft_advantage: 0.05,
      economy: 0.10,
      networth: -0.03
    }
  }

GET /ml/models
  Output: {
    models: [
      {
        name: "item_build_classifier",
        version: "1.0",
        accuracy: 0.82,
        f1_score: 0.79
      }
    ]
  }
```

### ML Models (Phase 2)

| Модель | Input | Output | Тип | Target Accuracy |
|--------|-------|--------|------|-----------------|
| Item Build Classifier | hero + role + enemies | item sequence | Classification | 75%+ |
| Economy Regressor | hero + role + game_time | GPM/net_worth | Regression | MAE < 100 |
| Win Probability | draft + economy | win prob | Classification | 65%+ |

---

## 5️⃣ CACHE WARMER SERVICE

### Відповідальність

- Pre-compute популярних запитів
- Warm Redis кожні 30 хвилин
- Manage TTL
- Invalidate після ingest матчів

### Cron Jobs

```python
# Кожні 30 хвилин
async def warm_meta_stats():
    """Pre-compute hero stats для всіх ролей"""
    for role in [1, 2, 3, 4, 5]:
        for days in [7, 14, 30]:
            stats = await analytics.get_meta_heroes(role=role, days=days)
            await redis.set(f"meta:role:{role}:days:{days}", json.dumps(stats))

# Кожну годину
async def warm_item_builds():
    """Pre-compute item builds для всіх героїв"""
    for hero_id in range(1, 128):
        for role in [1, 2, 3, 4, 5]:
            builds = await analytics.get_item_builds(hero_id, role)
            await redis.set(f"items:hero:{hero_id}:role:{role}", json.dumps(builds))

# На запит (після ingest матчу)
async def warm_counters(hero_id: int):
    """Invalidate та re-warm counter дані"""
    await redis.delete(f"counter:matrix:{hero_id}")
    counters = await analytics.get_counters(hero_id)
    await redis.set(f"counter:matrix:{hero_id}", json.dumps(counters), ex=3600)
```

### Event Handler

```python
# Subscribe на events
@event_bus.on("match.ingested")
async def on_match_ingested(match_id: int):
    """Trigger warm після batch матчів"""
    recent = await db.ingestion_log.count_recent(minutes=5)
    if recent >= 10:  # batch threshold
        await warm_all()
```

---

## 6️⃣ ADMIN SERVICE (:8005)

### Відповідальність

- Ручні корекції даних (для фіксів)
- DB integrity checks
- Logs & monitoring
- System health

### Endpoints

```
POST /admin/override/hero-stats
  Input: {
    hero_id, role, patch,
    winrate_override, pickrate_override,
    reason: "balance patch not yet synced"
  }

GET /admin/overrides
  Output: { overrides: [...], total: N }

DELETE /admin/overrides/{id}

POST /admin/rebuild-now
  Input: { what: "all" | "matchups" | "item_builds" }

GET /admin/health
  Output: {
    services: {
      ingestion: "ok",
      analytics: "ok",
      postgres: "ok",
      mongodb: "ok",
      redis: "ok"
    }
  }

POST /admin/clear-cache
  Input: { pattern: "meta:*" }
```

---

# 🗄️ СХЕМИ БД

## PostgreSQL (Relations + Pre-computed)

**Мета:** Структуровані дані, аналітика, транзакції

Детально описано вище в сервісах ✅

## MongoDB (Matches + Logs)

**Мета:** Гнучка схема для match data, append-only logs

```javascript
// matches collection
{
  _id: ObjectId,
  match_id: 7123456789,
  source: "opendota",
  duration: 2345,
  radiant_win: true,
  start_time: 1710000000,
  patch: "7.35d",
  
  radiant: {
    players: [
      {
        account_id: 123456,
        hero_id: 1,
        role: 1,
        lane_role: "safe",
        level: 25,
        kills: 12,
        deaths: 3,
        assists: 18,
        gpm: 650,
        xpm: 850,
        net_worth: 25000,
        last_hits: 450,
        hero_damage: 35000,
        tower_damage: 2000,
        healing: 5000,
        items: [1, 2, 3, 4, 5, 6]
      }
    ]
  },
  
  dire: { /* same */ },
  
  events: [
    {
      type: "hero_kill" | "tower_destroyed" | "roshan",
      timestamp: 600,
      radiant_heroes: [1, 2],
      dire_heroes: [3, 4]
    }
  ],
  
  processed: true,
  ingested_at: ISODate("2025-03-24T12:00:00Z"),
  version: 1
}

// ingestion_log collection
{
  _id: match_id,
  source: "opendota" | "user",
  status: "pending" | "ingested" | "invalid" | "duplicate",
  error: null,
  attempts: 2,
  last_attempt: ISODate("2025-03-24T12:00:00Z"),
  stored_at: ISODate
}
```

### Індекси

```javascript
db.matches.createIndex({ "match_id": 1 }, { unique: true })
db.matches.createIndex({ "start_time": 1 })
db.matches.createIndex({ "patch": 1 })
db.matches.createIndex({ "ingested_at": 1 })

db.ingestion_log.createIndex({ "status": 1 })
db.ingestion_log.createIndex({ "last_attempt": 1 })
```

## Redis (L1 Cache)

**Мета:** Hot data, швидкі lookups

```
# Meta stats
hero:meta:role:{role}:days={days}        → JSON
hero:meta:all                             → List<hero>

# Reference data
hero:all                                  → List<hero>
hero:{id}                                 → Hero JSON
item:all                                  → List<item>
item:{id}                                 → Item JSON

# Draft advisor
draft:reco:{picks_hash}                   → Recommendation JSON (TTL: 5 min)
counter:matrix:{hero_id}                  → Counter matrix (TTL: 1 hour)
synergy:matrix:{hero_id}                  → Synergy matrix (TTL: 1 hour)

# Item builds
item:build:{hero_id}:{role}               → Build JSON (TTL: 2 hours)
```

---

# 📡 API КОНТРАКТИ

## API Gateway (:80)

```
/api/v1/reference/*        → Reference Data Service (:8002)
/api/v1/analytics/*        → Analytics Service (:8003)
/api/v1/ml/*               → ML Service (:8004)
/api/v1/admin/*            → Admin Service (:8005)
/ws/*                      → WebSocket Gateway (:9000)
```

## Authentication (Phase 2)

```
Header: Authorization: Bearer {jwt_token}
Payload: { user_id, role: "user" | "admin", exp }
```

## Rate Limiting

```
Default:           100 req/min per IP
Authenticated:     500 req/min per user
Admin:             Unlimited

Stricter limits:
POST /ingest/*             → 10 req/min
POST /admin/*              → 5 req/min
```

## Error Response

```json
{
  "error": "string",
  "code": "error_code",
  "status": 400,
  "timestamp": "2025-03-24T12:00:00Z",
  "request_id": "uuid"
}
```

## Success Response

```json
{
  "data": { /* endpoint-specific */ },
  "meta": {
    "timestamp": "2025-03-24T12:00:00Z",
    "request_id": "uuid"
  }
}
```

---

# 🔄 DATA FLOWS

## Flow 1: New Match Ingestion (Новий матч)

```
1. POST /api/v1/ingest/opendota?match_id=123
   ↓
2. DATA INGESTION SERVICE:
   a. Check MongoDB dedup
   b. Fetch from OpenDota
   c. Validate (Pydantic)
   d. Normalize
   e. Store to MongoDB
   f. Update ingestion_log
   ↓
3. Publish event: "match.ingested"
   ↓
4. CACHE WARMER (listening):
   a. Counter++
   b. If counter >= 10 (за 5 хв):
      → Publish: "rebuild.requested"
   ↓
5. REBUILD JOB:
   a. rebuild_hero_stats()
   b. rebuild_matchups()
   c. rebuild_synergies()
   d. rebuild_item_builds()
   e. Update PostgreSQL
   ↓
6. CACHE WARMER (on completed):
   a. Invalidate Redis: meta:*, counter:*, synergy:*
   b. Warm cache
   ↓
7. Return: { match_id, status: "ingested" }
```

## Flow 2: Draft Advisory Request

```
1. Frontend: GET /api/v1/analytics/draft/recommend?picks=1,2,3&bans=5,6
   ↓
2. API GATEWAY → ANALYTICS SERVICE
   ↓
3. ANALYTICS SERVICE:
   a. Check Redis cache
   b. If cached: return
   c. If not:
      → Load from PostgreSQL
      → Call ML SERVICE for scoring
      → Cache result (TTL: 5 min)
      → Return recommendations
   ↓
4. Frontend: [ { hero_id, role, score, breakdown } ]
```

## Flow 3: Meta Stats View

```
1. GET /api/v1/analytics/meta/heroes?role=1&days=30
   ↓
2. ANALYTICS SERVICE:
   a. Check Redis: hero:meta:role:1:days:30
   b. If hot: return
   c. If cold:
      → Query PostgreSQL hero_stats_computed
      → Check overrides
      → Apply overrides
      → Return
```

---

# 🚀 MVP SCOPE

## Phase 1: MVP (Тижні 1-4)

### Epic 1: Foundation & Infrastructure
- [ ] Project структура + Docker setup
- [ ] PostgreSQL + MongoDB + Redis setup
- [ ] API Gateway (FastAPI)
- [ ] DB schemas (все 3)

### Epic 2: Data Ingestion
- [ ] OpenDota HTTP client (retry/rate limit)
- [ ] Match parser + validator (Pydantic)
- [ ] MongoDB ingestion
- [ ] Deduplication

### Epic 3: Reference Data
- [ ] Heroes sync
- [ ] Items sync
- [ ] Image URL generation
- [ ] Redis cache seeding

### Epic 4: Basic Analytics
- [ ] rebuild_hero_stats batch job
- [ ] rebuild_matchups batch job
- [ ] rebuild_synergies batch job
- [ ] GET /meta/heroes endpoint
- [ ] GET /draft/counters endpoint

### Epic 5: Draft Advisor (Rule-based)
- [ ] Synergy scorer
- [ ] Counter scorer
- [ ] Meta weight scorer
- [ ] GET /draft/recommend endpoint
- [ ] Redis caching

### Epic 6: Frontend MVP
- [ ] React + Vite + TypeScript
- [ ] Hero stats table
- [ ] Draft advisor UI
- [ ] Responsive design

**Total Story Points (MVP):** ~150 points

---

## Phase 2: Enhanced Analytics (Тижні 5-8)

- [ ] ML Service (item classifier, economy regressor)
- [ ] Item build recommendations
- [ ] Economy forecasts
- [ ] Lane matchup scoring
- [ ] Win probability predictions
- [ ] Advanced frontend

---

## Phase 3: Scale & Production (Тижні 9+)

- [ ] Authentication (JWT)
- [ ] Admin panel
- [ ] Monitoring
- [ ] Rate limiting
- [ ] Telegram bot
- [ ] Mobile app
- [ ] Production deployment

---

# 📊 EPICS & TASKS

## Epic 1: Foundation & Infrastructure (15 tasks)

| Task | Опис | Points | Owner |
|------|------|--------|-------|
| 1.1 | Project bootstrap: Python 3.11+, poetry, structure | 3 | - |
| 1.2 | Docker: Dockerfile, docker-compose.yml | 5 | - |
| 1.3 | API Gateway: FastAPI, routing, middleware | 5 | - |
| 1.4 | Logging: structlog, JSON output | 3 | - |
| 1.5 | Config: pydantic-settings, .env | 2 | - |
| 1.6 | DB connections: SQLAlchemy, PyMongo, aioredis | 5 | - |
| 1.7 | Health endpoints: /health, /ready | 2 | - |
| 1.8 | Swagger docs + ReDoc | 2 | - |

---

## Epic 2: Data Ingestion Service (10 tasks)

| Task | Опис | Points | Owner |
|------|------|--------|-------|
| 2.1 | OpenDota HTTP client: fetch, retry | 5 | - |
| 2.2 | Pydantic schemas: Match, Player validation | 5 | - |
| 2.3 | Normalizer: field names, enums | 3 | - |
| 2.4 | MongoDB writer: insert matches | 3 | - |
| 2.5 | Deduplication | 2 | - |
| 2.6 | Error handling | 3 | - |
| 2.7 | Unit + integration tests | 5 | - |
| 2.8 | Endpoints | 3 | - |

---

## Epic 3: Reference Data Service (10 tasks)

| Task | Опис | Points | Owner |
|------|------|--------|-------|
| 3.1 | Sync heroes | 3 | - |
| 3.2 | Sync items | 3 | - |
| 3.3 | Image URL generation | 2 | - |
| 3.4 | Redis cache seeding | 3 | - |
| 3.5 | Hero skills | 3 | - |
| 3.6 | GET endpoints | 3 | - |
| 3.7 | Admin endpoints | 2 | - |
| 3.8 | Tests | 3 | - |

---

## Epic 4: Basic Analytics (12 tasks)

| Task | Опис | Points | Owner |
|------|------|--------|-------|
| 4.1 | rebuild_hero_stats | 5 | - |
| 4.2 | rebuild_matchups | 5 | - |
| 4.3 | rebuild_synergies | 5 | - |
| 4.4 | PostgreSQL tables | 3 | - |
| 4.5 | Endpoints | 3 | - |
| 4.6 | Event handler | 3 | - |
| 4.7 | Tests | 5 | - |

---

## Epic 5: Draft Advisor (8 tasks)

| Task | Опис | Points | Owner |
|------|------|--------|-------|
| 5.1 | Synergy scorer | 3 | - |
| 5.2 | Counter scorer | 3 | - |
| 5.3 | Meta weight | 2 | - |
| 5.4 | Final score formula | 2 | - |
| 5.5 | GET endpoint | 3 | - |
| 5.6 | Redis cache | 2 | - |
| 5.7 | Tests | 3 | - |

---

## Epic 6: Frontend MVP (10 tasks)

| Task | Опис | Points | Owner |
|------|------|--------|-------|
| 6.1 | React + Vite + TypeScript | 3 | - |
| 6.2 | API client | 3 | - |
| 6.3 | Hero stats table | 5 | - |
| 6.4 | Draft advisor UI | 5 | - |
| 6.5 | Hero detail page | 5 | - |
| 6.6 | Responsive design | 3 | - |
| 6.7 | Loading + errors | 2 | - |
| 6.8 | Tests | 5 | - |

---

# 📈 МЕТРИКИ УСПІХУ

## Phase 1 Acceptance Criteria

### Якість даних
- ✅ 500+ матчів ingested
- ✅ Deduplication: < 1% дублів
- ✅ Validation: 100% invalid матчів перехоплені
- ✅ Normalization: назви полів стандартизовані

### Accuracy аналітики
- ✅ Hero stats: ± 2% від OpenDota
- ✅ Counter matrix: ≥ 50 matches per pair
- ✅ Synergy: ≥ 50 matches per pair

### Performance
- ✅ GET /meta/heroes: < 100ms (Redis hot)
- ✅ GET /draft/recommend: < 200ms
- ✅ Batch rebuild: < 5 min для 500 матчів

### Надійність
- ✅ API uptime: 99.5%
- ✅ OpenDota success rate: > 95%
- ✅ DB queries: < 0.1% failures

### Frontend
- ✅ Lighthouse score: > 80
- ✅ Mobile: responsive на всіх breakpoints
- ✅ Draft advisor: рекомендація < 1s

---

# 💻 ТЕХНОЛОГІЧНИЙ СТЕК

## Backend

```
Language:        Python 3.11+
Web Framework:   FastAPI 0.115.0
ORM:             SQLAlchemy 2.0 + alembic
NoSQL:           PyMongo 4.6 / Motor 3.3
Cache:           aioredis 2.0
Validation:      Pydantic v2.0
Data:            numpy, pandas
ML:              scikit-learn 1.3 (Phase 2)
Scheduler:       APScheduler 3.10
Logger:          structlog 23.2
Testing:         pytest 7.4 + pytest-asyncio
HTTP:            httpx 0.25
```

## Frontend

```
Runtime:         Node.js 18+
Framework:       React 19.0
Build:           Vite 7.0
Language:        TypeScript 5.3
State:           TanStack Query v5
Styling:         Tailwind CSS 3.3
WebSocket:       socket.io-client 4.7
Testing:         Vitest + React Testing Library
```

## DevOps

```
Containers:      Docker + docker-compose
CI/CD:           GitHub Actions
VCS:             Git
API Docs:        Swagger/OpenAPI 3.0
```

## Services

```
PostgreSQL:  15.2+
MongoDB:     6.0+
Redis:       7.2+
```

---

# 📝 НАСТУПНІ КРОКИ

1. ✅ **ТЗ готове** — українська + англійські терміни
2. 🔄 **Твоє ревю** — зміни, дополнення, уточнення
3. 📐 **Деталізація** — break-down Epics 1-2 на dev tasks
4. 📊 **Database migrations** — SQL schema files
5. ⚙️ **Стартові конфіги** — docker-compose, .env templates
6. 🚀 **Kickoff** — розподіл задач, sprint planning

---

## Питання для уточнення

1. ❓ Архітектура мікросервісів — ОК? Щось змінити?
2. ❓ PostgreSQL + MongoDB + Redis — правильна комбінація?
3. ❓ Draft scoring (35/35/30) — збалансовано?
4. ❓ MVP за 4 тижні — реалістично?
5. ❓ Чого не вистачає в ТЗ перед стартом?

---

**Автор:** recombinationBTRDRS + AI Assistant  
**Дата редакції:** 2025-03-24  
**Статус:** 🟢 Готове до перегляду
