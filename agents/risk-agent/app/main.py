from fastapi import FastAPI

app = FastAPI(title="risk-agent", version="0.1.0")


@app.get("/health")
async def health() -> dict[str, str]:
    return {"service": "risk-agent", "status": "ok"}
