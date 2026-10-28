"""Liczy w symulatorze: wykonania `STA ($80),Y` (piksele) per bank, cykle kasowania/rysowania/fillu."""
import sys, json
from collections import Counter
from fxsim import Machine

rom = open(sys.argv[1], "rb").read()
if rom[:4] == b"CART":
    rom = rom[16:]
d = sys.argv[2]
meta = json.load(open(f"{d}/meta.json"))
tot = Counter(); n = 0
for m in meta:
    img = bytearray(open(f"{d}/{m['k']:05d}.in", "rb").read()); img[0x42] = 0
    mc = Machine(rom, img, m["bank"], m["regs"])
    mem = mc.mem
    cnt = Counter()

    def tr(c):
        op = mem[c.pc]
        if op == 0x91 and mem[c.pc + 1] == 0x80:
            cnt[("plot", mem.bank if c.pc < 0xA000 else 15)] += 1

    stop = 0xA340 if m["pc"] == 0xA331 else 0xA37E
    c = mc.run(m["pc"], stop, trace=tr)
    tot.update(cnt); tot["cycles"] += c; n += 1
print("obrazów", n)
for k, v in sorted(tot.items(), key=str):
    print(k, v / n)
