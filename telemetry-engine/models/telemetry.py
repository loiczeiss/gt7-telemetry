from typing import Optional

from pydantic import BaseModel


class TelemetrySample(BaseModel):
    timestamp: float
    speed: float
    rpm: float
    gear: int
    throttle: int
    brake: int
    position_x: float
    position_y: float
    lap_count: int  # Fourni directement par GT7 (LAP_COUNT_OFFSET), fiable
    best_laptime_ms: Optional[int] = None  # -1 côté GT7 si non défini -> None ici

    # Pas de champ brut correspondant dans le paquet GT7 PacketA.
    # distance : à calculer toi-même (intégration de la vitesse) si besoin.
    # steering : non exposé par ce paquet UDP.
    distance: Optional[float] = None
    steering: Optional[int] = None