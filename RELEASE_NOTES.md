# Release Notes – FastAPI Task Queue System

## v0.1.0 – Release (2025-06-25)

### Core Features
- Job submission (`POST /jobs`)
- Job status view (`GET /jobs/{job_id}`)
- Job listing and filtering (`GET /jobs`)
- Job cancellation (`PATCH /jobs/{job_id}/cancel`)
- Async job execution loop with `asyncio`
- Job status auto-updates (`pending → running → completed`)
- Simple priority-based scheduling

### Backend
- PostgreSQL database
- Async SQLAlchemy ORM
- Alembic migration support

### Modifications Made
- Workers are set to 5 for testing purpose and can be changed accordingly

### Dev Tools
- Swagger UI enabled
- Docker Compose for optional PostgreSQL setup

### Not Yet Implemented
- Retry/backoff logic
- Timeout enforcement
- Dependency graph execution
- WebSocket for real-time updates
- Resource constraints (CPU/memory)


Next release will focus on smarter scheduling, retries, and observability.
