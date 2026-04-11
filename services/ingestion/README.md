# Dota 2 Analytics - Ingestion Service

HTTP service that fetches, parses, validates, and stores Dota 2 matches from OpenDota API.

## Features

- ✅ Async API with FastAPI
- ✅ MongoDB for match storage
- ✅ Redis for caching
- ✅ Structured JSON logging
- ✅ Repository Pattern for data access
- ✅ Request/Response validation with Pydantic
- ✅ OpenAPI/Swagger documentation
- ✅ Health checks and readiness probes
- ✅ CORS and rate limiting
- ✅ Proper error handling
- ✅ Dependency injection

## Quick Start

### Using Docker Compose

```bash
cd ../..
docker-compose up -d ingestion
```

### Manual Setup

```bash
# Install dependencies
poetry install

# Create .env
cp ../../.env.example .env

# Start service
poetry run python -m uvicorn app.main:app --reload --port 8001
```

## Health Checks

```bash
# Health check
curl http://localhost:8001/health

# Readiness check
curl http://localhost:8001/ready

# Config (debug)
curl http://localhost:8001/config
```

## API Endpoints

### Ingest Match

```bash
curl -X POST http://localhost:8001/api/v1/ingest/opendota \
  -H "Content-Type: application/json" \
  -d '{"match_id": 7123456789}'

# Response:
{
  "match_id": 7123456789,
  "status": "pending",
  "message": "Match queued for ingestion",
  "request_id": "uuid-123"
}
```

### Get Ingestion Status

```bash
curl http://localhost:8001/api/v1/ingest/status/7123456789

# Response:
{
  "match_id": 7123456789,
  "status": "ingested",
  "attempt": 1,
  "error": null
}
```

## API Documentation

Visit: http://localhost:8001/docs

## Testing

```bash
# All tests
poetry run pytest tests/ -v

# Specific test file
poetry run pytest tests/test_endpoints.py -v

# With coverage
poetry run pytest tests/ --cov=app -v
```

## Development

### Code Quality

```bash
# Format
poetry run black app/ tests/

# Lint
poetry run ruff check app/ tests/

# Type check
poetry run mypy app/
```

### Directory Structure
app/
├── init.py
├── main.py              # FastAPI application
├── config.py            # Settings
├── schemas.py           # Pydantic models
├── routers/             # API endpoints
│   ├── init.py
│   └── ingest.py
├── db/                  # Data access layer
│   ├── init.py
│   ├── mongodb.py       # MongoDB client
│   ├── repositories.py  # Repository Pattern
│   └── dependencies.py  # Dependency injection
└── logging_config.py    # Structured logging
tests/
├── init.py
├── test_smoke.py        # Smoke tests
├── test_config.py       # Config tests
├── test_logging.py      # Logging tests
├── test_repositories.py # Repository tests
├── test_endpoints.py    # Endpoint tests
├── test_docker.py       # Docker tests
└── test_lifespan.py     # Lifespan tests

## Configuration

See `.env.example` for all available settings.

## Logging

Structured JSON logging to stdout:

```json
{
  "timestamp": "2025-04-08T10:30:45.123Z",
  "level": "INFO",
  "name": "app.routers.ingest",
  "message": "ingest_opendota_requested",
  "match_id": 7123456789,
  "request_id": "uuid-123"
}
```

## Performance

- Async/await for non-blocking I/O
- Connection pooling for MongoDB
- Redis caching for frequently accessed data
- Rate limiting to prevent abuse
- Request logging for monitoring

## Error Handling

- Validation errors (422)
- Not found errors (404)
- Server errors (500)
- All errors include request_id for tracking