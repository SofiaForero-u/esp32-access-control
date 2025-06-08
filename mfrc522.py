# MFRC522.py - Micropython driver for the MFRC522 RFID reader.
# Adapted from https://github.com/wendlers/micropython-mfrc522

from machine import Pin, SPI
from os import uname
import time

class MFRC522:

    OK = 0
    NOTAGERR = 1
    ERR = 2

    REQIDL = 0x26
    REQALL = 0x52
    AUTHENT1A = 0x60
    AUTHENT1B = 0x61

    def __init__(self, spi, gpio_rst, gpio_cs):
        self.spi = spi
        self.rst = gpio_rst
        self.cs = gpio_cs

        self.cs.init(Pin.OUT, value=1)
        self.rst.init(Pin.OUT, value=1)

        self.reset()
        self.write(0x2A, 0x8D)
        self.write(0x2B, 0x3E)
        self.write(0x2D, 30)
        self.write(0x2C, 0)
        self.write(0x15, 0x40)
        self.write(0x11, 0x3D)
        self.antenna_on()

    def _wreg(self, reg, val):
        self.cs(0)
        self.spi.write(bytearray([(reg << 1) & 0x7E]))
        self.spi.write(bytearray([val]))
        self.cs(1)

    def _rreg(self, reg):
        self.cs(0)
        self.spi.write(bytearray([((reg << 1) & 0x7E) | 0x80]))
        val = self.spi.read(1)
        self.cs(1)
        return val[0]

    def write(self, reg, val):
        self._wreg(reg, val)

    def read(self, reg):
        return self._rreg(reg)

    def set_bit_mask(self, reg, mask):
        self.write(reg, self.read(reg) | mask)

    def clear_bit_mask(self, reg, mask):
        self.write(reg, self.read(reg) & (~mask))

    def antenna_on(self):
        if ~(self.read(0x14) & 0x03):
            self.set_bit_mask(0x14, 0x03)

    def antenna_off(self):
        self.clear_bit_mask(0x14, 0x03)

    def reset(self):
        self.write(0x01, 0x0F)

    def request(self, mode):
        self.write(0x0D, 0x07)
        (status, back_data, back_bits) = self._to_card(0x0C, [mode])
        if (status != self.OK) | (back_bits != 0x10):
            status = self.ERR
        return (status, back_bits)

    def anticoll(self):
        ser_chk = 0
        ser = [0x93, 0x20]
        self.write(0x0D, 0x00)
        (status, back_data, back_bits) = self._to_card(0x0C, ser)

        if status == self.OK:
            if len(back_data) == 5:
                for i in range(4):
                    ser_chk ^= back_data[i]
                if ser_chk != back_data[4]:
                    status = self.ERR
            else:
                status = self.ERR

        return (status, back_data)

    def _to_card(self, command, send):
        back_data = []
        back_len = 0
        status = self.ERR
        irq_en = 0x00
        wait_irq = 0x00
        last_bits = None
        n = 0

        if command == 0x0E:
            irq_en = 0x12
            wait_irq = 0x10
        elif command == 0x0C:
            irq_en = 0x77
            wait_irq = 0x30

        self.write(0x02, irq_en | 0x80)
        self.clear_bit_mask(0x04, 0x80)
        self.set_bit_mask(0x0A, 0x80)
        self.write(0x01, 0x00)

        for c in send:
            self.write(0x09, c)

        self.write(0x01, command)

        if command == 0x0C:
            self.set_bit_mask(0x0D, 0x80)

        i = 2000
        while True:
            n = self.read(0x04)
            i -= 1
            if not ((i != 0) and ~(n & 0x01) and ~(n & wait_irq)):
                break

        self.clear_bit_mask(0x0D, 0x80)

        if i:
            if (self.read(0x06) & 0x1B) == 0x00:
                status = self.OK
                if n & irq_en & 0x01:
                    status = self.NOTAGERR
                elif command == 0x0C:
                    n = self.read(0x0A)
                    last_bits = self.read(0x0C) & 0x07
                    if last_bits:
                        back_len = (n - 1) * 8 + last_bits
                    else:
                        back_len = n * 8
                    if n == 0:
                        n = 1
                    if n > 16:
                        n = 16
                    for _ in range(n):
                        back_data.append(self.read(0x09))
            else:
                status = self.ERR

        return (status, back_data, back_len)
