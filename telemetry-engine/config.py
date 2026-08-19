import os

LISTEN_IP = os.environ.get("GT7_LISTEN_IP", "192.168.1.8")  # IP de CE PC, pas de la PS5
LISTEN_PORT = int(os.environ.get("GT7_LISTEN_PORT", "33740"))
GT7_IP = LISTEN_IP  # alias historique (bind)
GT7_PORT = LISTEN_PORT
BUFFER_SIZE = 1500
RECV_TIMEOUT_S = 1.0

PS5_IP = os.environ.get("GT7_PS5_IP", "192.168.1.12")  # IP de la console
HEARTBEAT_PORT = 33739
HEARTBEAT_PAYLOAD = b"A"
HEARTBEAT_INTERVAL_S = 2.0

SALSA20_KEY = b"Simulator Interface Packet GT7 ver 0.0"[:32]  # Salsa20 exige 32 octets
SALSA20_IV_OFFSET = 0x40
SALSA20_MAGIC = 0x47375330
SALSA20_IV_XOR = 0xDEADBEAF  # orthographe du jeu, pas DEADBEEF

# Détection de tours : basée sur lap_count natif GT7 (voir LapDetector),
# donc plus besoin de TRACK_LENGTH / FINISH_LINE_*_PERCENTAGE / MIN_SPEED_FOR_LAP.

# Validation de tours (voir LapValidator) : durée min par rapport à
# best_laptime_ms fourni par GT7, plus de dépendance à une distance.
LAP_MIN_DURATION_PCT = 0.5
LAP_MIN_SAMPLES = 10


def require_ps5_ip(ps5_ip: str | None = None) -> str:
    ip = (ps5_ip if ps5_ip is not None else PS5_IP).strip()
    if not ip or ip == "0.0.0.0":
        raise SystemExit(
            "GT7_PS5_IP est requis en mode --real (IP LAN de la console, pas 0.0.0.0)."
        )
    return ip