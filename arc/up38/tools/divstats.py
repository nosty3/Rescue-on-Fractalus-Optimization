"""Argumenty dzieleń $8224 (B1:B0 / AF:AE -> B2) w scenach: rozkład D, czy x i y punktu mają wspólne D."""
import sys, json
from collections import Counter
from fxsim import Machine

rom = open(sys.argv[1], "rb").read()
if rom[:4] == b"CART":
    rom = rom[16:]
d = sys.argv[2]
meta = json.load(open(f"{d}/meta.json"))
calls = []
for m in meta:
    img = bytearray(open(f"{d}/{m['k']:05d}.in", "rb").read()); img[0x42] = 0
    mc = Machine(rom, img, m["bank"], m["regs"])
    mem = mc.mem

    def tr(c):
        if c.pc == 0x8224 and mem.bank == 2:
            ret = mem[0x100 + c.sp + 1] | mem[0x100 + c.sp + 2] << 8
            N = mem[0xB0] | mem[0xB1] << 8; D = mem[0xAE] | mem[0xAF] << 8
            calls.append((ret, N, D))

    mc.run(m["pc"], 0xA340 if m["pc"] == 0xA331 else 0xA37E, trace=tr)
print("wywołań", len(calls), "na obraz", len(calls) / len(meta))
print("miejsca:", Counter(hex(c[0]) for c in calls))
hb = Counter(c[2] >> 8 for c in calls)
print("D >> 8 rozkład (top):", sorted(hb.items())[:20], "...")
print("D < 256:", sum(1 for c in calls if c[2] < 256), " D < 4096:", sum(1 for c in calls if c[2] < 4096))
same = sum(1 for a, b in zip(calls, calls[1:]) if a[2] == b[2])
print("kolejne z tym samym D:", same)
for c in calls[:12]:
    print(hex(c[0]), c[1], c[2], (256 * c[1]) // c[2] if c[2] else None)
