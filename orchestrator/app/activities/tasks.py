from temporalio import activity


@activity.defn
async def compute_risk_score(patient_id: str) -> dict[str, str]:
    return {"patient_id": patient_id, "risk_score": "low"}
