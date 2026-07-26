import time
import logging
from datetime import datetime
from collector.udp_listener import UDPListener
from collector.decoder import GT7Decoder
from collector.mock_generator import MockTelemetryGenerator
from storage.sqlite import SQLiteStorage
from session.session_manager import SessionManager
from config import GT7_IP, GT7_PORT

# Configuration du logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def main(use_mock=True):
    # Initialisation du stockage
    storage = SQLiteStorage()
    
    # Métadonnées de session (pourraient être dynamiques plus tard)
    driver_id = "User1"
    track = "Trial Mountain"
    car = "Toyota GR Yaris"
    
    # Initialisation du gestionnaire de session
    session_manager = SessionManager(storage, driver_id, track, car)
    logger.info(f"Session démarrée : {track} avec {car} (ID: {session_manager.session.id})")

    if use_mock:
        logger.info("Utilisation du simulateur de télémétrie")
        generator = MockTelemetryGenerator()
        
        try:
            # Simuler un flux de 100 samples
            for sample in generator.generate(count=100):
                session_manager.process_sample(sample)
                time.sleep(0.01) # Simule un flux à 100Hz
        except KeyboardInterrupt:
            pass
    else:
        logger.info(f"Écoute des paquets GT7 sur {GT7_IP}:{GT7_PORT}")
        listener = UDPListener(GT7_IP, GT7_PORT)
        decoder = GT7Decoder()
        
        try:
            while True:
                packet = listener.receive()
                if packet:
                    sample = decoder.decode(packet)
                    if sample:
                        session_manager.process_sample(sample)
        except KeyboardInterrupt:
            logger.info("Arrêt du collector...")
        finally:
            listener.close()

    session_manager.end_session()
    logger.info(f"Session terminée. {len(session_manager.session.laps)} tours enregistrés.")
    storage.close()

if __name__ == "__main__":
    import sys
    use_mock = "--real" not in sys.argv
    main(use_mock=use_mock)
