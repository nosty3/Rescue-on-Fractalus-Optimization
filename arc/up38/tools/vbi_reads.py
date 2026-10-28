"""Czy VBI gry (wejście $B46C) czyta bajty strony zerowej rasteryzacji? Nagrywa N stanów w Altirrze na $B46C,
symuluje VBI do XITVBV ($E462) i wypisuje odczyty z listy adresów (z PC)."""
import sys, json
from collections import Counter
from fx import Emu, enter_flight
from fxsim import Machine
from py65.disassembler import Disassembler

ROMP = sys.argv[1]; N = int(sys.argv[2])
ADDRS = set([0x82, 0x83, 0x84, 0x85, 0x86] + list(range(0x95, 0xA0)) + list(range(0xEA, 0xFF)))
rom = open(ROMP, "rb").read(); rom = rom[16:] if rom[:4] == b"CART" else rom
hits = Counter(); states = []
with Emu("pal") as e:
    a = e.a
    enter_flight(a, ROMP, 3165); a.frame(170)
    a.bp_set(0xB46C)
    for i in range(N):
        a.frame(3 + i % 5)
        a.frame(2)
        r = a.regs()
        if r["PC"] != "$b46c":
            continue
        regs = {k.lower(): int(v[1:], 16) for k, v in r.items() if k in ("A", "X", "Y", "S", "P")}
        regs["sp"] = regs.pop("s")
        states.append((bytes(a.memdump(0, 0x10000)), regs, a.cart_info()["bank"]))
for img, regs, bank in states:
    mc = Machine(rom, bytearray(img), bank, regs); c = mc.cpu; ds = Disassembler(c)
    c.pc = 0xB46C; steps = 0
    while c.pc not in (0xE462,) and steps < 200000:
        length, text = ds.instruction_at(c.pc)
        p = text.split()
        if len(p) > 1 and p[1].startswith(("$", "($")):
            arg = p[1].strip("()").replace("),Y", "").split(",")[0].strip("()")
            try:
                ea = int(arg[1:], 16)
                if ea in ADDRS and not p[0].startswith("ST"):
                    hits[(ea, c.pc, text)] += 1
            except ValueError:
                pass
        c.step(); steps += 1
print("stanów", len(states))
for k, v in sorted(hits.items()):
    print(f"  ${k[0]:02x} @ ${k[1]:04x} {k[2]}: {v}")
