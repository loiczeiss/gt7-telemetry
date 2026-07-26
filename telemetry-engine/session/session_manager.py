from datetime import datetime
from typing import Optional, List
from models.telemetry import TelemetrySample
from models.lap import Lap
from models.session import Session
from session.lap_detector import LapDetector
from session.lap_validator import LapValidator
from storage.sqlite import SQLiteStorage

class SessionManager:
    def __init__(self, storage: SQLiteStorage, driver_id: str, track: str, car: str):
        self.storage = storage
        self.session = Session(
            driver_id=driver_id,
            track=track,
            car=car,
            start_time=datetime.now()
        )
        # On sauvegarde la session en DB pour avoir un ID
        self.session.id = self.storage.save_session(self.session)
        
        self.current_lap: Optional[Lap] = None
        self.lap_detector = LapDetector()
        self.lap_validator = LapValidator()
        self.max_lap_distance = 0.0 # Utilisé pour la validation

    def process_sample(self, sample: TelemetrySample):
        events = self.lap_detector.process_sample(sample)
        
        for event in events:
            if event.event_type == "LAP_STARTED":
                self._on_lap_started(event.lap_number, event.distance)
            elif event.event_type == "LAP_COMPLETED":
                self._on_lap_completed(event.distance)

        if self.current_lap:
            self.current_lap.samples.append(sample)
            self.current_lap.samples_count += 1
            if sample.distance > self.max_lap_distance:
                self.max_lap_distance = sample.distance

    def _on_lap_started(self, lap_number: int, start_distance: float):
        self.current_lap = Lap(
            session_id=self.session.id,
            lap_number=lap_number,
            start_distance=start_distance,
            samples=[]
        )

    def _on_lap_completed(self, end_distance: float):
        if self.current_lap:
            self.current_lap.end_distance = end_distance
            # Calcul du temps au tour (simplifié avec le premier et dernier sample)
            if len(self.current_lap.samples) >= 2:
                self.current_lap.lap_time = self.current_lap.samples[-1].timestamp - self.current_lap.samples[0].timestamp
            
            # Validation
            # On utilise max_lap_distance comme approximation de la longueur du tour
            self.current_lap.valid = self.lap_validator.validate(self.current_lap, self.max_lap_distance)
            
            # Sauvegarde du tour
            self.storage.save_lap(self.current_lap)
            self.session.laps.append(self.current_lap)
            
    def end_session(self):
        if self.lap_detector.last_sample:
            self._on_lap_completed(self.lap_detector.last_sample.distance)
        self.session.end_time = datetime.now()
        self.storage.update_session(self.session)
