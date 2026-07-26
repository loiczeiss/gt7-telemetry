# Offsets pour les paquets GT7 (basé sur la documentation communautaire)
# Note : Les données sont généralement des float (4 bytes) ou des int (4 bytes)

# Position dans le paquet
TIMESTAMP_OFFSET = 0x0   # Parfois 0x0 selon la version, souvent ignoré au profit de l'heure système
POSITION_X_OFFSET = 0x04 # Float
POSITION_Y_OFFSET = 0x08 # Float
POSITION_Z_OFFSET = 0x0C # Float
VELOCITY_X_OFFSET = 0x10 # Float
VELOCITY_Y_OFFSET = 0x14 # Float
VELOCITY_Z_OFFSET = 0x18 # Float

SPEED_OFFSET = 0x4C      # Float (en m/s, à convertir en km/h)
RPM_OFFSET = 0x2C        # Float
MAX_RPM_OFFSET = 0x30    # Float

GEAR_OFFSET = 0x5C       # Byte (souvent 0x5C pour le rapport actuel)
THROTTLE_OFFSET = 0x5D   # Byte (0-255)
BRAKE_OFFSET = 0x5E      # Byte (0-255)

STEERING_OFFSET = 0x0    # A confirmer, souvent calculé ou à un autre offset
DISTANCE_OFFSET = 0x54   # Float (mètres parcourus)

# Taille attendue du paquet GT7
GT7_PACKET_SIZE = 0x128  # 296 bytes
