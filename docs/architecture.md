# Architecture Overview

The platform is organized as a polyglot microservice monorepo:

- Spring Boot backend API for north-south traffic.
- Temporal-based Python orchestrator for workflow state and retries.
- FastAPI-based AI agents for modular inference and decision stages.
- Shared contracts for schemas, events, and deterministic rule definitions.
- Infrastructure definitions for local Docker and Kubernetes deployment.
