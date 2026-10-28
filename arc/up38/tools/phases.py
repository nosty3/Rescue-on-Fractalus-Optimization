"""Cykle CPU (bez DMA) faz potoku: kasowanie / góry ($87D3) / fill, średnio na obraz + udział nieba."""
import sys, json
from fxsim import Machine

rom = open(sys.argv[1], "rb").read()
if rom[:4] == b"CART":
    rom = rom[16:]
d = sys.argv[2]
meta = json.load(open(f"{d}/meta.json"))
acc = [0, 0, 0]; n = 0; sky = 0
for m in meta:
    img = bytearray(open(f"{d}/{m['k']:05d}.in", "rb").read()); img[0x42] = 0
    mc = Machine(rom, img, m["bank"], m["regs"])
    p = m["pc"]
    pts = [p, p + 5, p + 10, p + 15]  # ldx/jsr clear | ldx/jsr 87D3 | ldx/jsr fill | po
    for i in range(3):
        acc[i] += mc.run(pts[i], pts[i + 1])
    buf = mc.mem[0x1010:0x1010 + 96 * 48]
    x0 = 51 if p == 0xA331 else 3
    for c in range(42):
        r = 1
        while r < 44 and buf[r * 96 + x0 + c] == 0x55:
            r += 1
        sky += r - 1
    n += 1
print(f"obrazów {n}: kasowanie {acc[0]/n:.0f}, góry {acc[1]/n:.0f}, fill {acc[2]/n:.0f} cykli CPU; "
      f"niebo wiersze 1-43: {sky/(n*42*43):.3f}")
