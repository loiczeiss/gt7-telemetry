from pydantic import BaseModel
from typing import Optional, Any

class LapEvent(BaseModel):
    event_type: str  # LAP_STARTED, LAP_COMPLETED, LAP_INVALID
    lap_number: int
    timestamp: float
    metadata: Optional[dict[str, Any]] = None
