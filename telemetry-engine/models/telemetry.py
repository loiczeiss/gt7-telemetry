from typing import Optional

from pydantic import BaseModel, Field


class TelemetrySample(BaseModel):
    timestamp: float = 0.0
    packet_id: int = 0

    # --- Position / mouvement ---
    position_x: float = 0.0
    position_y: float = 0.0
    position_z: float = 0.0
    velocity_x: float = 0.0
    velocity_y: float = 0.0
    velocity_z: float = 0.0
    speed: float = 0.0  # km/h

    # --- Moteur / transmission ---
    rpm: float = 0.0
    gear: int = 0
    suggested_gear: int = 0
    throttle: float = 0.0  # normalisé 0.0 -> 1.0 (brut GT7 : 0-255)
    brake: float = 0.0  # normalisé 0.0 -> 1.0 (brut GT7 : 0-255)
    clutch: float = 0.0  # 0.0 -> 1.0
    boost: float = 0.0

    # --- Fluides / températures ---
    fuel_level: float = 0.0
    fuel_capacity: float = 0.0
    oil_pressure: float = 0.0
    water_temp: float = 0.0
    oil_temp: float = 0.0
    tyre_temp_fl: float = 0.0
    tyre_temp_fr: float = 0.0
    tyre_temp_rl: float = 0.0
    tyre_temp_rr: float = 0.0

    # --- Course / tour ---
    lap_count: int = 1  # Fourni directement par GT7 (LAP_COUNT_OFFSET), fiable
    total_laps: int = 0
    best_laptime_ms: Optional[int] = None  # -1 côté GT7 si non défini -> None ici
    last_laptime_ms: Optional[int] = None  # idem
    current_lap_ms: Optional[int] = None  # PacketC, convention -1 supposée

    # --- Direction / châssis (PacketC) ---
    steering: float = 0.0  # radians, moyenne gauche/droite
    wheel_base: float = 0.0  # mètres
    surface_type: str = ""  # T=tarmac, C=curb, D=dirt/grass
    car_category: str = ""  # ex: "GR3"

    car_code: int = 0

    # --- Complete PacketA / PacketB telemetry ---
    magic: int = 0
    iv: list[int] = Field(default_factory=list)
    rotation_pitch: float = 0.0
    rotation_yaw: float = 0.0
    rotation_roll: float = 0.0
    orientation_to_north: float = 0.0
    angular_velocity_x: float = 0.0
    angular_velocity_y: float = 0.0
    angular_velocity_z: float = 0.0
    body_height: float = 0.0
    day_progression: float = 0.0
    race_start_position: int = 0
    pre_race_num_cars: int = 0
    min_alert_rpm: int = 0
    max_alert_rpm: int = 0
    calc_max_speed: float = 0.0
    flags: int = 0
    unknown_byte1: int = 0
    road_plane_x: float = 0.0
    road_plane_y: float = 0.0
    road_plane_z: float = 0.0
    road_plane_distance: float = 0.0
    wheel_rps_fl: float = 0.0
    wheel_rps_fr: float = 0.0
    wheel_rps_rl: float = 0.0
    wheel_rps_rr: float = 0.0
    tyre_radius_fl: float = 0.0
    tyre_radius_fr: float = 0.0
    tyre_radius_rl: float = 0.0
    tyre_radius_rr: float = 0.0
    susp_height_fl: float = 0.0
    susp_height_fr: float = 0.0
    susp_height_rl: float = 0.0
    susp_height_rr: float = 0.0
    unknown_floats: list[float] = Field(default_factory=list)
    clutch_engagement: float = 0.0
    rpm_from_clutch_to_gearbox: float = 0.0
    transmission_top_speed: float = 0.0
    gear_ratios: list[float] = Field(default_factory=list)

    # --- PacketB ---
    wheel_rotation: float = 0.0
    steering_angular_velocity: float = 0.0
    sway: float = 0.0
    heave: float = 0.0
    surge: float = 0.0

