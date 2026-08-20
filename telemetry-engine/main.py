import time
import logging
from collector.udp_listener import UDPListener
from collector.decoder import GT7Decoder
from collector.heartbeat import HeartbeatSender
from collector.mock_generator import MockTelemetryGenerator
from storage.sqlite import SQLiteStorage
from session.session_manager import SessionManager
from config import LISTEN_IP, LISTEN_PORT, PS5_IP, require_ps5_ip

logging.basicConfig(level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


def main(use_mock=False):
    storage = SQLiteStorage()

    driver_id = "User1"

    session_manager = SessionManager(storage, driver_id)
    logger.info("Session démarrée : %s (ID: %s)", driver_id, session_manager.session.id)

    if use_mock:
        logger.info("Utilisation du simulateur de télémétrie")
        generator = MockTelemetryGenerator()

        try:
            for sample in generator.generate(count=100):
                session_manager.process_sample(sample)
                time.sleep(0.01)
        except KeyboardInterrupt:
            pass
    else:
        ps5_ip = require_ps5_ip(PS5_IP)
        logger.info("Écoute des paquets GT7 sur %s:%s (heartbeat -> %s)", LISTEN_IP, LISTEN_PORT, ps5_ip)
        listener = UDPListener(LISTEN_IP, LISTEN_PORT)
        heartbeat = HeartbeatSender(ps5_ip)
        decoder = GT7Decoder()

        listener.start()
        heartbeat.start()
        try:
            while True:
                data, _addr = listener.receive()
                if data:
                    with open("sample_packet.bin", "wb") as f:
                        f.write(data)
                if not data:
                    continue
                sample = decoder.decode(data, encrypted=True)
                if sample:
                    logger.debug("lap_count=%s speed=%s", sample.lap_count, getattr(sample, "speed", None))
                    session_manager.process_sample(sample)
                if not sample:
                    logger.debug("decode() returned None for %d bytes", len(data))
                    continue
        except KeyboardInterrupt:
            logger.info("Arrêt du collector...")
        finally:
            heartbeat.stop()
            listener.stop()

    session_manager.end_session()
    logger.info("Session terminée. %s tours enregistrés.", len(session_manager.session.laps))
    storage.close()


if __name__ == "__main__":
    import sys
    use_mock = "--real" not in sys.argv
    main(use_mock=use_mock)