from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional
from models.lap import Lap

class Session(BaseModel):
    id: Optional[int] = None
    driver_id: str
    start_time: datetime
    end_time: Optional[datetime] = None
    laps: List[Lap] = []
