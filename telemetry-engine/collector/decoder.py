import struct
import time
from models.telemetry import TelemetrySample
from collector.gt7_offsets import *

class GT7Decoder:
    @staticmethod
    def decode(packet_bytes: bytes) -> TelemetrySample:
        """
        Décode les bytes UDP de GT7 en un objet TelemetrySample.
        Format attendu : Little Endian.
        """
        # Utilisation de struct.unpack_from pour lire aux offsets définis
        
        # Position XYZ (Floats)
        pos_x = struct.unpack_from('<f', packet_bytes, POSITION_X_OFFSET)[0]
        pos_y = struct.unpack_from('<f', packet_bytes, POSITION_Y_OFFSET)[0]
        pos_z = struct.unpack_from('<f', packet_bytes, POSITION_Z_OFFSET)[0]
        
        # Vitesse (m/s -> km/h)
        speed_ms = struct.unpack_from('<f', packet_bytes, SPEED_OFFSET)[0]
        speed_kmh = speed_ms * 3.6
        
        # RPM
        rpm = struct.unpack_from('<f', packet_bytes, RPM_OFFSET)[0]
        
        # Gear (Le quartet de poids faible contient le rapport, 0-15)
        # Mais souvent stocké comme un simple byte à cet offset
        gear_raw = struct.unpack_from('<B', packet_bytes, GEAR_OFFSET)[0]
        gear = gear_raw & 0x0F
        
        # Throttle / Brake (0-255)
        throttle = struct.unpack_from('<B', packet_bytes, THROTTLE_OFFSET)[0]
        brake = struct.unpack_from('<B', packet_bytes, BRAKE_OFFSET)[0]
        
        # Distance (Float)
        distance = struct.unpack_from('<f', packet_bytes, DISTANCE_OFFSET)[0]
        
        # Steering (Souvent pas directement présent ou nécessite calcul, on met 0 par défaut pour l'instant)
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
            position_z=pos_z
        )
