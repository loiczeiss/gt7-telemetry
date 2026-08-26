from fastapi import APIRouter

from storage.sqlite import SQLiteStorage

router = APIRouter(
    prefix="/api/laps",
    tags=["Laps"],
)

storage = SQLiteStorage()

@router.get("/{lap_id}")
def get_lap(lap_id: int):
    return storage.get_lap(lap_id)

@router.get("/")
def get_laps():
    return storage.get_laps()