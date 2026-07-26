from models.telemetry import TelemetrySample
from models.events import LapEvent
from typing import Optional, List
import config

class LapDetector:
    """
    Détecteur de tours robuste basé sur la distance, la vitesse et les zones de ligne d'arrivée.
    Produit des LapEvent pour la couche supérieure.
    """
    def __init__(self):
        self.last_sample: Optional[TelemetrySample] = None
        self.current_lap_number = 0
        self.is_initialized = False

    def process_sample(self, sample: TelemetrySample) -> List[LapEvent]:
        events = []

        # 1. Initialisation au premier sample
        if not self.is_initialized:
            self.current_lap_number = 1
            self.is_initialized = True
            self.last_sample = sample
            events.append(LapEvent(
                event_type="LAP_STARTED",
                lap_number=self.current_lap_number,
                timestamp=sample.timestamp,
                distance=sample.distance
            ))
            return events

        # 2. Gestion des anomalies et ordres temporels
        if sample.timestamp <= self.last_sample.timestamp:
            # On ignore les paquets en retard ou doublons
            return events

        # 3. Détection passage ligne d'arrivée
        # Condition : On passe de la fin du circuit (>95%) au début (<5%)
        # ET on a une vitesse minimale pour éviter les détections à l'arrêt/reset
        
        in_finish_zone = self.last_sample.distance > (config.TRACK_LENGTH * config.FINISH_LINE_START_PERCENTAGE)
        in_start_zone = sample.distance < (config.TRACK_LENGTH * config.FINISH_LINE_END_PERCENTAGE)
        
        # Cas spécifique GT7 : La distance peut aussi faire un saut direct (ex: 4990 -> 10)
        # On vérifie si la distance a diminué de manière significative tout en étant dans les zones
        
        has_crossed_line = (self.last_sample.distance > sample.distance) and in_finish_zone and in_start_zone
        
        if has_crossed_line and sample.speed > config.MIN_SPEED_FOR_LAP:
            # Événement : Tour complété
            events.append(LapEvent(
                event_type="LAP_COMPLETED",
                lap_number=self.current_lap_number,
                timestamp=self.last_sample.timestamp,
                distance=self.last_sample.distance
            ))
            
            # Événement : Nouveau tour démarré
            self.current_lap_number += 1
            events.append(LapEvent(
                event_type="LAP_STARTED",
                lap_number=self.current_lap_number,
                timestamp=sample.timestamp,
                distance=sample.distance
            ))

        self.last_sample = sample
        return events
