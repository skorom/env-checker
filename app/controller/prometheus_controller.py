from app.config.application_config import PROMETHEUS_METRICS_ENDPOINT
from fastapi import FastAPI
from prometheus_fastapi_instrumentator import Instrumentator

app = FastAPI(
    title="MS environment checker",
    summary="Checks if the running environment is ready by scanning ports, exposing metrics and logging.",
    version="1.0.0-SNAPSHOT",
    contact={
        "name": "Szilárd Korom",
        "email": "korom.szilard@inf.elte.hu",
    },
)
"""The FastAPI instance"""

Instrumentator(excluded_handlers=[PROMETHEUS_METRICS_ENDPOINT]).instrument(app).expose(
    app, endpoint=PROMETHEUS_METRICS_ENDPOINT
)


@app.get("/")
async def root():
    """The root landing point of the web service.

    Returns:
        json: A status:up JSON just to return with something meaningful.
    """
    return {"status": "up"}
