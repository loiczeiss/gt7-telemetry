import struct
import time
from typing import Optional

from collector.crypto import decrypt_gt7_packet
from collector.gt7_offsets import *
from models.telemetry import TelemetrySample


class GT7Decoder:
    @staticmethod
    def decode_plaintext(packet_bytes: bytes) -> TelemetrySample:
        pos_x = struct.unpack_from("<f", packet_bytes, POSITION_X_OFFSET)[0]
        pos_y = struct.unpack_from("<f", packet_bytes, POSITION_Y_OFFSET)[0]

        speed_ms = struct.unpack_from("<f", packet_bytes, SPEED_OFFSET)[0]
        speed_kmh = speed_ms * 3.6

        rpm = struct.unpack_from("<f", packet_bytes, ENGINE_RPM_OFFSET)[0]

        gear_raw = struct.unpack_from("<B", packet_bytes, GEARS_OFFSET)[0]
        gear = gear_raw & 0x0F  # 4 bits bas = rapport actuel

        throttle = struct.unpack_from("<B", packet_bytes, THROTTLE_OFFSET)[0]
        brake = struct.unpack_from("<B", packet_bytes, BRAKE_OFFSET)[0]

        lap_count = struct.unpack_from("<h", packet_bytes, LAP_COUNT_OFFSET)[0]

        best_laptime_raw = struct.unpack_from("<i", packet_bytes, BEST_LAPTIME_OFFSET)[0]
        best_laptime_ms = best_laptime_raw if best_laptime_raw >= 0 else None

        # GT7 n'expose pas de "distance parcourue" ni de "steering" bruts
        # dans ce paquet. On les laisse à 0/None pour l'instant plutôt que
        # de lire un mauvais offset silencieusement — voir notes ci-dessous.
        distance = 0.0
        steering = 0

        return TelemetrySample(
            timestamp=time.time(),
            distance=distance,
            speed=speed_kmh,
            rpm=rpm,
            gear=gear,
            throttle=throttle,
            brake=brake,
            steering=steering,
            position_x=pos_x,
            position_y=pos_y,
            lap_count=lap_count,
            best_laptime_ms=best_laptime_ms,
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