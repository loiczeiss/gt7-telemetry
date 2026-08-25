import os
import pytest
from datetime import datetime
from models.telemetry import TelemetrySample
from session.lap_detector import LapDetector
from session.session_manager import SessionManager
from storage.sqlite import SQLiteStorage

def test_lap_detector_logic():
    detector = LapDetector()
    
    # Premier sample
    events = detector.process_sample(TelemetrySample(
        timestamp=0, lap_count=1, speed=100, rpm=5000,
        gear=3, throttle=255, brake=0, steering=0, 
        position_x=0, position_y=0
    ))
    assert len(events) == 1
    assert events[0].event_type == "LAP_STARTED"
    assert events[0].lap_number == 1
    
    # Même tour
    detector.process_sample(TelemetrySample(
        timestamp=1, lap_count=1, speed=100, rpm=5000,
        gear=3, throttle=255, brake=0, steering=0, 
        position_x=0, position_y=0
    ))
    
    # GT7 signale directement le tour suivant
    events = detector.process_sample(TelemetrySample(
        timestamp=2, lap_count=2, speed=100, rpm=5000,
        gear=3, throttle=255, brake=0, steering=0, 
        position_x=0, position_y=0
    ))
        
    # On attend 2 événements : LAP_COMPLETED tour 1 et LAP_STARTED tour 2
    assert len(events) == 2
    assert events[0].event_type == "LAP_COMPLETED"
    assert events[1].event_type == "LAP_STARTED"
    assert events[1].lap_number == 2

def test_lap_validator_invalid():
    # Test d'un tour interrompu (peu de samples)
    from session.lap_validator import LapValidator
    from models.lap import Lap
    
    validator = LapValidator(min_samples=10)
    lap = Lap(lap_number=1, samples=[TelemetrySample(
            timestamp=0, lap_count=1, speed=100, rpm=5000,
            gear=3, throttle=255, brake=0, steering=0, 
            position_x=0, position_y=0
        )] * 5) # Seulement 5 samples
    
    assert validator.validate(lap, 5000) == False

def test_full_session_flow():
    db_path = "test_session.db"
    if os.path.exists(db_path):
        os.remove(db_path)
        
    storage = SQLiteStorage(f"sqlite:///{db_path}")
    manager = SessionManager(storage, driver_id="Junie")
    
    # Simuler 2 tours avec le compteur GT7.
    for d in range(0, 10):
        manager.process_sample(TelemetrySample(
            timestamp=d / 10, lap_count=1, speed=100, rpm=5000,
            gear=3, throttle=255, brake=0, steering=0, 
            position_x=0, position_y=0
        ))
    
    # GT7 signale le tour suivant.
    manager.process_sample(TelemetrySample(
        timestamp=1.0, lap_count=2, speed=100, rpm=5000,
        gear=3, throttle=255, brake=0, steering=0, 
        position_x=0, position_y=0
    ))

    for d in range(1, 10):
        manager.process_sample(TelemetrySample(
            timestamp=1 + d / 10, lap_count=2, speed=100, rpm=5000,
            gear=3, throttle=255, brake=0, steering=0, 
            position_x=0, position_y=0
        ))
        
    manager.end_session()
    
    # Vérification
    session = storage.get_session(manager.session.id)
    assert session is not None
    assert len(session.laps) == 2
    assert session.laps[0].lap_number == 1
    assert session.laps[1].lap_number == 2
    assert session.end_time is not None
    
    storage.close()
    if os.path.exists(db_path):
        os.remove(db_path)
