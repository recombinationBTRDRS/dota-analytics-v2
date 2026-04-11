# Dota 2 Analytics - Ingestion Service

## Overview

HTTP service that fetches, parses, validates, and stores Dota 2 matches from OpenDota API.

Port: **8001**

## Quick Start

### Using Docker Compose (Recommended)

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f ingestion

# Stop all services
docker-compose down
```

### Manual Setup (Local Development)

```bash
# Install dependencies
poetry install

# Set up environment
cp .env.example .env
# Edit .env with your local settings

# Start services locally
poetry run python -m uvicorn services.ingestion.app.main:app --reload --port 8001
```

## Health Checks

```bash
# Health check
curl http://localhost:8001/health

# Readiness check
curl http://localhost:8001/ready

# Debug config (only in DEBUG=true)
curl http://localhost:8001/config
```

## Configuration

See `.env.example` for all available settings.

### Key Settings

| Setting | Default | Description |
|---------|---------|-------------|
| `SERVICE_PORT` | 8001 | Service port |
| `DEBUG` | true | Debug mode |
| `OPENDOTA_TIMEOUT` | 30 | Request timeout (seconds) |
| `MONGODB_URL` | mongodb://localhost:27017 | MongoDB connection |
| `REDIS_URL` | redis://localhost:6379 | Redis connection |

## API Documentation

Once running, visit: http://localhost:8001/docs

## Testing

```bash
# Run all tests
poetry run pytest services/ingestion/tests/ -v

# Run with coverage
poetry run pytest services/ingestion/tests/ --cov=services.ingestion

# Run specific test
poetry run pytest services/ingestion/tests/test_config.py -v
```

## Development

### Code Quality Tools

```bash
# Format code
poetry run black services/ingestion/

# Lint code
poetry run ruff check services/ingestion/

# Type checking
poetry run mypy services/ingestion/
```

### Directory Structure
services/ingestion/
├── app/
│   ├── init.py
│   ├── main.py           # FastAPI app
│   ├── config.py         # Settings
│   ├── routers/          # API endpoints
│   └── db/               # Database layer
├── tests/
│   ├── test_smoke.py
│   ├── test_config.py
│   └── test_docker.py
└── README.md

## Docker Details

### Build Image

```bash
docker build -t dota2-ingestion:latest .
```

### Run Container

```bash
docker run -p 8001:8001 \
  -e DEBUG=true \
  -e MONGODB_URL=mongodb://mongodb:27017 \
  -e REDIS_URL=redis://redis:6379 \
  --network dota2_network \
  dota2-ingestion:latest
```

### Health Check

Container includes health check:

```bash
docker ps  # Check health status
# Should show "healthy" after 10-20 seconds
```