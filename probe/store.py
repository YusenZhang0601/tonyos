"""Crash-safe framing, produced by experiment E2.

A frame is `magic | length | crc32 | payload`. Recovery returns the longest
prefix of complete, checksum-valid frames and the byte offset where it stopped.
It never raises: a torn tail is a normal condition, not an error.
"""
import struct
import zlib

MAGIC = b"TY1"
HEADER = struct.Struct("<3sII")      # 11 bytes


def frame(payload: bytes) -> bytes:
    return HEADER.pack(MAGIC, len(payload), zlib.crc32(payload)) + payload


def recover(data: bytes):
    """-> (payloads, valid_bytes). Stops at the first incomplete or corrupt frame."""
    out, off = [], 0
    while off + HEADER.size <= len(data):
        magic, length, crc = HEADER.unpack_from(data, off)
        if magic != MAGIC:
            break
        start = off + HEADER.size
        end = start + length
        if end > len(data):
            break
        payload = data[start:end]
        if zlib.crc32(payload) != crc:
            break
        out.append(payload)
        off = end
    return out, off
