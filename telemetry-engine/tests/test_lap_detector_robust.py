import pytest
import config
from models.telemetry import TelemetrySample
from session.lap_detector import LapDetector

def create_sample(timestamp: float, distance: float, speed: float = 100.0) -> TelemetrySample:
    return TelemetrySample(
        timestamp=timestamp,
        distance=distance,
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
    events = detector.process_sample(create_sample(1.0, 0.0))
    assert len(events) == 1
    assert events[0].event_type == "LAP_STARTED"
    assert events[0].lap_number == 1

    # 2. Progression normale
    events = detector.process_sample(create_sample(2.0, 1000.0))
    assert len(events) == 0
    
    events = detector.process_sample(create_sample(3.0, 4800.0))
    assert len(events) == 0
    
    # 3. Passage ligne (4900 -> 10)
    # TRACK_LENGTH = 5000.0, FINISH_LINE_START = 4750.0, FINISH_LINE_END = 250.0
    events = detector.process_sample(create_sample(4.0, 10.0))
    assert len(events) == 2
    assert events[0].event_type == "LAP_COMPLETED"
    assert events[0].lap_number == 1
    assert events[0].distance == 4800.0
    
    assert events[1].event_type == "LAP_STARTED"
    assert events[1].lap_number == 2
    assert events[1].distance == 10.0

def test_lap_detector_reverse_gear():
    detector = LapDetector()
    detector.process_sample(create_sample(1.0, 2000.0))
    
    # Marche arrière : distance diminue mais on n'est pas dans la zone de départ
    events = detector.process_sample(create_sample(2.0, 1900.0))
    assert len(events) == 0
    
    events = detector.process_sample(create_sample(3.0, 1800.0))
    assert len(events) == 0

def test_lap_detector_zero_speed():
    detector = LapDetector()
    # On arrive en fin de tour
    detector.process_sample(create_sample(1.0, 4900.0))
    
    # Passage ligne mais vitesse nulle (ex: reset ou bug)
    events = detector.process_sample(create_sample(2.0, 10.0, speed=0.0))
    assert len(events) == 0

def test_lap_detector_full_session():
    detector = LapDetector()
    all_events = []
    
    # Start
    all_events.extend(detector.process_sample(create_sample(0.0, 0.0)))
    
    # 10 tours
    for i in range(1, 11):
        # Mi-tour
        detector.process_sample(create_sample(i * 100.0 + 50.0, 2500.0))
        # Fin de tour
        detector.process_sample(create_sample(i * 100.0 + 99.0, 4950.0))
        # Passage ligne
        events = detector.process_sample(create_sample((i+1) * 100.0, 50.0))
        all_events.extend(events)
        
    # On s'attend à 1 LAP_STARTED initial + 10 (LAP_COMPLETED + LAP_STARTED)
    # Total = 1 + 20 = 21 événements
    assert len(all_events) == 21
    
    completed_laps = [e for e in all_events if e.event_type == "LAP_COMPLETED"]
    assert len(completed_laps) == 10
    for i, lap in enumerate(completed_laps):
        assert lap.lap_number == i + 1
