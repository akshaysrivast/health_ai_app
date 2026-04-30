from fastapi import FastAPI

app = FastAPI(title="orchestrator", version="0.1.0")


@app.get("/health")
async def health() -> dict[str, str]:
    return {"service": "orchestrator", "status": "ok"}
