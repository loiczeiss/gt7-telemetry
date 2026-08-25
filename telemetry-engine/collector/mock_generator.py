import random
import time
from datetime import datetime
from models.telemetry import TelemetrySample

class MockTelemetryGenerator:
    def __init__(self, driver_id="JuniorDev", track="Spa", car="Porsche 911 GT3 RS"):
        self.driver_id = driver_id
        self.track = track
        self.car = car
        self.lap_count = 1

    def generate_sample(self) -> TelemetrySample:
        return TelemetrySample(
            timestamp=time.time(),
            packet_id=0,
            speed=random.uniform(100.0, 250.0),
            rpm=random.uniform(5000, 9000),
            gear=random.randint(3, 6),
            suggested_gear=0,
            throttle=random.randint(0, 255),
            brake=random.randint(0, 255),
            clutch=0.0,
            boost=0.0,
            fuel_level=0.0,
            fuel_capacity=0.0,
            oil_pressure=0.0,
            water_temp=0.0,
            oil_temp=0.0,
            tyre_temp_fl=0.0,
            tyre_temp_fr=0.0,
            tyre_temp_rl=0.0,
            tyre_temp_rr=0.0,
            lap_count=self.lap_count,
            total_laps=0,
            wheel_base=0.0,
            surface_type="",
            car_category="",
            car_code=0,
            steering=random.randint(-100, 100),
            position_x=random.uniform(-1000, 1000),
            position_y=random.uniform(-1000, 1000),
            position_z=0.0,
            velocity_x=0.0,
            velocity_y=0.0,
            velocity_z=0.0,
        )

    def generate(self, count=100):
        for _ in range(count):
            yield self.generate_sample()
