from typing import Optional

from Crypto.Cipher import Salsa20

from collector.gt7_offsets import GT7_PACKETC_SIZE
from config import SALSA20_IV_OFFSET, SALSA20_IV_XOR, SALSA20_KEY, SALSA20_MAGIC


def _nonce_from_iv1(iv1: int) -> bytes:
    iv2 = iv1 ^ SALSA20_IV_XOR
    return iv2.to_bytes(4, "little") + iv1.to_bytes(4, "little")


def decrypt_gt7_packet(raw: bytes) -> Optional[bytes]:
    """Déchiffre un paquet UDP GT7 (Salsa20). Retourne None si invalide."""
    if len(raw) < SALSA20_IV_OFFSET + 4:
        return None

    iv1 = int.from_bytes(raw[SALSA20_IV_OFFSET : SALSA20_IV_OFFSET + 4], "little")
    cipher = Salsa20.new(key=SALSA20_KEY, nonce=_nonce_from_iv1(iv1))
    plaintext = cipher.decrypt(raw)

    magic = int.from_bytes(plaintext[0:4], "little")
    if magic != SALSA20_MAGIC:
        return None
    return plaintext


def decrypt_gt7_packet(raw: bytes) -> Optional[bytes]:
    if len(raw) < SALSA20_IV_OFFSET + 4:
        return None

    iv1 = int.from_bytes(raw[SALSA20_IV_OFFSET : SALSA20_IV_OFFSET + 4], "little")
    cipher = Salsa20.new(key=SALSA20_KEY, nonce=_nonce_from_iv1(iv1))
    plaintext = cipher.decrypt(raw)

    magic = int.from_bytes(plaintext[0:4], "little")
    if magic != SALSA20_MAGIC:
        import logging
        logging.getLogger(__name__).debug(
            "Magic mismatch: got 0x%08X, expected 0x%08X (packet len=%d)",
            magic, SALSA20_MAGIC, len(raw)
        )
        return None
    return plaintext