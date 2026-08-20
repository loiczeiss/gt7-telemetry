from typing import Optional

from pydantic import BaseModel


class TelemetrySample(BaseModel):
    timestamp: float
    packet_id: int

    # --- Position / mouvement ---
    position_x: float
    position_y: float
    position_z: float
    velocity_x: float
    velocity_y: float
    velocity_z: float
    speed: float  # km/h

    # --- Moteur / transmission ---
    rpm: float
    gear: int
    suggested_gear: int
    throttle: float  # normalisé 0.0 -> 1.0 (brut GT7 : 0-255)
    brake: float  # normalisé 0.0 -> 1.0 (brut GT7 : 0-255)
    clutch: float  # 0.0 -> 1.0
    boost: float

    # --- Fluides / températures ---
    fuel_level: float
    fuel_capacity: float
    oil_pressure: float
    water_temp: float
    oil_temp: float
    tyre_temp_fl: float
    tyre_temp_fr: float
    tyre_temp_rl: float
    tyre_temp_rr: float

    # --- Course / tour ---
    lap_count: int  # Fourni directement par GT7 (LAP_COUNT_OFFSET), fiable
    total_laps: int
    best_laptime_ms: Optional[int] = None  # -1 côté GT7 si non défini -> None ici
    last_laptime_ms: Optional[int] = None  # idem
    current_lap_ms: Optional[int] = None  # PacketC, convention -1 supposée

    # --- Direction / châssis (PacketC) ---
    steering: float  # radians, moyenne gauche/droite
    wheel_base: float  # mètres
    surface_type: str  # T=tarmac, C=curb, D=dirt/grass
    car_category: str  # ex: "GR3"

    car_code: int

