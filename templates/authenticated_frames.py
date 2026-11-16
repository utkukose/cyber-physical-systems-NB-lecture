"""Authenticated Modbus frames: a counter and an HMAC tag with SHA-256 in front of the CRC, a receiver that rejects damaged,
forged and replayed frames, and the cost of the longer frames in the poll cycle of a serial bus.

Week: 11
Inputs: a shared secret key, the address, the register and the value of a write request (function 06), the counter of
the sender, and the registers polled from each device, the baud rate and the response time of the bus.
Outputs: the authenticated frame in hexadecimal, the decision of the receiver for genuine, forged, replayed and guessed
frames, and the poll cycle in ms with plain and with authenticated frames.
Example: python authenticated_frames.py
The example is the battery inverter at address 2 with its power setpoint in register 100 on an RS-485 bus at 19200
baud with a meter, the inverter and the battery management system. Uses only the Python standard library.
"""
import hashlib
import hmac
import os
import struct

TAG_BYTES = 8


def crc16_modbus(data):
    """CRC-16 of Modbus RTU: initial value 0xFFFF, reflected polynomial 0xA001."""
    crc = 0xFFFF
    for b in data:
        crc ^= b
        for _ in range(8):
            crc = (crc >> 1) ^ 0xA001 if crc & 1 else crc >> 1
    return crc


def with_crc(body):
    crc = crc16_modbus(body)
    return body + bytes([crc & 0xFF, crc >> 8])


def secure_write(key, counter, address, register, value):
    """Function 06 with a signed value, a counter of 4 bytes and the first TAG_BYTES bytes of the HMAC with SHA-256."""
    body = bytes([address, 0x06]) + struct.pack(">HhI", register, value, counter)
    return with_crc(body + hmac.new(key, body, hashlib.sha256).digest()[:TAG_BYTES])


class Receiver:
    """Accepts a frame only if its CRC, its tag and its counter are all right."""

    def __init__(self, key):
        self.key, self.last = key, 0

    def receive(self, frame):
        if crc16_modbus(frame) != 0:
            return "rejected: damaged frame"
        body, tag = frame[:-2 - TAG_BYTES], frame[-2 - TAG_BYTES:-2]
        if not hmac.compare_digest(hmac.new(self.key, body, hashlib.sha256).digest()[:TAG_BYTES], tag):
            return "rejected: wrong tag"
        register, value, counter = struct.unpack(">HhI", body[2:10])
        if counter <= self.last:
            return "rejected: old counter"
        self.last = counter
        return f"accepted: register {register} = {value}"


def poll_time(n_reg, baud, extra=0, t_resp=5.0):
    """One Modbus transaction in ms: request and response with extra bytes each, two silent intervals, response time."""
    t_c = 11 / baud * 1000
    t35 = 1.75 if baud > 19200 else 3.5 * t_c
    return (8 + 5 + 2 * n_reg + 2 * extra) * t_c + 2 * t35 + t_resp


if __name__ == "__main__":
    key = bytes.fromhex("5f1c9a3e7b2d4c6f8e0a1b3c5d7e9f20")
    inverter = Receiver(key)
    frame = secure_write(key, 41, 2, 100, 120)
    print(len(frame), "bytes:", frame.hex(" ").upper())
    print("genuine: ", inverter.receive(frame))
    forged = bytearray(frame[:-2])
    forged[4:6] = struct.pack(">h", -250)
    print("forged:  ", inverter.receive(with_crc(bytes(forged))))
    print("replayed:", inverter.receive(frame))
    forged[6:10] = struct.pack(">I", 42)
    guesses = sum(inverter.receive(with_crc(bytes(forged[:10]) + os.urandom(TAG_BYTES))).startswith("accepted")
                  for _ in range(1000))
    print("random tags accepted:", guesses, "of 1000")
    bus = [10, 20, 40]
    for baud in (9600, 19200, 38400):
        plain = sum(poll_time(n, baud) for n in bus)
        secure = sum(poll_time(n, baud, extra=4 + TAG_BYTES) for n in bus)
        print(f"{baud:>6} baud: poll cycle {plain:7.2f} ms plain, {secure:7.2f} ms with counter and tag")
