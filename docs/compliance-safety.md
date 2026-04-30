# Compliance and Safety Guardrails

This platform applies baseline safeguards aligned with healthcare compliance readiness:

## Input validation

- Backend validates `PatientContext` structure with schema and size constraints.
- Domain-level checks enforce:
  - required `patient_id`
  - lab name/value validity
  - numeric lab safety ranges

## Rate limiting

- API gateway enforces per-IP per-endpoint request limits.
- Default limit is `60 requests/minute` (configurable via env vars).

## LLM output validation

- LLM responses must be strict JSON with required fields.
- Report content is validated for:
  - schema and length constraints
  - blocked unsafe clinical language patterns

## Safe rule evaluation

- Rule engine uses explicit operator mapping only.
- No `eval()`, `exec()`, or dynamic code execution in rule processing.

## Operational readiness

- Structured logs include `trace_id` and `patient_id` for auditability.
- Controls are configurable via environment variables for staged deployments.
