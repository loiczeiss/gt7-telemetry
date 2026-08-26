from fastapi import FastAPI

from api.routes import sessions
from api.routes import laps

app = FastAPI(
    title="GT7 Telemetry API",
)

app.include_router(sessions.router)
app.include_router(laps.router)