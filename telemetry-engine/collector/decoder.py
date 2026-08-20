import struct
import time
from typing import Optional

from collector.crypto import decrypt_gt7_packet
from collector.gt7_offsets import *
from models.telemetry import TelemetrySample


class GT7Decoder:
    @staticmethod
    def _read_str4(packet_bytes: bytes, offset: int) -> str:
        """Lit une chaîne ASCII de 4 octets max, null-terminée (surfaceType, carCategory)."""
        raw = packet_bytes[offset:offset + 4]
        return raw.split(b"\x00", 1)[0].decode("ascii", errors="replace")

    @staticmethod
    def decode_plaintext(packet_bytes: bytes) -> TelemetrySample:
        f = lambda off: struct.unpack_from("<f", packet_bytes, off)[0]
        i32 = lambda off: struct.unpack_from("<i", packet_bytes, off)[0]
        i16 = lambda off: struct.unpack_from("<h", packet_bytes, off)[0]
        u8 = lambda off: struct.unpack_from("<B", packet_bytes, off)[0]

        # --- Position / mouvement ---
        pos_x, pos_y, pos_z = f(POSITION_X_OFFSET), f(POSITION_Y_OFFSET), f(POSITION_Z_OFFSET)
        vel_x, vel_y, vel_z = f(VELOCITY_X_OFFSET), f(VELOCITY_Y_OFFSET), f(VELOCITY_Z_OFFSET)
        speed_kmh = f(SPEED_OFFSET) * 3.6

        # --- Moteur / transmission ---
        rpm = f(ENGINE_RPM_OFFSET)
        gear_raw = u8(GEARS_OFFSET)
        gear = gear_raw & 0x0F  # 4 bits bas = rapport actuel
        suggested_gear = (gear_raw >> 4) & 0x0F  # 4 bits hauts = rapport suggéré

        # Normalisés en 0.0 -> 1.0 (brut GT7 : 0-255)
        throttle = u8(THROTTLE_OFFSET) / 255.0
        brake = u8(BRAKE_OFFSET) / 255.0

        clutch = f(CLUTCH_OFFSET)
        boost = f(BOOST_OFFSET)

        # --- Fluides / températures ---
        fuel_level = f(FUEL_LEVEL_OFFSET)
        fuel_capacity = f(FUEL_CAPACITY_OFFSET)
        oil_pressure = f(OIL_PRESSURE_OFFSET)
        water_temp = f(WATER_TEMP_OFFSET)
        oil_temp = f(OIL_TEMP_OFFSET)
        tyre_temp_fl = f(TYRE_TEMP_FL_OFFSET)
        tyre_temp_fr = f(TYRE_TEMP_FR_OFFSET)
        tyre_temp_rl = f(TYRE_TEMP_RL_OFFSET)
        tyre_temp_rr = f(TYRE_TEMP_RR_OFFSET)

        # --- Course / tour ---
        packet_id = i32(PACKET_ID_OFFSET)
        lap_count = i16(LAP_COUNT_OFFSET)
        total_laps = i16(TOTAL_LAPS_OFFSET)

        best_laptime_raw = i32(BEST_LAPTIME_OFFSET)
        best_laptime_ms = best_laptime_raw if best_laptime_raw >= 0 else None

        last_laptime_raw = i32(LAST_LAPTIME_OFFSET)
        last_laptime_ms = last_laptime_raw if last_laptime_raw >= 0 else None

        # Convention -1 = non défini supposée par analogie avec best/last
        # laptime, à confirmer si tu observes une valeur aberrante en jeu.
        current_lap_raw = i32(PACKETC_CURRENT_LAP_OFFSET)
        current_lap_ms = current_lap_raw if current_lap_raw >= 0 else None

        # --- Direction / châssis (PacketC) ---
        steer_l = f(PACKETC_WHEEL_STEERING_ANGLE_LEFT_OFFSET)
        steer_r = f(PACKETC_WHEEL_STEERING_ANGLE_RIGHT_OFFSET)
        steering = (steer_l + steer_r) / 2.0

        wheel_base = f(PACKETC_WHEEL_BASE_OFFSET)
        surface_type = GT7Decoder._read_str4(packet_bytes, PACKETC_SURFACE_TYPE_OFFSET)
        car_category = GT7Decoder._read_str4(packet_bytes, PACKETC_CAR_CATEGORY_OFFSET)

        car_code = i32(CAR_CODE_OFFSET)

        return TelemetrySample(
            timestamp=time.time(),
            packet_id=packet_id,
            position_x=pos_x,
            position_y=pos_y,
            position_z=pos_z,
            velocity_x=vel_x,
            velocity_y=vel_y,
            velocity_z=vel_z,
            speed=speed_kmh,
            rpm=rpm,
            gear=gear,
            suggested_gear=suggested_gear,
            throttle=throttle,
            brake=brake,
            clutch=clutch,
            boost=boost,
            fuel_level=fuel_level,
            fuel_capacity=fuel_capacity,
            oil_pressure=oil_pressure,
            water_temp=water_temp,
            oil_temp=oil_temp,
            tyre_temp_fl=tyre_temp_fl,
            tyre_temp_fr=tyre_temp_fr,
            tyre_temp_rl=tyre_temp_rl,
            tyre_temp_rr=tyre_temp_rr,
            lap_count=lap_count,
            total_laps=total_laps,
            best_laptime_ms=best_laptime_ms,
            last_laptime_ms=last_laptime_ms,
            current_lap_ms=current_lap_ms,
            steering=steering,
            wheel_base=wheel_base,
            surface_type=surface_type,
            car_category=car_category,
            car_code=car_code,
        )

    @staticmethod
    def decode(packet_bytes: bytes, encrypted: bool = True) -> Optional[TelemetrySample]:
        """
        Décode un paquet GT7. En production les paquets sont chiffrés Salsa20.
        Les tests plaintext passent encrypted=False.
        """
        if encrypted:
            packet_bytes = decrypt_gt7_packet(packet_bytes)
            if packet_bytes is None:
                return None
        return GT7Decoder.decode_plaintext(packet_bytes)