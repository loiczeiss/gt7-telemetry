from pydantic import BaseModel, Field

class Lap(BaseModel):
    id: Optional[int] = None
    session_id: Optional[int] = None
    lap_number: int

    lap_time: Optional[float] = None
    valid: bool = True

    samples_count: int = 0

    samples: List[TelemetrySample] = Field(default_factory=list)