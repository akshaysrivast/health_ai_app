# metabolic-ai-platform

Production-grade monorepo for an AI-driven metabolic care platform.

## Monorepo Architecture

- `backend-api` (Java Spring Boot): External API gateway and domain orchestration entrypoint.
- `orchestrator` (Python + Temporal + FastAPI): Long-running workflow coordinator.
- `agents/*` (Python + FastAPI): Specialized AI services:
  - `feature-agent`
  - `risk-agent`
  - `diagnosis-agent`
  - `treatment-agent`
  - `report-agent`
- `shared`:
  - `schemas`: Canonical request/response and internal contract models.
  - `events`: Event naming and publishing contracts.
  - `rule-engine`: Rule assets and evaluation conventions.
- `infra`:
  - `docker`: Local container orchestration.
  - `kafka`: Broker/topic setup and defaults.
  - `k8s`: Kubernetes deployment templates.
- `flutter-app`: Mobile client.
- `docs`: Architecture and operational documentation.

## Design Principles

- Clean modular boundaries per service.
- Independent dependency management for each Python service (`requirements.txt`).
- Contract-first communication through shared schemas/events.
- Infrastructure as code for local and cluster environments.

## Quick Start

1. Run API service:
   - `cd backend-api && ./mvnw spring-boot:run`
2. Run orchestrator:
   - `cd orchestrator && pip install -r requirements.txt && uvicorn app.main:app --reload`
3. Run an agent (example):
   - `cd agents/feature-agent && pip install -r requirements.txt && uvicorn app.main:app --reload`
4. Run local infrastructure:
   - `docker compose -f infra/docker/docker-compose.yml up -d`
