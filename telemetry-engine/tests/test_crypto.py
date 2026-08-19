import struct

import pytest

from collector.crypto import decrypt_gt7_packet, encrypt_gt7_packet
from collector.gt7_offsets import GT7_PACKET_SIZE, SPEED_OFFSET
from config import SALSA20_MAGIC, SALSA20_IV_OFFSET


def _plaintext_with_speed(speed_ms: float = 50.0) -> bytes:
    packet = bytearray(GT7_PACKET_SIZE)
    struct.pack_into("<I", packet, 0, SALSA20_MAGIC)
    struct.pack_into("<f", packet, SPEED_OFFSET, speed_ms)
    return bytes(packet)


def test_decrypt_roundtrip_magic_and_speed():
    plaintext = _plaintext_with_speed(50.0)
    encrypted = encrypt_gt7_packet(plaintext, iv1=1)

    decrypted = decrypt_gt7_packet(encrypted)
    assert decrypted is not None
    assert int.from_bytes(decrypted[0:4], "little") == SALSA20_MAGIC
    speed = struct.unpack_from("<f", decrypted, SPEED_OFFSET)[0]
    assert speed == pytest.approx(50.0)


def test_decrypt_corrupted_ciphertext_returns_none():
    plaintext = _plaintext_with_speed(50.0)
    encrypted = bytearray(encrypt_gt7_packet(plaintext, iv1=1))
    encrypted[0] ^= 0xFF
    assert decrypt_gt7_packet(bytes(encrypted)) is None


def test_decrypt_too_short_returns_none():
    assert decrypt_gt7_packet(b"\x00" * SALSA20_IV_OFFSET) is None
