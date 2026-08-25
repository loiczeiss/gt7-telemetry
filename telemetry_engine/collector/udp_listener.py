import socket
import logging
from typing import Optional, Tuple
from config import BUFFER_SIZE, GT7_IP, GT7_PORT, RECV_TIMEOUT_S

logger = logging.getLogger(__name__)


class UDPListener:
    def __init__(self, ip: str = GT7_IP, port: int = GT7_PORT, timeout_s: float = RECV_TIMEOUT_S):
        self.ip = ip
        self.port = port
        self.timeout_s = timeout_s
        self.sock: Optional[socket.socket] = None

    def start(self):
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.sock.bind((self.ip, self.port))
            self.sock.settimeout(self.timeout_s)
            logger.info("UDP listener started on %s:%s", self.ip, self.port)
        except Exception as e:
            logger.error("Failed to start UDP listener: %s", e)
            raise

    def receive(self) -> Tuple[Optional[bytes], Optional[tuple]]:
        if not self.sock:
            raise RuntimeError("Socket not started. Call start() first.")

        try:
            data, addr = self.sock.recvfrom(BUFFER_SIZE)
            logger.debug("Packet received: %s bytes from %s", len(data), addr)
            return data, addr
        except socket.timeout:
            return None, None
        except Exception as e:
            logger.error("Error receiving UDP packet: %s", e)
            raise

    def stop(self):
        if self.sock:
            self.sock.close()
            self.sock = None
            logger.info("UDP listener stopped")

    def close(self):
        self.stop()