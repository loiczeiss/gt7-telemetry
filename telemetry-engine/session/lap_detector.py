from models.telemetry import TelemetrySample
from models.events import LapEvent
from typing import Optional, List


class LapDetector:
    """
    Détecteur de tours basé sur le compteur de tours natif GT7 (lap_count).
    Plus fiable qu'une heuristique de franchissement de ligne basée sur la
    distance : GT7 gère lui-même la détection de ligne d'arrivée et
    incrémente lap_count en conséquence, donc on se contente de suivre
    ce changement.
    Produit des LapEvent pour la couche supérieure.
    """
    def __init__(self):
        self.last_sample: Optional[TelemetrySample] = None
        self.is_initialized = False

    def process_sample(self, sample: TelemetrySample) -> List[LapEvent]:
        events = []

        # 1. Initialisation au premier sample
        if not self.is_initialized:
            self.is_initialized = True
            self.last_sample = sample
            events.append(LapEvent(
                event_type="LAP_STARTED",
                lap_number=sample.lap_count,
                timestamp=sample.timestamp,
                distance=sample.distance
            ))
            return events

        # 2. Gestion des anomalies et ordres temporels
        if sample.timestamp <= self.last_sample.timestamp:
            # On ignore les paquets en retard ou doublons
            return events

        # 3. Détection de changement de tour via lap_count
        # GT7 met lap_count à -1 (ou une valeur négative) hors course /
        # avant le départ : on ignore ces transitions.
        lap_increased = (
            sample.lap_count > self.last_sample.lap_count
            and self.last_sample.lap_count >= 0
        )

        if lap_increased:
            # Événement : Tour complété (le tour qui vient de se terminer)
            events.append(LapEvent(
                event_type="LAP_COMPLETED",
                lap_number=self.last_sample.lap_count,
                timestamp=sample.timestamp,
                distance=self.last_sample.distance
            ))

            # Événement : Nouveau tour démarré
            events.append(LapEvent(
                event_type="LAP_STARTED",
                lap_number=sample.lap_count,
                timestamp=sample.timestamp,
                distance=sample.distance
            ))

        # 4. Cas reset / retour aux stands / nouvelle session :
        # lap_count qui redescend à 1 (ou à une valeur <= à l'actuelle)
        # après avoir été plus haut. On le signale comme un nouveau départ
        # plutôt que de le traiter comme une anomalie silencieuse.
        elif sample.lap_count < self.last_sample.lap_count:
            events.append(LapEvent(
                event_type="LAP_STARTED",
                lap_number=sample.lap_count,
                timestamp=sample.timestamp,
                distance=sample.distance
            ))

        self.last_sample = sample
        return events