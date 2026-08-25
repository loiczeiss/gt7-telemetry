from typing import Optional

from models.telemetry import TelemetrySample
from models.events import LapEvent


class LapDetector:
    """
    Detects laps exclusively from GT7's native lap_count.

    GT7 is the source of truth for lap boundaries.

    Responsibilities:
    - Detect the first valid lap.
    - Detect normal lap transitions.
    - Ignore duplicate/out-of-order telemetry.
    - Ignore negative lap_count values.
    - Detect lap-count resets/anomalies without inventing laps.

    No distance or position-based lap detection is performed.
    """

    def __init__(self):
        self.last_sample: Optional[TelemetrySample] = None
        self.is_initialized = False

    def process_sample(self, sample: TelemetrySample) -> list[LapEvent]:
        events: list[LapEvent] = []

        # ---------------------------------------------------------
        # 1. Ignore telemetry where GT7 does not provide a valid lap.
        #
        # Example:
        #   lap_count = -1
        #
        # This can happen before/after a race or outside a valid
        # racing state.
        #
        # IMPORTANT:
        # We do NOT update last_sample here.
        # ---------------------------------------------------------
        if sample.lap_count < 0:
            return events

        # ---------------------------------------------------------
        # 2. First valid sample.
        #
        # We don't have a previous lap to compare against, so this
        # establishes the initial lap.
        # ---------------------------------------------------------
        if not self.is_initialized:
            self.is_initialized = True
            self.last_sample = sample

            events.append(
                LapEvent(
                    event_type="LAP_STARTED",
                    lap_number=sample.lap_count,
                    timestamp=sample.timestamp,
                )
            )

            return events

        # At this point last_sample should exist because the detector
        # has been initialized.
        if self.last_sample is None:
            self.last_sample = sample
            return events

        # ---------------------------------------------------------
        # 3. Ignore old / duplicate packets.
        #
        # UDP does not guarantee ordering, so telemetry can arrive
        # out of order.
        # ---------------------------------------------------------
        if sample.timestamp <= self.last_sample.timestamp:
            return events

        previous_lap = self.last_sample.lap_count
        current_lap = sample.lap_count

        # ---------------------------------------------------------
        # 4. Normal lap transition.
        #
        # Example:
        #
        #   previous_lap = 3
        #   current_lap  = 4
        #
        # Therefore:
        #
        #   LAP_COMPLETED 3
        #   LAP_STARTED   4
        #
        # The current sample belongs to lap 4.
        # ---------------------------------------------------------
        if current_lap == previous_lap + 1:
            events.append(
                LapEvent(
                    event_type="LAP_COMPLETED",
                    lap_number=previous_lap,
                    timestamp=sample.timestamp,
                )
            )

            events.append(
                LapEvent(
                    event_type="LAP_STARTED",
                    lap_number=current_lap,
                    timestamp=sample.timestamp,
                )
            )

        # ---------------------------------------------------------
        # 5. Same lap.
        #
        # Nothing happened.
        #
        # Example:
        #   3 -> 3
        # ---------------------------------------------------------
        elif current_lap == previous_lap:
            pass

        # ---------------------------------------------------------
        # 6. Lap count increased by more than one.
        #
        # Example:
        #   3 -> 5
        #
        # We missed at least one lap boundary.
        #
        # We should NOT invent events for laps we didn't observe.
        # The caller can decide how to handle this anomaly.
        # ---------------------------------------------------------
        elif current_lap > previous_lap:
            # We observed a discontinuity in lap_count.
            #
            # Do not generate fake LAP_COMPLETED events.
            # Start the newly observed lap only if the caller wants
            # to recover from the discontinuity.
            events.append(
                LapEvent(
                    event_type="LAP_STARTED",
                    lap_number=current_lap,
                    timestamp=sample.timestamp,
                )
            )

        # ---------------------------------------------------------
        # 7. Lap count decreased.
        #
        # Example:
        #   5 -> 1
        #
        # This is NOT treated as a normal lap transition.
        #
        # It may indicate:
        # - race reset
        # - return to pits
        # - new race
        # - session state change
        #
        # We deliberately don't invent a LAP_STARTED event here.
        # ---------------------------------------------------------
        elif current_lap < previous_lap:
            pass

        # ---------------------------------------------------------
        # 8. This is now the latest valid chronological sample.
        # ---------------------------------------------------------
        self.last_sample = sample

        return events