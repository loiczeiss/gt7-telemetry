from models.lap import Lap

class LapValidator:
    def __init__(self, min_distance_pct: float = 0.9, min_samples: int = 10):
        self.min_distance_pct = min_distance_pct
        self.min_samples = min_samples

    def validate(self, lap: Lap, expected_distance: float) -> bool:
        # Un tour est valide si :
        # - distance parcourue > 90% du tour complet (approximé par expected_distance)
        # - nombre minimum de samples
        
        if len(lap.samples) < self.min_samples:
            return False
            
        if expected_distance > 0:
            actual_distance = lap.end_distance - lap.start_distance if lap.end_distance else 0
            if actual_distance < expected_distance * self.min_distance_pct:
                return False
                
        return True
