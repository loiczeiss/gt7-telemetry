from pydantic import BaseModel
from datetime import datetime

class TelemetrySample(BaseModel):
    timestamp: float
    distance: float
    speed: float
    rpm: float
    gear: int
    throttle: int
    brake: int
    steering: int
    position_x: float
    position_y: float
