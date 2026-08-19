import logging
import socket
import threading
import time
from typing import Optional

from config import HEARTBEAT_INTERVAL_S, HEARTBEAT_PAYLOAD, HEARTBEAT_PORT

logger = logging.getLogger(__name__)


class HeartbeatSender:
    """Envoie périodiquement b'A' vers la PS5 (port 33739) pour maintenir le flux GT7."""

    def __init__(
        self,
        ps5_ip: str,
        port: int = HEARTBEAT_PORT,
        interval_s: float = HEARTBEAT_INTERVAL_S,
        sock: Optional[socket.socket] = None,
    ):
        self.ps5_ip = ps5_ip
        self.port = port
        self.interval_s = interval_s
        self._owns_socket = sock is None
        self._sock = sock if sock is not None else socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self._stop = threading.Event()
        self._thread: Optional[threading.Thread] = None

    def _send_once(self) -> None:
        try:
            self._sock.sendto(HEARTBEAT_PAYLOAD, (self.ps5_ip, self.port))
            logger.debug("Heartbeat sent to %s:%s", self.ps5_ip, self.port)
        except OSError as exc:
            logger.warning("Heartbeat send failed: %s", exc)

    def _run(self) -> None:
        while not self._stop.wait(self.interval_s):
            self._send_once()

    def start(self) -> None:
        if self._thread and self._thread.is_alive():
            return
        self._stop.clear()
        logger.info("Heartbeat started -> %s:%s every %ss", self.ps5_ip, self.port, self.interval_s)
        self._send_once()
        self._thread = threading.Thread(target=self._run, name="gt7-heartbeat", daemon=True)
        self._thread.start()

    def stop(self) -> None:
        self._stop.set()
        if self._thread:
            self._thread.join(timeout=self.interval_s + 1.0)
            self._thread = None
        if self._owns_socket:
            self._sock.close()
        logger.info("Heartbeat stopped")
