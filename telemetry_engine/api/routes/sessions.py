from fastapi import APIRouter

from storage.sqlite import SQLiteStorage

router = APIRouter(
    prefix="/api/sessions",
    tags=["Sessions"],
)

storage = SQLiteStorage()


@router.get("/")
def get_sessions():
    return storage.get_sessions()

@router.get("/{session_id}")
def get_session(session_id: int):
    return storage.get_session(session_id)