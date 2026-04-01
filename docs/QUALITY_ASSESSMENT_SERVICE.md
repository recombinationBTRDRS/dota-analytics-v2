# 🔍 QUALITY ASSESSMENT SERVICE (:8006)

## Огляд

**Мета:** Оцінювати якість гейм-плею на основі match data - виявляти проблемні матчі, аномальне поведення, нелогічні дії тощо.

**Статус:** 🔜 Phase 2 (додається до архітектури)

---

# 📊 ЧТО ОЦІНЮЄМО

## 1️⃣ Player Quality Metrics

### Основні індикатори

| Метрика | Опис | Alert Threshold |
|---------|------|-----------------|
| **Role Mismatch** | Герой/роль не збігаються (carry з 150 LH за 30 хв) | LH < 100 for carry |
| **Farming Anomaly** | GPM far away від середнього по герою | GPM < 50% avg for role |
| **Position Abuse** | Supp який фармить мейн палач, або carry який не фармить | xpm > expected, gold/minute analysis |
| **Unconventional Build** | Дивні предмети (6x Boots, Aghs на carry, etc) | Item frequency < 5% |
| **Skill Build Anomaly** | Дивне розповсюдження скилів (лев усі в одне) | Pattern analysis |

---

## 2️⃣ Game-level Quality Indicators

### Match Quality Scoring

| Індикатор | Що означає | How to detect |
|-----------|-----------|------------|
| **Smurf Detection** | Низький рейтинг, але очень високі KDA / Networth | High KDA (>8.0) + Low bracket |
| **Booster Detection** | Нетипово висока перформанс протягом сесії | Multiple games with >20 kills |
| **Inting (Intentional Feeding)** | Навмисне програвання матчу | Deaths in obvious positions, no items, etc |
| **Ruined Game** | Матч был явно зіпсований (team feeding, disconnect, etc) | 5+ consecutive deaths in first 5 min |
| **Stomp Game** | Один тім мав безумовну перевагу (ММР дисбаланс) | Networth difference > 40k by min 30 |

---

## 3️⃣ Team Coordination Metrics

### Як команда гралась

| Метрика | Опис | Formula |
|---------|------|---------|
| **Team Fight Efficiency** | Скільки kill на одного death | (Total kills / Total deaths) by 5 |
| **Teamfight Distribution** | Чи була баланс у damage contribution | Std dev of damage % |
| **Farm Efficiency** | Скільки команда взяла ресурсів | Total GPM / avg team GPM |
| **Objective Timing** | Чи хороша timing на основні об'єкти (Roshan, towers) | Events correlation |

---

# 🎯 DETECTION ALGORITHMS

## Algorithm 1: Unconventional Build Detection

```python
class UnconventionalBuildDetector:
    """
    Виявляє дивні/нелогічні組合 предметів
    """
    
    async def detect(self, match_id: int, player_slot: int):
        # 1. Get player items from MongoDB
        items = await get_player_items(match_id, player_slot)
        
        # 2. Get expected items from hero_item_build_computed
        expected = await get_expected_builds(hero_id, role)
        
        # 3. Compare
        # Яка % цього билду зустрічається?
        frequency = expected.find(items) / expected.total
        
        # 4. Flag if rare
        if frequency < 0.05:  # less than 5%
            return {
                "type": "unconventional_build",
                "severity": "warning" | "critical",
                "expected_items": expected.top_3,
                "actual_items": items,
                "frequency": frequency
            }
```

## Algorithm 2: Role Mismatch Detection

```python
class RoleMismatchDetector:
    """
    Виявляє коли герой / роль не матчать
    """
    
    async def detect(self, match_id: int, player_slot: int):
        player = await get_player(match_id, player_slot)
        
        # Expected stats for (hero, role) pair
        expected = await analytics.get_expected_stats(
            hero_id=player.hero_id,
            role=player.role,
            days_back=30
        )
        
        flags = []
        
        # Carry повинен мати 300+ LH за 30 хв
        if player.role == 1 and player.last_hits < 100:
            flags.append({
                "type": "low_farm_carry",
                "severity": "critical",
                "actual": player.last_hits,
                "expected_min": 200
            })
        
        # Support не повинен мати більше 200 LH
        if player.role == 5 and player.last_hits > 250:
            flags.append({
                "type": "support_farming",
                "severity": "warning",
                "actual": player.last_hits,
                "expected_max": 200
            })
        
        return flags
```

## Algorithm 3: Smurf Detection

```python
class SmurfDetector:
    """
    Виявляє smurf accounts (low MMR, high KDA)
    """
    
    async def detect(self, match_id: int, player_slot: int):
        player = await get_player(match_id, player_slot)
        account_stats = await get_account_stats(player.account_id)
        
        # Red flags
        flags = []
        
        # High KDA + Low bracket
        if player.kda > 8.0 and account_stats.avg_rank < 30:
            flags.append({
                "type": "possible_smurf",
                "severity": "info",
                "indicators": ["high_kda", "low_bracket"],
                "kda": player.kda,
                "bracket": account_stats.avg_rank
            })
        
        # Winning streak in new account
        if account_stats.games_played < 20 and account_stats.win_rate > 0.75:
            flags.append({
                "type": "smurf_pattern",
                "severity": "warning",
                "win_rate": account_stats.win_rate,
                "games": account_stats.games_played
            })
        
        return flags
```

## Algorithm 4: Inting Detection

```python
class IntingDetector:
    """
    Виявляє intentional feeding / руіна
    """
    
    async def detect(self, match_id: int, player_slot: int):
        player = await get_player(match_id, player_slot)
        match = await get_match(match_id)
        
        flags = []
        
        # 5+ deaths in first 10 minutes
        deaths_early = sum(1 for e in match.events 
                          if e.type == "death" 
                          and e.player == player_slot 
                          and e.timestamp < 600)
        if deaths_early >= 5:
            flags.append({
                "type": "early_feeding",
                "severity": "critical",
                "deaths": deaths_early,
                "time": "first 10 minutes"
            })
        
        # No items but high deaths
        if len(player.items) == 0 and player.deaths > 10:
            flags.append({
                "type": "feeding_no_items",
                "severity": "critical",
                "deaths": player.deaths,
                "items": len(player.items)
            })
        
        # Dying in impossible positions (enemy fountain)
        for event in match.events:
            if event.type == "death" and event.location == "enemy_fountain":
                flags.append({
                    "type": "obvious_feeding",
                    "severity": "critical",
                    "location": "enemy_fountain"
                })
        
        return flags
```

## Algorithm 5: Game Stomp Detection

```python
class StompDetector:
    """
    Виявляє дисбаланс матчу (один тім явно сильніше)
    """
    
    async def detect(self, match_id: int):
        match = await get_match(match_id)
        
        # Calculate networth at key timestamps
        nw_10min = get_networth_at_timestamp(match, 600)
        nw_20min = get_networth_at_timestamp(match, 1200)
        nw_30min = get_networth_at_timestamp(match, 1800)
        
        radiant_nw = sum(nw_30min["radiant"])
        dire_nw = sum(nw_30min["dire"])
        
        nw_diff = abs(radiant_nw - dire_nw)
        
        if nw_diff > 40000:  # Більш ніж 40k difference
            return {
                "type": "game_stomp",
                "severity": "warning",
                "radiant_nw": radiant_nw,
                "dire_nw": dire_nw,
                "difference": nw_diff,
                "likely_winner": "radiant" if radiant_nw > dire_nw else "dire"
            }
```

---

# 📡 API ENDPOINTS

```
# Player-level assessment
POST /assess/player/{player_id}/match/{match_id}
  Output: {
    player_id,
    match_id,
    quality_score: 0-100,
    flags: [
      {
        type: "role_mismatch" | "unconventional_build" | etc,
        severity: "info" | "warning" | "critical",
        description: "...",
        evidence: {...}
      }
    ]
  }

# Match-level assessment
POST /assess/match/{match_id}
  Output: {
    match_id,
    quality_score: 0-100,
    overall_assessment: "clean" | "suspicious" | "likely_ruined",
    flags: [
      {
        type: "stomp" | "inting" | etc,
        team: "radiant" | "dire",
        severity: "info" | "warning" | "critical"
      }
    ]
  }

# Account-level assessment
GET /assess/account/{account_id}
  Output: {
    account_id,
    smurf_score: 0-100,
    behavior_flags: [...],
    recent_matches: [
      {
        match_id,
        quality_score,
        assessment: "clean" | "suspicious"
      }
    ]
  }

# Admin: Assessment history
GET /admin/assess/history
  Query: ?account_id={id}&min_severity=warning
  Output: { assessments: [...] }
```

---

# 🗄️ DATABASE SCHEMA

## PostgreSQL

```sql
CREATE TABLE match_assessments (
  id SERIAL PRIMARY KEY,
  match_id INT NOT NULL,
  quality_score FLOAT,
  overall_assessment VARCHAR(50),  -- "clean" | "suspicious" | "likely_ruined"
  
  -- Flags
  has_inting BOOLEAN,
  has_stomp BOOLEAN,
  has_smurf BOOLEAN,
  has_unconventional_build BOOLEAN,
  has_role_mismatch BOOLEAN,
  
  -- Metadata
  assessed_at TIMESTAMP DEFAULT now(),
  updated_at TIMESTAMP DEFAULT now(),
  
  UNIQUE(match_id)
);

CREATE TABLE player_assessments (
  id SERIAL PRIMARY KEY,
  match_id INT NOT NULL REFERENCES match_assessments(match_id),
  player_slot INT NOT NULL,
  account_id BIGINT,
  
  quality_score FLOAT,
  role_match FLOAT,        -- 0-1 (how well hero matches role)
  build_logic FLOAT,       -- 0-1 (how logical is build)
  farm_efficiency FLOAT,   -- 0-1
  
  -- Flags
  flags JSONB,             -- array of detected issues
  
  assessed_at TIMESTAMP DEFAULT now(),
  
  UNIQUE(match_id, player_slot)
);

CREATE TABLE account_assessments (
  id SERIAL PRIMARY KEY,
  account_id BIGINT NOT NULL UNIQUE,
  
  -- Smurf indicators
  smurf_score FLOAT,       -- 0-100
  is_likely_smurf BOOLEAN,
  
  -- Behavior
  inting_rate FLOAT,       -- % matches with inting flags
  unconventional_rate FLOAT,
  
  -- Metadata
  last_assessment TIMESTAMP,
  match_history_size INT,  -- how many matches analyzed
  
  UPDATED_AT TIMESTAMP DEFAULT now()
);

CREATE TABLE assessment_flags (
  id SERIAL PRIMARY KEY,
  match_id INT,
  player_slot INT,
  
  flag_type VARCHAR(50),   -- "role_mismatch", "unconventional_build", etc
  severity VARCHAR(20),    -- "info", "warning", "critical"
  description TEXT,
  evidence JSONB,          -- raw data that triggered flag
  
  created_at TIMESTAMP DEFAULT now()
);
```

---

# 🔧 INTEGRATION WITH OTHER SERVICES

## Dependencies

```
Analytics Service (read hero_stats_computed, matchup data)
↓
Data Ingestion Service (read match data)
↓
Quality Assessment Service (compute flags + score)
↓
Frontend (display quality_score, flags)
```

## Event Flow

```
match.ingested event
  ↓
Analytics Service (rebuild stats)
  ↓
[async] Quality Assessment Service
  └─→ POST /assess/match/{match_id}
  └─→ Store results in PostgreSQL
  └─→ Publish event: "match.assessed"
  ↓
Frontend can now display quality indicators
```

---

# 📈 QUALITY SCORE FORMULA

```python
def calculate_quality_score(match_id: int) -> float:
    """
    0-100 score (100 = clean game, 0 = definite ruin/inting)
    """
    
    # Start with 100
    score = 100.0
    
    # Deduct for each flag
    flags = detect_all_flags(match_id)
    
    for flag in flags:
        if flag.severity == "critical":
            score -= 25
        elif flag.severity == "warning":
            score -= 10
        elif flag.severity == "info":
            score -= 2
    
    # Floor at 0
    return max(0, min(100, score))

def assess_quality(score: float) -> str:
    """Convert score to assessment"""
    if score >= 80:
        return "clean"
    elif score >= 50:
        return "suspicious"
    else:
        return "likely_ruined"
```

### Приклади

```
Match 1: 
  - No flags
  - score = 100
  - assessment = "clean"

Match 2:
  - role_mismatch (warning)
  - unconventional_build (warning)
  - score = 100 - 10 - 10 = 80
  - assessment = "clean" (borderline)

Match 3:
  - early_feeding (critical)
  - stomp (warning)
  - possible_smurf (info)
  - score = 100 - 25 - 10 - 2 = 63
  - assessment = "suspicious"

Match 4:
  - obvious_feeding (critical)
  - obvious_feeding (critical)
  - obvious_feeding (critical)
  - score = 100 - 25 - 25 - 25 = 25
  - assessment = "likely_ruined"
```

---

# 📋 ЗАДАЧИ ДЛЯ РЕАЛІЗАЦІЇ

## Phase 2 Tasks

| Task | Опис | Points |
|------|------|--------|
| 6.1 | Bootstrap Quality Assessment Service | 3 |
| 6.2 | UnconventionalBuildDetector implementation | 5 |
| 6.3 | RoleMismatchDetector implementation | 5 |
| 6.4 | SmurfDetector implementation | 5 |
| 6.5 | IntingDetector implementation | 5 |
| 6.6 | StompDetector implementation | 3 |
| 6.7 | Quality score formula + assessment logic | 3 |
| 6.8 | PostgreSQL schema for assessments | 2 |
| 6.9 | API endpoints: /assess/player, /assess/match | 5 |
| 6.10 | Event integration with Analytics | 3 |
| 6.11 | Unit tests for detectors | 5 |
| 6.12 | Smoke test: real match assessment | 3 |

**Total: ~50 story points**

---

# 🎯 CRITERIA FOR SUCCESS (Phase 2)

- ✅ 500+ matches assessed
- ✅ Detection accuracy: 80%+ for obvious inting
- ✅ False positive rate: < 10%
- ✅ All detectors integrated
- ✅ API endpoints working
- ✅ Quality score is useful for filtering/sorting
- ✅ Frontend can display quality indicators

---

# 💡 FUTURE ENHANCEMENTS

| Фіча | Опис | Phase |
|------|------|-------|
| **ML-based Detection** | Train classifier on labeled matches | Phase 3 |
| **Player Behavior Timeline** | Show smurf/behavior progression | Phase 3 |
| **Team Coordination Analysis** | Advanced teamfight patterns | Phase 3 |
| **Predictive Moderation** | Predict likely inting before it happens | Phase 4 |
| **Admin Overrides** | Mark match as clean/dirty manually | Phase 2 |
| **Export Reports** | Detailed PDF/JSON assessment reports | Phase 3 |

---

**Статус:** Готово до інтеграції в архітектуру 🚀
