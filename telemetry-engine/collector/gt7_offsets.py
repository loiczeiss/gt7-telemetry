"""
Offsets pour les paquets telemetry GT7 (type A, paquet complet - 296 octets / 0x128)

Recalculés directement à partir du struct C++ `PacketA`, en respectant
l'alignement naturel des types (float/int32 alignés sur 4 octets,
int16 sur 2 octets, uint8 sur 1 octet). Le total tombe exactement sur
0x128 (296 octets), ce qui confirme le layout.

Rappel : le paquet brut envoyé par la PS5 est chiffré en Salsa20.
Il faut le déchiffrer AVANT de faire le parsing avec ces offsets.
Voir le champ `iv` (0x40) qui sert de vecteur d'initialisation.
"""

import struct

# --- Général ---
MAGIC_OFFSET = 0x00                # int32 - identifie le jeu

# --- Position / mouvement ---
POSITION_X_OFFSET = 0x04           # float (m)
POSITION_Y_OFFSET = 0x08           # float (m)
POSITION_Z_OFFSET = 0x0C           # float (m)

VELOCITY_X_OFFSET = 0x10           # float (m/s)
VELOCITY_Y_OFFSET = 0x14           # float (m/s)
VELOCITY_Z_OFFSET = 0x18           # float (m/s)

ROTATION_PITCH_OFFSET = 0x1C       # float, range -1 -> 1
ROTATION_YAW_OFFSET = 0x20         # float, range -1 -> 1
ROTATION_ROLL_OFFSET = 0x24        # float, range -1 -> 1

ORIENTATION_TO_NORTH_OFFSET = 0x28 # float, 1.0 = nord, 0.0 = sud

ANGULAR_VELOCITY_X_OFFSET = 0x2C   # float (rad/s)
ANGULAR_VELOCITY_Y_OFFSET = 0x30   # float (rad/s)
ANGULAR_VELOCITY_Z_OFFSET = 0x34   # float (rad/s)

BODY_HEIGHT_OFFSET = 0x38          # float

# --- Moteur ---
ENGINE_RPM_OFFSET = 0x3C           # float (PAS 0x2C comme dans la version précédente)

IV_OFFSET = 0x40                   # uint8[4] - IV Salsa20

FUEL_LEVEL_OFFSET = 0x44           # float (litres)
FUEL_CAPACITY_OFFSET = 0x48        # float (litres)

SPEED_OFFSET = 0x4C                # float (m/s -> convertir en km/h : *3.6)

BOOST_OFFSET = 0x50                # float, offset +1 (1.0 = 0x100kPa)

OIL_PRESSURE_OFFSET = 0x54         # float (bar)
WATER_TEMP_OFFSET = 0x58           # float (toujours 85 en pratique)
OIL_TEMP_OFFSET = 0x5C             # float (toujours 110 en pratique)

# --- Pneus ---
TYRE_TEMP_FL_OFFSET = 0x60         # float (°C)
TYRE_TEMP_FR_OFFSET = 0x64
TYRE_TEMP_RL_OFFSET = 0x68
TYRE_TEMP_RR_OFFSET = 0x6C

# --- Course / tour ---
PACKET_ID_OFFSET = 0x70            # int32
LAP_COUNT_OFFSET = 0x74            # int16
TOTAL_LAPS_OFFSET = 0x76           # int16
BEST_LAPTIME_OFFSET = 0x78         # int32 (ms), -1 si non défini
LAST_LAPTIME_OFFSET = 0x7C         # int32 (ms), -1 si non défini
DAY_PROGRESSION_OFFSET = 0x80      # int32 (ms)

RACE_START_POSITION_OFFSET = 0x84  # int16, -1 après le départ
PRE_RACE_NUM_CARS_OFFSET = 0x86    # int16, -1 après le départ

MIN_ALERT_RPM_OFFSET = 0x88        # int16
MAX_ALERT_RPM_OFFSET = 0x8A        # int16
CALC_MAX_SPEED_OFFSET = 0x8C       # int16

FLAGS_OFFSET = 0x8E                # uint16 (bitfield SimulatorFlags)

# --- Pédales / rapport ---
GEARS_OFFSET = 0x90                # uint8 : 4 bits bas = rapport actuel, 4 bits hauts = rapport suggéré
THROTTLE_OFFSET = 0x91             # uint8 (0-255)
BRAKE_OFFSET = 0x92                # uint8 (0-255)
UNKNOWN_BYTE1_OFFSET = 0x93        # padding

# --- Route / suspension ---
ROAD_PLANE_X_OFFSET = 0x94         # float
ROAD_PLANE_Y_OFFSET = 0x98         # float
ROAD_PLANE_Z_OFFSET = 0x9C         # float
ROAD_PLANE_DISTANCE_OFFSET = 0xA0  # float

WHEEL_RPS_FL_OFFSET = 0xA4         # float (rad/s)
WHEEL_RPS_FR_OFFSET = 0xA8
WHEEL_RPS_RL_OFFSET = 0xAC
WHEEL_RPS_RR_OFFSET = 0xB0

TYRE_RADIUS_FL_OFFSET = 0xB4       # float (m)
TYRE_RADIUS_FR_OFFSET = 0xB8
TYRE_RADIUS_RL_OFFSET = 0xBC
TYRE_RADIUS_RR_OFFSET = 0xC0

SUSP_HEIGHT_FL_OFFSET = 0xC4       # float
SUSP_HEIGHT_FR_OFFSET = 0xC8
SUSP_HEIGHT_RL_OFFSET = 0xCC
SUSP_HEIGHT_RR_OFFSET = 0xD0

UNKNOWN_FLOATS_OFFSET = 0xD4       # float[8], inconnu, 32 octets (0xD4 -> 0xF3)

# --- Embrayage / boîte ---
CLUTCH_OFFSET = 0xF4                       # float (0.0 -> 1.0)
CLUTCH_ENGAGEMENT_OFFSET = 0xF8            # float (0.0 -> 1.0)
RPM_FROM_CLUTCH_TO_GEARBOX_OFFSET = 0xFC   # float
TRANSMISSION_TOP_SPEED_OFFSET = 0x100      # float

GEAR_RATIOS_OFFSET = 0x104         # float[8], 32 octets (0x104 -> 0x123)

CAR_CODE_OFFSET = 0x124            # int32

# Taille totale du paquet A (confirmée par le calcul du layout ci-dessus)
GT7_PACKET_SIZE = 0x128  # 296 bytes


def get_current_gear(gears_byte: int) -> int:
    """4 bits bas = rapport actuel."""
    return gears_byte & 0x0F


def get_suggested_gear(gears_byte: int) -> int:
    """4 bits hauts = rapport suggéré."""
    return (gears_byte >> 4) & 0x0F


def parse_packet(data: bytes) -> dict:
    """
    Parse un paquet GT7 DÉCHIFFRÉ (Salsa20 déjà appliqué) de 296 octets.
    Retourne un dict avec les valeurs principales.
    """
    if len(data) < GT7_PACKET_SIZE:
        raise ValueError(f"Paquet trop court : {len(data)} octets (attendu {GT7_PACKET_SIZE})")

    def f(offset):
        return struct.unpack_from('<f', data, offset)[0]

    def i32(offset):
        return struct.unpack_from('<i', data, offset)[0]

    def i16(offset):
        return struct.unpack_from('<h', data, offset)[0]

    def u8(offset):
        return struct.unpack_from('<B', data, offset)[0]

    gears_byte = u8(GEARS_OFFSET)

    return {
        "magic": i32(MAGIC_OFFSET),
        "position": (f(POSITION_X_OFFSET), f(POSITION_Y_OFFSET), f(POSITION_Z_OFFSET)),
        "velocity": (f(VELOCITY_X_OFFSET), f(VELOCITY_Y_OFFSET), f(VELOCITY_Z_OFFSET)),
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
        "current_gear": get_current_gear(gears_byte),
        "suggested_gear": get_suggested_gear(gears_byte),
        "throttle": u8(THROTTLE_OFFSET) / 255.0,
        "brake": u8(BRAKE_OFFSET) / 255.0,
        "clutch": f(CLUTCH_OFFSET),
        "clutch_engagement": f(CLUTCH_ENGAGEMENT_OFFSET),
        "car_code": i32(CAR_CODE_OFFSET),
    }