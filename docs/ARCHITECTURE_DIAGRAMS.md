# 🏗️ DOTA 2 ANALYTICS v2.0 — АРХІТЕКТУРА (ДІАГРАМИ)

---

# 1️⃣ ЗАГАЛЬНА АРХІТЕКТУРА

```
┌──────────────────────────────────────────────────────────────────┐
│                        USERS / CLIENTS                           │
│     (Web Browser + Telegram Bot + Future Mobile App)             │
└────────────────┬─────────────────────────────────┬───────────────┘
                 │                                 │
         ┌───────▼──────────────┐        ┌────────▼──────────────┐
         │   REST API CALLS     │        │  WebSocket LIVE DRAFT │
         │  (JSON responses)    │        │  (Real-time updates)  │
         └───────┬──────────────┘        └────────┬──────────────┘
                 │                                 │
         ┌───────┴─────────────────────────────────┴───────────────┐
         │                                                          │
         │           🌐 API GATEWAY (FastAPI :80)                  │
         │        Rate limiting + CORS + Versioning               │
         │                                                          │
         └────┬──────────────┬──────────────┬──────────────┬───────┘
              │              │              │              │
         ┌────▼────┐    ┌────▼────┐  ┌────▼────┐  ┌────▼────┐
         │Reference │   │Analytics │  │  Admin  │  │   ML    │
         │  Data    │   │ Service  │  │Service  │  │Service  │
         │ :8002    │   │  :8003   │  │ :8005   │  │ :8004   │
         └────┬────┘    └────┬────┘  └────┬────┘  └────┬────┘
              │              │            │            │
              │        ┌─────▼──────┐     │            │
              │        │ Data       │     │            │
              │        │ Ingestion  │     │            │
              │        │ :8001      │     │            │
              │        └─────┬──────┘     │            │
              │              │            │            │
         ┌────┴──────┬───────┴──────┬────┴────┬───────┴─────┐
         │            │              │         │             │
    ┌────▼────┐  ┌───▼─────┐  ┌────▼───┐ ┌──▼──┐  ┌───────▼──┐
    │PostgreSQL│  │ MongoDB │  │ Redis  │ │Care │  │ Cache    │
    │(relations)  │ (matches)  │(L1)   │ │Warmer   │(Scheduler)
    │& computed   └──────────┘  └──────┘ └─────┘  └──────────┘
    └────────────────────────────────────────────────────────────┘
```

---

# 2️⃣ MICROSERVICES DETAIL

## Data Ingestion Service (:8001)

```
┌─────────────────────────────────────────────────┐
│  DATA INGESTION SERVICE                         │
│  ┌───────────────────────────────────────────┐  │
│  │ OpenDota / User Upload                    │  │
│  └──────────────┬──────────────────────────┘  │
│                 │                             │
│       ┌─────────▼──────────┐                 │
│       │ HTTP Client        │                 │
│       │ (retry/backoff)    │                 │
│       └─────────┬──────────┘                 │
│                 │                             │
│       ┌─────────▼──────────┐                 │
│       │ Parser + Validator │                 │
│       │ (Pydantic Schema)  │                 │
│       └─────────┬──────────┘                 │
│                 │                             │
│       ┌─────────▼──────────┐                 │
│       │ Normalizer         │                 │
│       │ (standardize)      │                 │
│       └─────────┬──────────┘                 │
│                 │                             │
│       ┌─────────▼──────────┐                 │
│       │ MongoDB Writer     │                 │
│       │ (dedup + save)     │                 │
│       └─────────┬──────────┘                 │
│                 │                             │
│       ┌─────────▼──────────┐                 │
│       │ Publish Event      │                 │
│       │ "match.ingested"   │                 │
│       └────────────────────┘                 │
│                                              │
└──────────────────────────────────────────────┘
```

## Reference Data Service (:8002)

```
┌──────────────────────────────────────────┐
│  REFERENCE DATA SERVICE                  │
│  ┌────────────────────────────────────┐  │
│  │ Sync Heroes / Items from OpenDota  │  │
│  └──────────┬───────────────────────┘  │
│             │                          │
│  ┌──────────▼────────┐  ┌────────────┐ │
│  │ PostgreSQL Write  │  │ Image URL  │ │
│  │ (heroes, items)   │  │ Generation │ │
│  └──────────┬────────┘  └────────────┘ │
│             │                          │
│  ┌──────────▼────────┐                 │
│  │ Redis Cache Seed  │                 │
│  │ (on startup)      │                 │
│  └───────────────────┘                 │
│                                        │
│ Endpoints:                             │
│ GET /heroes                            │
│ GET /heroes/{id}                       │
│ GET /items                             │
│ GET /skills/{hero_id}                  │
└────────────────────────────────────────┘
```

## Analytics Service (:8003)

```
┌─────────────────────────────────────────────────┐
│  ANALYTICS SERVICE                              │
│                                                 │
│  ┌──────────────────────────────────────────┐  │
│  │ PostgreSQL Pre-computed Reader           │  │
│  │ (hero_stats_computed, matchups, etc)     │  │
│  └──────────────────────────────────────────┘  │
│                                                 │
│  ┌──────────────────────────────────────────┐  │
│  │ Batch Job Trigger                        │  │
│  │ (listen to match.ingested → rebuild)     │  │
│  └──────────────────────────────────────────┘  │
│                                                 │
│  ┌─────────────────┐  ┌──────────────────┐   │
│  │ Hero Stats Agg  │  │ Matchup Matrix   │   │
│  │ rebuild         │  │ rebuild          │   │
│  └─────────────────┘  └──────────────────┘   │
│                                                 │
│  ┌─────────────────┐  ┌──────────────────┐   │
│  │ Synergy Compute │  │ Item Build Agg   │   │
│  │ rebuild         │  │ rebuild          │   │
│  └─────────────────┘  └──────────────────┘   │
│                                                 │
│  ┌──────────────────────────────────────────┐  │
│  │ Recommendation Scorer                    │  │
│  │ (synergy + counter + meta = score)       │  │
│  └──────────────────────────────────────────┘  │
│                                                 │
│ Endpoints:                                     │
│ GET /meta/heroes                              │
│ GET /draft/recommend                          │
│ GET /draft/counters/{hero_id}                 │
│ GET /draft/synergies/{hero_id}                │
└─────────────────────────────────────────────────┘
```

## ML/Insights Service (:8004)

```
┌──────────────────────────────────────────┐
│  ML/INSIGHTS SERVICE (Phase 2)           │
│                                          │
│  ┌──────────────────────────────────┐   │
│  │ Models Training                  │   │
│  │ • Item Build Classifier          │   │
│  │ • Economy Regressor              │   │
│  │ • Win Probability Model          │   │
│  └──────────────────────────────────┘   │
│                                          │
│  ┌──────────────────────────────────┐   │
│  │ Model Serving + Scoring          │   │
│  │ • Predict item builds            │   │
│  │ • Forecast economy curves        │   │
│  │ • Win prob calculations          │   │
│  └──────────────────────────────────┘   │
│                                          │
│  ┌──────────────────────────────────┐   │
│  │ A/B Testing Framework            │   │
│  │ (validate model accuracy)        │   │
│  └──────────────────────────────────┘   │
│                                          │
│ Endpoints:                              │
│ POST /ml/predict/item-build             │
│ POST /ml/predict/economy                │
│ POST /ml/predict/win-probability        │
└──────────────────────────────────────────┘
```

## Quality Assessment Service (:8006, Phase 2)

```
┌────────────────────────────────────────────┐
│  QUALITY ASSESSMENT SERVICE (Phase 2)      │
│                                            │
│  ┌──────────────────────────────────────┐ │
│  │ Detectors                            │ │
│  │ • RoleMismatchDetector               │ │
│  │ • UnconventionalBuildDetector        │ │
│  │ • SmurfDetector                      │ │
│  │ • IntingDetector                     │ │
│  │ • StompDetector                      │ │
│  └──────────────────────────────────────┘ │
│                                            │
│  ┌──────────────────────────────────────┐ │
│  │ Quality Scoring                      │ │
│  │ (flags → quality_score 0-100)        │ │
│  └──────────────────────────────────────┘ │
│                                            │
│ Endpoints:                                │
│ POST /assess/player/{player_id}/match/{id} │
│ POST /assess/match/{match_id}             │
│ GET /assess/account/{account_id}          │
└────────────────────────────────────────────┘
```

---

# 3️⃣ DATA FLOW DIAGRAM

## New Match Ingest Flow

```
User / Webhook
    │
    ▼
POST /api/v1/ingest/opendota?match_id=123
    │
    ├─→ DATA INGESTION SERVICE
    │   ├─ Check MongoDB (dedup)
    │   ├─ Fetch OpenDota
    │   ├─ Parse (Pydantic)
    │   ├─ Normalize
    │   ├─ Store MongoDB
    │   └─ Publish: "match.ingested"
    │
    ├─→ CACHE WARMER (listener)
    │   ├─ Count recent ingests
    │   ├─ If >= 10 in 5 min:
    │   │   └─ Publish: "rebuild.requested"
    │   │
    │   └─→ ANALYTICS SERVICE (rebuild batch)
    │       ├─ rebuild_hero_stats()
    │       ├─ rebuild_matchups()
    │       ├─ rebuild_synergies()
    │       ├─ rebuild_item_builds()
    │       └─ Store PostgreSQL
    │
    └─→ CACHE WARMER (on completed)
        ├─ Invalidate Redis keys
        └─ Warm cache with new data

Response to user:
    { match_id, status: "ingested" }
```

## Draft Recommendation Flow

```
User: "I have picks [1,2,3], bans [5,6], what hero should I pick?"
    │
    ▼
GET /api/v1/analytics/draft/recommend?picks=1,2,3&bans=5,6
    │
    ├─→ API GATEWAY
    │   └─ Route to ANALYTICS SERVICE
    │
    └─→ ANALYTICS SERVICE
        ├─ Check Redis cache: draft:reco:{hash}
        │   │
        │   ├─ HIT: return immediately
        │   │
        │   └─ MISS:
        │       ├─ Load from PostgreSQL
        │       │  (hero_stats_computed, matchups, synergies)
        │       │
        │       ├─→ RECOMMENDATION SCORER
        │       │   ├─ For each hero (1-127):
        │       │   │   ├─ synergy_score = avg(synergy with picks)
        │       │   │   ├─ counter_score = avg(counter vs bans)
        │       │   │   ├─ meta_score = pickrate × winrate
        │       │   │   └─ final = 0.35*syn + 0.35*cnt + 0.30*meta
        │       │   │
        │       │   └─ Return top 10 recommendations
        │       │
        │       ├─ Cache result (TTL: 5 min)
        │       └─ Return to user
    │
    ▼
Response: [ { hero_id, role, score, breakdown } ]
```

---

# 4️⃣ DATABASE ARCHITECTURE

```
┌─────────────────────────────────────┐
│         POSTGRESQL 15+              │
│      (Relations + Pre-computed)      │
│                                     │
│  Master Data:                       │
│  • heroes                           │
│  • items                            │
│  • hero_skills                      │
│                                     │
│  Pre-computed Analytics:            │
│  • hero_stats_computed              │
│  • hero_matchup_computed            │
│  • hero_synergy_computed            │
│  • item_build_computed              │
│                                     │
│  Metadata:                          │
│  • hero_stats_overrides             │
│  • data_sync_log                    │
│  • rebuild_jobs                     │
│  • assessment results (Phase 2)     │
└─────────────────────────────────────┘

┌─────────────────────────────────────┐
│        MONGODB 6.0+                 │
│    (Flexible JSON Documents)        │
│                                     │
│  Collections:                       │
│  • matches                          │
│    ├─ match_id (unique)             │
│    ├─ radiant: { players: [...] }   │
│    ├─ dire: { players: [...] }      │
│    ├─ events: [...]                 │
│    └─ processed: boolean            │
│                                     │
│  • ingestion_log                    │
│    ├─ _id: match_id                 │
│    ├─ status: enum                  │
│    ├─ error: string                 │
│    └─ attempts: int                 │
│                                     │
│  Indexes:                           │
│  • match_id (unique)                │
│  • start_time                       │
│  • patch                            │
│  • ingested_at                      │
└─────────────────────────────────────┘

┌─────────────────────────────────────┐
│         REDIS 7.2+                  │
│       (L1 Hot Cache)                │
│                                     │
│  Keys (TTL-managed):                │
│  • hero:all                         │
│  • hero:{id}                        │
│  • item:all                         │
│  • item:{id}                        │
│                                     │
│  • hero:meta:role:{r}:days={d}     │
│  • counter:matrix:{hero_id}         │
│  • synergy:matrix:{hero_id}         │
│  • item:build:{hero_id}:{role}     │
│                                     │
│  • draft:reco:{picks_hash}          │
│    (TTL: 5 min)                     │
│                                     │
│  Metadata:                          │
│  • cache:last_warm                  │
│  • cache:status                     │
└─────────────────────────────────────┘
```

---

# 5️⃣ DEPLOYMENT TOPOLOGY (Docker Compose)

```
┌──────────────────────────────────────────────────────┐
│         DOCKER COMPOSE (dev)                         │
│                                                      │
│  ┌────────────────────────────────────────────────┐ │
│  │ Services Network (bridge)                      │ │
│  │                                                │ │
│  │  api-gateway:80      (FastAPI)                 │ │
│  │  ingestion:8001      (FastAPI)                 │ │
│  │  reference:8002      (FastAPI)                 │ │
│  │  analytics:8003      (FastAPI)                 │ │
│  │  ml:8004             (FastAPI)                 │ │
│  │  admin:8005          (FastAPI)                 │ │
│  │  quality:8006        (FastAPI) [Phase 2]       │ │
│  │  cache-warmer        (APScheduler job)         │ │
│  │                                                │ │
│  │  postgres:5432       (DB)                      │ │
│  │  mongodb:27017       (DB)                      │ │
│  │  redis:6379          (Cache)                   │ │
│  │                                                │ │
│  │  frontend:5173       (Vite dev server)         │ │
│  └────────────────────────────────────────────────┘ │
│                                                      │
│  Volume mounts:                                     │
│  • ./services -> /app (code)                        │
│  • postgres_data                                    │
│  • mongo_data                                       │
│  • redis_data                                       │
└──────────────────────────────────────────────────────┘
```

---

# 6️⃣ REQUEST / RESPONSE EXAMPLE

## Get Draft Recommendations

### Request
```
GET /api/v1/analytics/draft/recommend?picks=1,2,3&bans=5,6&remaining_roles=1,4,5
Authorization: Bearer {token}
X-Request-ID: uuid-123
```

### Response (200 OK)
```json
{
  "data": {
    "recommendations": [
      {
        "hero_id": 10,
        "hero_name": "Morphling",
        "role": 1,
        "score": 8.2,
        "breakdown": {
          "synergy": 0.85,
          "counter": 0.75,
          "meta_weight": 0.80
        }
      },
      {
        "hero_id": 45,
        "hero_name": "Anti-Mage",
        "role": 1,
        "score": 7.9,
        "breakdown": {
          "synergy": 0.80,
          "counter": 0.70,
          "meta_weight": 0.85
        }
      }
    ],
    "cached_from": "redis" | "computed"
  },
  "meta": {
    "timestamp": "2025-03-24T12:00:00Z",
    "request_id": "uuid-123"
  }
}
```

---

# 7️⃣ DEPLOYMENT PHASES

## Phase 1: MVP (Local Dev)
```
docker-compose up
→ All services running locally
→ PostgreSQL + MongoDB + Redis
→ Frontend on localhost:5173
```

## Phase 2: Staging (Docker)
```
Docker images for each service
→ Push to registry
→ Deploy to cloud VM
→ Real domain + SSL
→ Monitoring stack
```

## Phase 3: Production
```
Kubernetes cluster
→ Auto-scaling
→ Load balancing
→ High availability
→ CDN for frontend
```

---

**Версія:** 1.0  
**Статус:** 🟢 Reference  
**Для:** Швидкого ознайомлення з архітектурою
