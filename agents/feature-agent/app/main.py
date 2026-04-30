from fastapi import FastAPI

from app.core.path_setup import configure_import_path

configure_import_path()

from app.api.routes import router
from app.core.logging_config import configure_logging, get_logger

configure_logging()
logger = get_logger(__name__)

app = FastAPI(title="feature-agent", version="1.0.0")
app.include_router(router)


@app.on_event("startup")
async def on_startup() -> None:
    logger.info("feature-agent starting up")
