"""Builds and parses Modbus RTU frames with their CRC, decodes registers into integers and floats and computes the
poll cycle of a bus.

Week: 8
Inputs: device addresses, register addresses and counts, the baud rate and the reply delay of each device.
Outputs: request frames as bytes, register values from a response frame, the time of each transaction and of a cycle.
Example: python modbus_rtu_frames.py
The frame layout follows the MODBUS Application Protocol Specification V1.1b3 and the timing follows the MODBUS over
Serial Line Specification and Implementation Guide V1.02 (11 bits per character, a silence of 3.5 characters).
Only the Python standard library is needed. To talk to real devices, send the frames with a serial library such as
pyserial, or use a Modbus library such as pymodbus.
"""
import struct


def crc16_modbus(data: bytes) -> int:
    """CRC-16 of Modbus RTU: initial value 0xFFFF, reflected polynomial 0xA001."""
    crc = 0xFFFF
    for b in data:
        crc ^= b
        for _ in range(8):
            crc = (crc >> 1) ^ 0xA001 if crc & 1 else crc >> 1
    return crc


def with_crc(pdu: bytes) -> bytes:
    crc = crc16_modbus(pdu)
    return pdu + bytes([crc & 0xFF, crc >> 8])          # low byte first


def read_holding_registers(address: int, start: int, count: int) -> bytes:
    """Request of function 03 (1 to 125 registers)."""
    if not 1 <= count <= 125:
        raise ValueError("function 03 reads 1 to 125 registers")
    return with_crc(bytes([address, 0x03]) + struct.pack(">HH", start, count))


def write_single_register(address: int, register: int, value: int) -> bytes:
    """Request of function 06."""
    return with_crc(bytes([address, 0x06]) + struct.pack(">HH", register, value & 0xFFFF))


def parse_read_response(frame: bytes, address: int) -> list:
    """Checks the CRC, the address and the function code of a response to function 03 and returns the registers."""
    if crc16_modbus(frame) != 0:
        raise ValueError("CRC error")
    if frame[0] != address:
        raise ValueError(f"answer from address {frame[0]}, expected {address}")
    if frame[1] & 0x80:
        raise ValueError(f"exception code {frame[2]}")
    n = frame[2] // 2
    return list(struct.unpack(f">{n}H", frame[3:3 + 2 * n]))


def regs_to_float(hi: int, lo: int) -> float:
    """Two registers, most significant word first, as a 32-bit IEEE 754 float."""
    return struct.unpack(">f", struct.pack(">HH", hi, lo))[0]


def float_to_regs(x: float) -> tuple:
    return struct.unpack(">HH", struct.pack(">f", x))


def t35_ms(baud: int) -> float:
    return 1.75 if baud > 19200 else 3.5 * 11 / baud * 1000


def transaction_ms(n_regs: int, baud: int, reply_ms: float = 5.0) -> float:
    """Request (8 bytes), response (5 + 2N bytes), two silences and the reply delay of the device."""
    t_char = 11 / baud * 1000
    return (8 + 5 + 2 * n_regs) * t_char + 2 * t35_ms(baud) + reply_ms


def cycle_ms(devices, baud: int) -> float:
    """devices: list of (name, address, registers, reply_ms)."""
    return sum(transaction_ms(n, baud, r) for _, _, n, r in devices)


if __name__ == "__main__":
    req = read_holding_registers(1, 0, 10)
    print("request:", req.hex(" ").upper())                       # 01 03 00 00 00 0A C5 CD
    hi, lo = float_to_regs(49.98)
    resp = with_crc(bytes([1, 3, 4]) + struct.pack(">HH", hi, lo))
    regs = parse_read_response(resp, 1)
    print("response:", resp.hex(" ").upper(), "->", round(regs_to_float(*regs), 2), "Hz")
    bus = [("container meter", 1, 10, 5.0), ("battery inverter", 2, 20, 5.0), ("battery BMS", 3, 40, 5.0)]
    for baud in (9600, 19200, 38400, 115200):
        print(f"{baud:>6} baud: poll cycle {cycle_ms(bus, baud):6.1f} ms")
