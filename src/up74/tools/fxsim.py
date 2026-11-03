"""Symulator 6502 (py65) maszyny Fractalusa: 64 KB RAM, kartridż XEGS (okno $8000-$9FFF wybierane
zapisem do $D5xx, stały ostatni bank w $A000-$BFFF), OS ROM $C000-$FFFF tylko do odczytu.
Służy do porównań bajt w bajt potoku rysowania (kasowanie, góry, fill) między wersjami ROM-u."""
from py65.devices.mpu6502 import MPU


class Mem(bytearray):
    """Odczyt = zwykły bytearray (szybki). Zapis: RAM < $8000, $D5xx = bank, reszta ROM/sprzęt ignorowana."""

    def setup(self, rom):
        self.rom = rom
        self.nbanks = len(rom) // 8192
        self.bank = None
        self.bank_writes = 0
        bytearray.__setitem__(self, slice(0xA000, 0xC000), rom[-8192:])

    def select(self, b):
        b %= self.nbanks
        if b != self.bank:
            self.bank = b
            bytearray.__setitem__(self, slice(0x8000, 0xA000), self.rom[b * 8192:(b + 1) * 8192])

    def __setitem__(self, addr, v):
        if addr < 0x8000:
            bytearray.__setitem__(self, addr, v)
        elif 0xD500 <= addr < 0xD600:
            self.bank_writes += 1
            self.select(v)


class Machine:
    def __init__(self, rom, image, bank, regs=None):
        """rom: bytes kartridża; image: 64 KB widoku pamięci (RAM + OS ROM; okno kartridża nadpisujemy)."""
        self.mem = Mem(image)
        self.mem.setup(rom)
        self.mem.select(bank)
        self.cpu = MPU(memory=self.mem, pc=0)
        if regs:
            self.cpu.a, self.cpu.x, self.cpu.y = regs.get("a", 0), regs.get("x", 0), regs.get("y", 0)
            self.cpu.sp = regs.get("sp", 0xFF)
            self.cpu.p = regs.get("p", 0x30)

    def run(self, pc, stop, limit=5_000_000, trace=None):
        """Wykonuje od pc do osiągnięcia adresu stop (w stałym banku). Zwraca liczbę cykli CPU (bez DMA)."""
        c = self.cpu
        c.pc = pc
        start = c.processorCycles
        n = 0
        step = c.step
        while c.pc != stop:
            if trace is not None:
                trace(c)
            step()
            n += 1
            if n > limit:
                raise RuntimeError(f"limit instrukcji, PC=${c.pc:04x} bank {self.mem.bank}")
        return c.processorCycles - start
