import pytest
from datetime import datetime
import os
from models.lap import Lap
from models.session import Session
from models.telemetry import TelemetrySample
from storage.sqlite import SQLiteStorage
from collector.mock_generator import MockTelemetryGenerator

def test_pipeline_integration():
    # 1. Setup
    db_path = "test_telemetry.db"
    if os.path.exists(db_path):
        os.remove(db_path)
    
    storage = SQLiteStorage(db_url=f"sqlite:///{db_path}")
    generator = MockTelemetryGenerator()
    
    # 2. Générer des données simulées
    samples = [generator.generate_sample() for _ in range(10)]
    
    # 3. Créer un tour
    lap = Lap(
        session_id=1,
        lap_number=1,
        start_time=datetime.now(),
        samples=samples
    )
    
    # 4. Sauvegarder le tour
    lap_id = storage.save_lap(lap)
    assert lap_id is not None
    
    # 5. Recharger le tour
    # On crée d'abord une session pour que get_session fonctionne (ou on teste directement save_lap)
    session_id = storage.save_session(Session(driver_id="Test", track="Test", car="Test", start_time=datetime.now()))
    lap.session_id = session_id
    storage.save_lap(lap)
    
    session = storage.get_session(session_id)
    assert session is not None
    assert len(session.laps) > 0
    loaded_lap = session.laps[0]
    
    # 6. Vérifications
    assert len(loaded_lap.samples) == 10
    assert loaded_lap.samples[0].speed == samples[0].speed
    
    # Cleanup
    storage.close()
    if os.path.exists(db_path):
        os.remove(db_path)
