import time
from collector.gt7_offsets import GT7_PACKET_SIZE

class GT7Packet:
    def __init__(self, raw_data: bytes):
        self.raw_data = raw_data
        self.timestamp = time.time()
        self.packet_size = len(raw_data)
        self.validate()

    def validate(self):
        """
        Vérifie si le paquet semble être un paquet GT7 valide.
        Note : GT7 peut envoyer des paquets plus petits ou de tailles différentes 
        selon l'état du jeu, mais pour la télémétrie active, on attend une certaine taille.
        """
        if self.packet_size == 0:
            raise ValueError("Empty packet received")
        
        if self.packet_size < 128: # Taille minimale arbitraire pour un paquet de données
             raise ValueError(f"Packet too small: {self.packet_size} bytes")

    def __repr__(self):
        return f"<GT7Packet size={self.packet_size} at {self.timestamp}>"
