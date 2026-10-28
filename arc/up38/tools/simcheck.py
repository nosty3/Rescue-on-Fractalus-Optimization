"""Walidacja symulatora: potok v10.1 (od `ldx` kasowania do po fillu) na nagranych scenach vs bufor z Altirry."""
import sys, json, time
from fxsim import Machine

rom = open(sys.argv[1], "rb").read()
if rom[:4] == b"CART":
    rom = rom[16:]
d = sys.argv[2]
meta = json.load(open(f"{d}/meta.json"))
ok = 0; t0 = time.time(); cyc = []
for m in meta:
    img = bytearray(open(f"{d}/{m['k']:05d}.in", "rb").read())
    img[0x42] = 0  # przełączenie bufora już się odbyło (w symulacji nie ma VBI)
    mc = Machine(rom, img, m["bank"], m["regs"])
    stop = 0xA340 if m["pc"] == 0xA331 else 0xA37E
    c = mc.run(m["pc"], stop)
    cyc.append(c)
    real = open(f"{d}/{m['k']:05d}.buf", "rb").read()
    sim = bytes(mc.mem[0x1010:0x1010 + 96 * 48])
    x0 = 51 if m["pc"] == 0xA331 else 3
    diff = [(i // 96, i % 96) for i in range(len(sim)) if sim[i] != real[i] and x0 <= i % 96 < x0 + 42]
    if diff:
        print(m["k"], "DIFF", len(diff), diff[:6])
    else:
        ok += 1
print(f"{ok}/{len(meta)} scen zgodnych, średnio {sum(cyc)/len(cyc):.0f} cykli CPU, {time.time()-t0:.1f}s")
