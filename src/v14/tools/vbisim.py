"""Symulacja VBI gry: Machine z logiem zapisów do sprzętu ($D000-$D7FF) i profilem cykli.
Start w $B46C (wejście VBI gry przez VVBLKI), koniec przy pierwszym wejściu do $E462 (XITVBV)."""
from collections import Counter
from fxsim import Machine, Mem


class LogMem(Mem):
    def setup(self, rom):
        Mem.setup(self, rom)
        self.hw = []

    def __setitem__(self, addr, v):
        if 0xD000 <= addr < 0xD800:
            self.hw.append((addr, v))
        Mem.__setitem__(self, addr, v)


class VbiMachine(Machine):
    def __init__(self, rom, image, bank, regs=None):
        self.mem = LogMem(image)
        self.mem.setup(rom)
        self.mem.select(bank)
        from py65.devices.mpu6502 import MPU
        self.cpu = MPU(memory=self.mem, pc=0)
        if regs:
            self.cpu.a, self.cpu.x, self.cpu.y = regs.get("a", 0), regs.get("x", 0), regs.get("y", 0)
            self.cpu.sp = regs.get("sp", 0xFF)
            self.cpu.p = regs.get("p", 0x30)

    def run_vbi(self, prof=None, limit=200000):
        """Wykonuje VBI od $B46C do $E462. prof: Counter (bank, pc) -> cykle. Zwraca cykle CPU."""
        c = self.cpu; mem = self.mem
        c.pc = 0xB46C
        start = c.processorCycles
        n = 0
        while c.pc != 0xE462:
            pc = c.pc
            b = c.processorCycles
            c.step()
            if prof is not None:
                prof[(mem.bank if 0x8000 <= pc < 0xA000 else (15 if pc >= 0xA000 else -1), pc)] += c.processorCycles - b
            n += 1
            if n > limit:
                raise RuntimeError(f"VBI nie kończy się, PC=${c.pc:04x}")
        return c.processorCycles - start


def load_scene(d, m, rom):
    img = bytearray(open(f"{d}/{m['k']:05d}.in", "rb").read())
    return VbiMachine(rom, img, m["bank"], m["regs"])
