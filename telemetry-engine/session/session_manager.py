from datetime import datetime
from typing import Optional

from models.telemetry import TelemetrySample
from models.lap import Lap
from models.session import Session
from session.lap_detector import LapDetector
from session.lap_validator import LapValidator
from storage.sqlite import SQLiteStorage
from collector.car_catalog import get_car_info, format_car_name


class SessionManager:
    """
    Orchestrates a GT7 driving session.

    Responsibilities:
    - Own the current Session.
    - Receive telemetry samples.
    - Ask LapDetector for lap events.
    - Create and complete Lap objects.
    - Calculate lap duration from timestamps.
    - Validate completed laps.
    - Persist sessions and laps.

    Lap boundaries are determined exclusively by GT7's lap_count.
    No distance-based lap detection is performed.
    """

    def __init__(
            self,
            storage: SQLiteStorage,
            driver_id: str,
    ):
        self.storage = storage

        # Session lifecycle
        self.session = Session(
            driver_id=driver_id,
            start_time=datetime.now(),
        )

        # Save immediately so the session gets its DB ID.
        self.session.id = self.storage.save_session(self.session)

        # Current lap being recorded.
        self.current_lap: Optional[Lap] = None

        # Components responsible for their own concerns.
        self.lap_detector = LapDetector()
        self.lap_validator = LapValidator()

        self.is_active = True

    def process_sample(self, sample: TelemetrySample) -> None:
        """
        Process one telemetry sample.

        The sample is first given to LapDetector so that we know whether
        GT7 changed lap_count.

        Important:
        The sample that contains the new lap_count belongs to the NEW lap.
        """

        if not self.is_active:
            return

        events = self.lap_detector.process_sample(sample)

        if self.session.car_code is None and sample.car_code:
            car_info = get_car_info(sample.car_code)
            self.session.car_code = sample.car_code
            self.session.car_name = format_car_name(sample.car_code)
            self.session.manufacturer_id = (
                car_info.manufacturer_id if car_info else None
            )
            self.storage.update_session(self.session)

        for event in events:

            if event.event_type == "LAP_COMPLETED":
                self._on_lap_completed(event)

            elif event.event_type == "LAP_STARTED":
                self._on_lap_started(event)

        # The sample belongs to the lap indicated by its own lap_count.
        if self.current_lap is not None:
            self.current_lap.samples.append(sample)
            self.current_lap.samples_count += 1

    def _on_lap_started(self, event) -> None:
        """
        Start recording a new lap.

        The lap number comes directly from GT7's lap_count.
        """

        # Defensive check: don't create a lap for an invalid lap number.
        if event.lap_number < 0:
            return

        self.current_lap = Lap(
            session_id=self.session.id,
            lap_number=event.lap_number,
        )

    def _on_lap_completed(self, event) -> None:
        """
        Complete the currently recorded lap.

        The event timestamp represents the telemetry sample where GT7
        detected the transition to the next lap.
        """

        if self.current_lap is None:
            return

        # Make sure the event corresponds to the lap we're recording.
        if self.current_lap.lap_number != event.lap_number:
            return

        # Calculate lap duration from telemetry timestamps.
        if self.current_lap.samples:
            start_timestamp = self.current_lap.samples[0].timestamp

            self.current_lap.lap_time = (
                    event.timestamp - start_timestamp
            )

        # Validate the completed lap.
        self.current_lap.valid = (
            self.lap_validator.validate(self.current_lap)
        )

        # Persist the completed lap.
        self.storage.save_lap(self.current_lap)

        self.session.laps.append(self.current_lap)

        # There is no active lap until LAP_STARTED arrives.
        self.current_lap = None

    def end_session(self) -> None:
        """
        End the current session.

        If a lap is still being recorded, it is finalized using the
        timestamp of the last valid telemetry sample.
        """

        if not self.is_active:
            return

        # Finish an incomplete/current lap.
        if self.current_lap is not None:
            last_sample = self.lap_detector.last_sample

            if last_sample is not None:
                self._complete_current_lap_at(
                    last_sample.timestamp
                )

        self.session.end_time = datetime.now()

        self.storage.update_session(self.session)

        self.is_active = False

    def _complete_current_lap_at(self, timestamp: float) -> None:
        """
        Complete the current lap at a given timestamp.

        Used when the session ends before GT7 emits a LAP_COMPLETED event.
        """

        if self.current_lap is None:
            return

        if self.current_lap.samples:
            start_timestamp = self.current_lap.samples[0].timestamp

            self.current_lap.lap_time = (
                    timestamp - start_timestamp
            )

        self.current_lap.valid = (
            self.lap_validator.validate(self.current_lap)
        )

        self.storage.save_lap(self.current_lap)

        self.session.laps.append(self.current_lap)

        self.current_lap = None