import os

LISTEN_IP = os.environ.get("GT7_LISTEN_IP", "0.0.0.0")
LISTEN_PORT = int(os.environ.get("GT7_LISTEN_PORT", "33740"))
GT7_IP = LISTEN_IP  # alias historique (bind)
GT7_PORT = LISTEN_PORT
BUFFER_SIZE = 1500
RECV_TIMEOUT_S = 1.0

PS5_IP = os.environ.get("GT7_PS5_IP", "")
HEARTBEAT_PORT = 33739
HEARTBEAT_PAYLOAD = b"A"
HEARTBEAT_INTERVAL_S = 2.0

SALSA20_KEY = b"Simulator Interface Packet GT7 ver 0.0"[:32]  # Salsa20 exige 32 octets
SALSA20_IV_OFFSET = 0x40
SALSA20_MAGIC = 0x47375330
SALSA20_IV_XOR = 0xDEADBEAF  # orthographe du jeu, pas DEADBEEF

# Configuration de la détection de tours
TRACK_LENGTH = 5000.0  # Valeur par défaut, à adapter par circuit
FINISH_LINE_START_PERCENTAGE = 0.95  # Zone de fin de tour (95%+)
FINISH_LINE_END_PERCENTAGE = 0.05    # Zone de début de tour (0-5%)
MIN_SPEED_FOR_LAP = 10.0            # Vitesse min en km/h pour valider un passage


def require_ps5_ip(ps5_ip: str | None = None) -> str:
    ip = (ps5_ip if ps5_ip is not None else PS5_IP).strip()
    if not ip or ip == "0.0.0.0":
        raise SystemExit(
            "GT7_PS5_IP est requis en mode --real (IP LAN de la console, pas 0.0.0.0)."
        )
    return ip
