import struct
from typing import BinaryIO


class AdvancedBinaryIO:
    def __init__(self, file: BinaryIO):
        self.file = file

    def read_int(self) -> int:
        return int.from_bytes(self.file.read(4), "big")

    def write_int(self, num: int):
        self.file.write(num.to_bytes(4, "big"))

    def read_float(self) -> float:
        return struct.unpack('f', self.file.read(4))[0]

    def write_float(self, num: float):
        self.file.write(struct.pack('f', num))

    def read_string(self):
        size = self.read_int()
        return self.file.read(size).decode('utf-8')

    def write_string(self, text: str):
        text_bytes = text.encode('utf-8')
        self.write_int(len(text_bytes))
        self.file.write(text_bytes)

    def read_bool(self) -> bool:
        return self.file.read(1) == b'\1'

    def write_bool(self, num: bool):
        self.file.write(b'\1' if num else b'\0')
