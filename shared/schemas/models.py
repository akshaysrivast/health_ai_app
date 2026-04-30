from pydantic import BaseModel


class PatientContext(BaseModel):
    patient_id: str
    age: int
    biomarkers: dict[str, float]


class RiskAssessment(BaseModel):
    patient_id: str
    level: str
    score: float
