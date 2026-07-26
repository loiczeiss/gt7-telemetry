import socket
import logging
from typing import Optional, Tuple
from config import GT7_IP, GT7_PORT, BUFFER_SIZE

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class UDPListener:
    def __init__(self, ip: str = GT7_IP, port: int = GT7_PORT):
        self.ip = ip
        self.port = port
        self.sock: Optional[socket.socket] = None

    def start(self):
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.sock.bind((self.ip, self.port))
            logger.info(f"UDP listener started on {self.ip}:{self.port}")
        except Exception as e:
            logger.error(f"Failed to start UDP listener: {e}")
            raise

    def receive(self) -> Tuple[bytes, tuple]:
        if not self.sock:
            raise RuntimeError("Socket not started. Call start() first.")
        
        try:
            data, addr = self.sock.recvfrom(BUFFER_SIZE)
            logger.debug(f"Packet received: {len(data)} bytes from {addr}")
            return data, addr
        except Exception as e:
            logger.error(f"Error receiving UDP packet: {e}")
            raise

    def stop(self):
        if self.sock:
            self.sock.close()
            logger.info("UDP listener stopped")
