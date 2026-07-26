from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional
from models.telemetry import TelemetrySample

class Lap(BaseModel):
    id: Optional[int] = None
    session_id: Optional[int] = None
    lap_number: int
    start_distance: float = 0.0
    end_distance: Optional[float] = None
    lap_time: Optional[float] = None
    valid: bool = True
    samples_count: int = 0
    samples: List[TelemetrySample] = []
