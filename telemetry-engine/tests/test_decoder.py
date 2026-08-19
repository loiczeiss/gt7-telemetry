import struct
import pytest
from collector.decoder import GT7Decoder
from collector.gt7_offsets import *
from models.telemetry import TelemetrySample

def test_decoder_basic():
    # Création d'un faux paquet binaire GT7 (296 bytes) rempli de zéros
    packet = bytearray(GT7_PACKET_SIZE)
    
    # Injection de valeurs connues aux offsets
    # Position X = 123.45
    struct.pack_into('<f', packet, POSITION_X_OFFSET, 123.45)
    # Speed = 50.0 m/s (soit 180 km/h)
    struct.pack_into('<f', packet, SPEED_OFFSET, 50.0)
    # RPM = 7500.0
    struct.pack_into('<f', packet, RPM_OFFSET, 7500.0)
    # Gear = 4
    struct.pack_into('<B', packet, GEAR_OFFSET, 4)
    # Throttle = 200, Brake = 50
    struct.pack_into('<B', packet, THROTTLE_OFFSET, 200)
    struct.pack_into('<B', packet, BRAKE_OFFSET, 50)
    # Distance = 1000.0
    struct.pack_into('<f', packet, DISTANCE_OFFSET, 1000.0)
    
    # Décodage
    sample = GT7Decoder.decode(bytes(packet), encrypted=False)
    
    # Vérifications
    assert isinstance(sample, TelemetrySample)
    assert pytest.approx(sample.position_x) == 123.45
    assert pytest.approx(sample.speed) == 180.0
    assert pytest.approx(sample.rpm) == 7500.0
    assert sample.gear == 4
    assert sample.throttle == 200
    assert sample.brake == 50
    assert pytest.approx(sample.distance) == 1000.0
