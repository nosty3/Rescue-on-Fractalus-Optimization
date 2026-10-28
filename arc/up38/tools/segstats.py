"""Odcinki wchodzące do rasteryzacji ($982A, bank 2 -> bank 5): szerokość R.x-L.x, koszt cykli do wyjścia."""
import sys, json
from collections import Counter, defaultdict
from fxsim import Machine

rom = open(sys.argv[1], "rb").read()
if rom[:4] == b"CART":
    rom = rom[16:]
d = sys.argv[2]
meta = json.load(open(f"{d}/meta.json"))
wcnt = Counter(); wcyc = Counter(); nseg = 0
for m in meta:
    img = bytearray(open(f"{d}/{m['k']:05d}.in", "rb").read()); img[0x42] = 0
    mc = Machine(rom, img, m["bank"], m["regs"])
    mem = mc.mem; c = mc.cpu
    state = {}

    def tr(cpu):
        if cpu.pc == 0x982A and mem.bank == 2 and not state:
            L = mem[0x82]; R = mem[0x95]
            state["w"] = (R - L) & 0xFF if R >= L else -1
            state["c0"] = cpu.processorCycles
            state["sp"] = cpu.sp
        elif state and cpu.sp > state["sp"] + 1 and mem.bank == 2:
            pass
        # wyjście: powrót do banku 2 na $9907 (pla/plp/rts) albo rts z $986C ścieżki ogólnej
        if state and mem.bank == 2 and cpu.pc in (0x9907, 0x986C, 0x9930, 0x99B6):
            w = state["w"]
            wcnt[w] += 1; wcyc[w] += cpu.processorCycles - state["c0"]
            state.clear()

    stop = 0xA340 if m["pc"] == 0xA331 else 0xA37E
    mc.run(m["pc"], stop, trace=tr)
n = len(meta)
tot = sum(wcyc.values())
print("odcinków na obraz", sum(wcnt.values()) / n, "cykli na obraz", tot / n)
acc = 0
for w in sorted(wcnt):
    acc += wcyc[w]
    if wcnt[w] / n >= 0.3:
        print(f" w={w:4d} n/obraz {wcnt[w]/n:6.1f} cykli/odc {wcyc[w]/wcnt[w]:7.0f} udział {100*wcyc[w]/tot:5.1f}% narast {100*acc/tot:5.1f}%")
