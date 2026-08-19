from models.lap import Lap


class LapValidator:
    """
    Valide qu'un tour enregistré est "réel" et pas un artefact (reset,
    retour aux stands, changement de session, tour tronqué en début
    d'enregistrement, etc.).

    Note : GT7 n'expose pas de distance parcourue dans le paquet
    telemetry (PacketA) — cette info n'est donc plus disponible de
    façon fiable. On valide à la place sur la durée du tour (basée sur
    les timestamps réels des samples) et le nombre de samples.
    """
    def __init__(self, min_duration_pct: float = 0.5, min_samples: int = 10):
        # min_duration_pct : le tour doit durer au moins cette fraction
        # du temps de référence attendu (ex: meilleur tour connu, ou
        # temps de référence du circuit) pour écarter les tours tronqués.
        self.min_duration_pct = min_duration_pct
        self.min_samples = min_samples

    @staticmethod
    def expected_duration_from_lap(lap: Lap) -> float:
        """
        Dérive la durée de référence à partir de best_laptime_ms (fourni
        par GT7, ms). GT7 renvoie -1 tant qu'aucun tour valide n'a été
        enregistré dans la session (ex: tout premier tour) -> on tombe
        alors sur best_laptime_ms=None côté decoder, et on renvoie 0.0
        ici pour signaler "pas de référence disponible".
        """
        if not lap.samples:
            return 0.0
        best_ms = lap.samples[-1].best_laptime_ms
        if best_ms is None:
            return 0.0
        return best_ms / 1000.0

    def validate(self, lap: Lap, expected_duration: float = None) -> bool:
        if len(lap.samples) < self.min_samples:
            return False

        if expected_duration is None:
            expected_duration = self.expected_duration_from_lap(lap)

        if expected_duration > 0:
            if not lap.samples:
                return False
            actual_duration = lap.samples[-1].timestamp - lap.samples[0].timestamp
            if actual_duration < expected_duration * self.min_duration_pct:
                return False

        return True