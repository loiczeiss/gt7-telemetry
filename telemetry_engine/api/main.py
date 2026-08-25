from fastapi import FastAPI

from api.routes import sessions

app = FastAPI(
    title="GT7 Telemetry API",
)

app.include_router(sessions.router)