from fastapi import FastAPI

app = FastAPI(title="feature-agent", version="0.1.0")


@app.get("/health")
async def health() -> dict[str, str]:
    return {"service": "feature-agent", "status": "ok"}
