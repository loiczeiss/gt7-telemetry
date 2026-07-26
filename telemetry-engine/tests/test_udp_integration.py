import socket
import struct
import time
import threading
import pytest
from collector.udp_listener import UDPListener
from collector.gt7_packet import GT7Packet
from collector.decoder import GT7Decoder
from collector.gt7_offsets import *

def test_udp_flow():
    """
    Test le flux complet : Envoi UDP -> Réception -> Validation -> Décodage
    """
    # Configuration
    test_ip = "127.0.0.1"
    test_port = 55555
    
    listener = UDPListener(ip=test_ip, port=test_port)
    listener.start()
    
    # Préparation d'un paquet
    packet_data = bytearray(GT7_PACKET_SIZE)
    struct.pack_into('<f', packet_data, SPEED_OFFSET, 60.0) # 216 km/h
    
    # Fonction pour envoyer un paquet après un court délai
    def send_packet():
        time.sleep(0.1)
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.sendto(packet_data, (test_ip, test_port))
        sock.close()
    
    thread = threading.Thread(target=send_packet)
    thread.start()
    
    # Réception
    try:
        data, addr = listener.receive()
        
        # Validation et décodage
        gt7_packet = GT7Packet(data)
        sample = GT7Decoder.decode(gt7_packet.raw_data)
        
        assert len(data) == GT7_PACKET_SIZE
        assert pytest.approx(sample.speed) == 216.0
        
    finally:
        listener.stop()
        thread.join()
