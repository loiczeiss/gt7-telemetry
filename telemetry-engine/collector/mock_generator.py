import random
import time
from datetime import datetime
from models.telemetry import TelemetrySample

class MockTelemetryGenerator:
    def __init__(self, driver_id="JuniorDev", track="Spa", car="Porsche 911 GT3 RS"):
        self.driver_id = driver_id
        self.track = track
        self.car = car
        self.distance = 0.0

    def generate_sample(self) -> TelemetrySample:
        self.distance += random.uniform(5.0, 10.0)
        # Simulation passage de ligne après 5000m
        if self.distance > 5000.0:
            self.distance = self.distance % 5000.0
        
        return TelemetrySample(
            timestamp=time.time(),
            distance=self.distance,
            speed=random.uniform(100.0, 250.0),
            rpm=random.uniform(5000, 9000),
            gear=random.randint(3, 6),
            throttle=random.randint(0, 255),
            brake=random.randint(0, 255),
            steering=random.randint(-100, 100),
            position_x=random.uniform(-1000, 1000),
            position_y=random.uniform(-1000, 1000)
        )

    def generate(self, count=100):
        for _ in range(count):
            yield self.generate_sample()
