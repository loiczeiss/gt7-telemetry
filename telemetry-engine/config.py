GT7_IP = "0.0.0.0"  # Écoute sur toutes les interfaces
GT7_PORT = 33740      # Port par défaut de GT7
BUFFER_SIZE = 1500    # Taille max d'un paquet UDP standard MTU

# Configuration de la détection de tours
TRACK_LENGTH = 5000.0  # Valeur par défaut, à adapter par circuit
FINISH_LINE_START_PERCENTAGE = 0.95  # Zone de fin de tour (95%+)
FINISH_LINE_END_PERCENTAGE = 0.05    # Zone de début de tour (0-5%)
MIN_SPEED_FOR_LAP = 10.0            # Vitesse min en km/h pour valider un passage
