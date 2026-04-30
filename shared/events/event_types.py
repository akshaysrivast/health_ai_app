from enum import StrEnum


class EventType(StrEnum):
    PATIENT_INGESTED = "patient.ingested"
    RISK_COMPUTED = "risk.computed"
    DIAGNOSIS_GENERATED = "diagnosis.generated"
    TREATMENT_PLANNED = "treatment.planned"
    REPORT_COMPILED = "report.compiled"
