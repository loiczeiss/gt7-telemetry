import pytest
import config
from models.telemetry import TelemetrySample
from session.lap_detector import LapDetector

def create_sample(timestamp: float, lap_count: int, speed: float = 100.0) -> TelemetrySample:
    return TelemetrySample(
        timestamp=timestamp,
        lap_count=lap_count,
        speed=speed,
        rpm=5000,
        gear=3,
        throttle=0,
        brake=0,
        steering=0,
        position_x=0.0,
        position_y=0.0
    )

def test_lap_detector_normal_flow():
    detector = LapDetector()
    
    # 1. Premier sample -> LAP_STARTED
    events = detector.process_sample(create_sample(1.0, 1))
    assert len(events) == 1
    assert events[0].event_type == "LAP_STARTED"
    assert events[0].lap_number == 1

    # 2. Progression normale
    events = detector.process_sample(create_sample(2.0, 1))
    assert len(events) == 0
    
    events = detector.process_sample(create_sample(3.0, 1))
    assert len(events) == 0
    
    # 3. GT7 reports the next lap directly.
    events = detector.process_sample(create_sample(4.0, 2))
    assert len(events) == 2
    assert events[0].event_type == "LAP_COMPLETED"
    assert events[0].lap_number == 1
    
    assert events[1].event_type == "LAP_STARTED"
    assert events[1].lap_number == 2

def test_lap_detector_reverse_gear():
    detector = LapDetector()
    detector.process_sample(create_sample(1.0, 1))
    
    # Un compteur inchangé ne déclenche pas de transition.
    events = detector.process_sample(create_sample(2.0, 1))
    assert len(events) == 0
    
    events = detector.process_sample(create_sample(3.0, 1))
    assert len(events) == 0

def test_lap_detector_lap_count_is_independent_of_speed():
    detector = LapDetector()
    # GT7 reste l'autorité même si la vitesse est nulle.
    detector.process_sample(create_sample(1.0, 1))
    
    # Le changement de lap_count suffit à déclarer la transition.
    events = detector.process_sample(create_sample(2.0, 2, speed=0.0))
    assert [event.event_type for event in events] == [
        "LAP_COMPLETED",
        "LAP_STARTED",
    ]

def test_lap_detector_full_session():
    detector = LapDetector()
    all_events = []
    
    # Start
    all_events.extend(detector.process_sample(create_sample(0.0, 1)))
    
    # 10 tours
    for i in range(1, 11):
        detector.process_sample(create_sample(i * 100.0 + 50.0, i))
        events = detector.process_sample(create_sample((i+1) * 100.0, i + 1))
        all_events.extend(events)
        
    # On s'attend à 1 LAP_STARTED initial + 10 (LAP_COMPLETED + LAP_STARTED)
    # Total = 1 + 20 = 21 événements
    assert len(all_events) == 21
    
    completed_laps = [e for e in all_events if e.event_type == "LAP_COMPLETED"]
    assert len(completed_laps) == 10
    for i, lap in enumerate(completed_laps):
        assert lap.lap_number == i + 1
