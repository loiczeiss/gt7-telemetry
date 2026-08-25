"""
Offsets pour les paquets telemetry GT7 — format PacketC (340 octets / 0x154)

PacketC = PacketA + PacketB + champs spécifiques (surface, tour en cours,
angle de braquage, empattement, catégorie voiture).

Rappel : le paquet brut est chiffré en Salsa20, à déchiffrer AVANT parsing.
Voir le champ `iv` (0x40) qui sert de vecteur d'initialisation.
"""

import struct

# ============================================================
# PacketA (0x00 -> 0x128, 296 octets) — inchangé
# ============================================================
MAGIC_OFFSET = 0x00

POSITION_X_OFFSET = 0x04
POSITION_Y_OFFSET = 0x08
POSITION_Z_OFFSET = 0x0C

VELOCITY_X_OFFSET = 0x10
VELOCITY_Y_OFFSET = 0x14
VELOCITY_Z_OFFSET = 0x18

ROTATION_PITCH_OFFSET = 0x1C
ROTATION_YAW_OFFSET = 0x20
ROTATION_ROLL_OFFSET = 0x24

ORIENTATION_TO_NORTH_OFFSET = 0x28

ANGULAR_VELOCITY_X_OFFSET = 0x2C
ANGULAR_VELOCITY_Y_OFFSET = 0x30
ANGULAR_VELOCITY_Z_OFFSET = 0x34

BODY_HEIGHT_OFFSET = 0x38
ENGINE_RPM_OFFSET = 0x3C

IV_OFFSET = 0x40

FUEL_LEVEL_OFFSET = 0x44
FUEL_CAPACITY_OFFSET = 0x48
SPEED_OFFSET = 0x4C
BOOST_OFFSET = 0x50
OIL_PRESSURE_OFFSET = 0x54
WATER_TEMP_OFFSET = 0x58
OIL_TEMP_OFFSET = 0x5C

TYRE_TEMP_FL_OFFSET = 0x60
TYRE_TEMP_FR_OFFSET = 0x64
TYRE_TEMP_RL_OFFSET = 0x68
TYRE_TEMP_RR_OFFSET = 0x6C

PACKET_ID_OFFSET = 0x70
LAP_COUNT_OFFSET = 0x74
TOTAL_LAPS_OFFSET = 0x76
BEST_LAPTIME_OFFSET = 0x78
LAST_LAPTIME_OFFSET = 0x7C
DAY_PROGRESSION_OFFSET = 0x80

RACE_START_POSITION_OFFSET = 0x84
PRE_RACE_NUM_CARS_OFFSET = 0x86

MIN_ALERT_RPM_OFFSET = 0x88
MAX_ALERT_RPM_OFFSET = 0x8A
CALC_MAX_SPEED_OFFSET = 0x8C

FLAGS_OFFSET = 0x8E

GEARS_OFFSET = 0x90
THROTTLE_OFFSET = 0x91
BRAKE_OFFSET = 0x92
UNKNOWN_BYTE1_OFFSET = 0x93

ROAD_PLANE_X_OFFSET = 0x94
ROAD_PLANE_Y_OFFSET = 0x98
ROAD_PLANE_Z_OFFSET = 0x9C
ROAD_PLANE_DISTANCE_OFFSET = 0xA0

WHEEL_RPS_FL_OFFSET = 0xA4
WHEEL_RPS_FR_OFFSET = 0xA8
WHEEL_RPS_RL_OFFSET = 0xAC
WHEEL_RPS_RR_OFFSET = 0xB0

TYRE_RADIUS_FL_OFFSET = 0xB4
TYRE_RADIUS_FR_OFFSET = 0xB8
TYRE_RADIUS_RL_OFFSET = 0xBC
TYRE_RADIUS_RR_OFFSET = 0xC0

SUSP_HEIGHT_FL_OFFSET = 0xC4
SUSP_HEIGHT_FR_OFFSET = 0xC8
SUSP_HEIGHT_RL_OFFSET = 0xCC
SUSP_HEIGHT_RR_OFFSET = 0xD0

UNKNOWN_FLOATS_OFFSET = 0xD4  # float[8], 32 octets

CLUTCH_OFFSET = 0xF4
CLUTCH_ENGAGEMENT_OFFSET = 0xF8
RPM_FROM_CLUTCH_TO_GEARBOX_OFFSET = 0xFC
TRANSMISSION_TOP_SPEED_OFFSET = 0x100

GEAR_RATIOS_OFFSET = 0x104  # float[8], 32 octets

CAR_CODE_OFFSET = 0x124

# ============================================================
# PacketB (0x128 -> 0x13C, +20 octets)
# ============================================================
PACKETB_WHEEL_ROTATION_OFFSET = 0x128              # float (rad)
PACKETB_STEERING_ANGULAR_VELOCITY_OFFSET = 0x12C   # float (rad/s)
PACKETB_SWAY_OFFSET = 0x130                        # float, accélération axe X
PACKETB_HEAVE_OFFSET = 0x134                       # float, accélération axe Y
PACKETB_SURGE_OFFSET = 0x138                        # float, accélération axe Z

# ============================================================
# PacketC (0x13C -> 0x154, +24 octets)
# ============================================================
PACKETC_SURFACE_TYPE_OFFSET = 0x13C                # char[4] : T=tarmac, C=curb, D=dirt, G=grass, S=Sand, s=snow,
PACKETC_CURRENT_LAP_OFFSET = 0x140                 # int32 (ms)
PACKETC_WHEEL_STEERING_ANGLE_LEFT_OFFSET = 0x144   # float (rad)
PACKETC_WHEEL_STEERING_ANGLE_RIGHT_OFFSET = 0x148  # float (rad)
PACKETC_WHEEL_BASE_OFFSET = 0x14C                  # float (m)
PACKETC_CAR_CATEGORY_OFFSET = 0x150                # char[4], ex: "GR3\0"

GT7_PACKETC_SIZE = 0x154  # 340 octets — taille totale attendue

# Backwards-compatible names used by the original decoder tests.
GT7_PACKET_SIZE = GT7_PACKETC_SIZE
RPM_OFFSET = ENGINE_RPM_OFFSET
GEAR_OFFSET = GEARS_OFFSET


def get_current_gear(gears_byte: int) -> int:
    return gears_byte & 0x0F


def get_suggested_gear(gears_byte: int) -> int:
    return (gears_byte >> 4) & 0x0F


def parse_packet_c(data: bytes) -> dict:
    """
    Parse un paquet GT7 DÉCHIFFRÉ (Salsa20 déjà appliqué) au format PacketC
    (340 octets). Inclut tous les champs hérités de PacketA et PacketB.
    """
    if len(data) < GT7_PACKETC_SIZE:
        raise ValueError(f"Paquet trop court : {len(data)} octets (attendu {GT7_PACKETC_SIZE})")

    def f(offset):
        return struct.unpack_from('<f', data, offset)[0]

    def i32(offset):
        return struct.unpack_from('<i', data, offset)[0]

    def i16(offset):
        return struct.unpack_from('<h', data, offset)[0]

    def u8(offset):
        return struct.unpack_from('<B', data, offset)[0]

    def s4(offset):
        return data[offset:offset + 4].split(b'\x00', 1)[0].decode('ascii', errors='replace')

    gears_byte = u8(GEARS_OFFSET)

    return {
        # --- PacketA ---
        "magic": i32(MAGIC_OFFSET),
        "iv": list(data[IV_OFFSET:IV_OFFSET + 4]),
        "position": (f(POSITION_X_OFFSET), f(POSITION_Y_OFFSET), f(POSITION_Z_OFFSET)),
        "velocity": (f(VELOCITY_X_OFFSET), f(VELOCITY_Y_OFFSET), f(VELOCITY_Z_OFFSET)),
        "rotation": (f(ROTATION_PITCH_OFFSET), f(ROTATION_YAW_OFFSET), f(ROTATION_ROLL_OFFSET)),
        "orientation_to_north": f(ORIENTATION_TO_NORTH_OFFSET),
        "angular_velocity": (f(ANGULAR_VELOCITY_X_OFFSET), f(ANGULAR_VELOCITY_Y_OFFSET), f(ANGULAR_VELOCITY_Z_OFFSET)),
        "body_height": f(BODY_HEIGHT_OFFSET),
        "speed_kmh": f(SPEED_OFFSET) * 3.6,
        "engine_rpm": f(ENGINE_RPM_OFFSET),
        "fuel_level": f(FUEL_LEVEL_OFFSET),
        "fuel_capacity": f(FUEL_CAPACITY_OFFSET),
        "oil_pressure": f(OIL_PRESSURE_OFFSET),
        "water_temp": f(WATER_TEMP_OFFSET),
        "oil_temp": f(OIL_TEMP_OFFSET),
        "tyre_temp": {
            "FL": f(TYRE_TEMP_FL_OFFSET),
            "FR": f(TYRE_TEMP_FR_OFFSET),
            "RL": f(TYRE_TEMP_RL_OFFSET),
            "RR": f(TYRE_TEMP_RR_OFFSET),
        },
        "packet_id": i32(PACKET_ID_OFFSET),
        "lap_count": i16(LAP_COUNT_OFFSET),
        "total_laps": i16(TOTAL_LAPS_OFFSET),
        "best_laptime_ms": i32(BEST_LAPTIME_OFFSET),
        "last_laptime_ms": i32(LAST_LAPTIME_OFFSET),
        "day_progression": f(DAY_PROGRESSION_OFFSET),
        "race_start_position": i16(RACE_START_POSITION_OFFSET),
        "pre_race_num_cars": i16(PRE_RACE_NUM_CARS_OFFSET),
        "min_alert_rpm": i16(MIN_ALERT_RPM_OFFSET),
        "max_alert_rpm": i16(MAX_ALERT_RPM_OFFSET),
        "calc_max_speed": f(CALC_MAX_SPEED_OFFSET),
        "flags": i16(FLAGS_OFFSET),
        "current_gear": get_current_gear(gears_byte),
        "suggested_gear": get_suggested_gear(gears_byte),
        "throttle": u8(THROTTLE_OFFSET) / 255.0,
        "brake": u8(BRAKE_OFFSET) / 255.0,
        "unknown_byte1": u8(UNKNOWN_BYTE1_OFFSET),
        "road_plane": (f(ROAD_PLANE_X_OFFSET), f(ROAD_PLANE_Y_OFFSET), f(ROAD_PLANE_Z_OFFSET)),
        "road_plane_distance": f(ROAD_PLANE_DISTANCE_OFFSET),
        "wheel_rps": {
            "FL": f(WHEEL_RPS_FL_OFFSET),
            "FR": f(WHEEL_RPS_FR_OFFSET),
            "RL": f(WHEEL_RPS_RL_OFFSET),
            "RR": f(WHEEL_RPS_RR_OFFSET),
        },
        "tyre_radius": {
            "FL": f(TYRE_RADIUS_FL_OFFSET),
            "FR": f(TYRE_RADIUS_FR_OFFSET),
            "RL": f(TYRE_RADIUS_RL_OFFSET),
            "RR": f(TYRE_RADIUS_RR_OFFSET),
        },
        "susp_height": {
            "FL": f(SUSP_HEIGHT_FL_OFFSET),
            "FR": f(SUSP_HEIGHT_FR_OFFSET),
            "RL": f(SUSP_HEIGHT_RL_OFFSET),
            "RR": f(SUSP_HEIGHT_RR_OFFSET),
        },
        "unknown_floats": list(struct.unpack_from('<8f', data, UNKNOWN_FLOATS_OFFSET)),
        "clutch": f(CLUTCH_OFFSET),
        "clutch_engagement": f(CLUTCH_ENGAGEMENT_OFFSET),
        "rpm_from_clutch_to_gearbox": f(RPM_FROM_CLUTCH_TO_GEARBOX_OFFSET),
        "transmission_top_speed": f(TRANSMISSION_TOP_SPEED_OFFSET),
        "gear_ratios": list(struct.unpack_from('<8f', data, GEAR_RATIOS_OFFSET)),
        "car_code": i32(CAR_CODE_OFFSET),

        # --- PacketB ---
        "wheel_rotation": f(PACKETB_WHEEL_ROTATION_OFFSET),
        "steering_angular_velocity": f(PACKETB_STEERING_ANGULAR_VELOCITY_OFFSET),
        "sway": f(PACKETB_SWAY_OFFSET),
        "heave": f(PACKETB_HEAVE_OFFSET),
        "surge": f(PACKETB_SURGE_OFFSET),

        # --- PacketC ---
        "surface_type": s4(PACKETC_SURFACE_TYPE_OFFSET),
        "current_lap_ms": i32(PACKETC_CURRENT_LAP_OFFSET),
        "wheel_steering_angle": (
            f(PACKETC_WHEEL_STEERING_ANGLE_LEFT_OFFSET),
            f(PACKETC_WHEEL_STEERING_ANGLE_RIGHT_OFFSET),
        ),
        "wheel_base": f(PACKETC_WHEEL_BASE_OFFSET),
        "car_category": s4(PACKETC_CAR_CATEGORY_OFFSET),
    }