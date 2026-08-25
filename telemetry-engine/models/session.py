from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional
from models.lap import Lap

class Session(BaseModel):
    id: Optional[int] = None
    driver_id: str
    car_code: Optional[int] = None
    car_name: Optional[str] = None
    manufacturer_id: Optional[int] = None
    start_time: datetime
    end_time: Optional[datetime] = None
    laps: List[Lap] = []
