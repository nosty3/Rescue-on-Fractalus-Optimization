"""Profil całej połówki pętli lotu w symulatorze ($A32E->$A36C, $A36C->$A32E), z podziałem na wywołania
z pętli (jsr z poziomu $A3xx) i na banki. Czekanie na VBI omijane ($42:=0 w pętli czekania).
Użycie: loopprof.py ROM DIR"""
import sys, json
from collections import Counter
from fxsim import Machine

rom = open(sys.argv[1], "rb").read()
if rom[:4] == b"CART":
    rom = rom[16:]
d = sys.argv[2]
meta = json.load(open(f"{d}/meta.json"))
WAITS = {0x84A0, 0x84A6, 0x9FD5, 0x9FDB}
per_call = Counter(); bybank = Counter(); n = 0; tot = 0
for m in meta:
    img = bytearray(open(f"{d}/{m['k']:05d}.in", "rb").read())
    mc = Machine(rom, img, m["bank"], m["regs"])
    mem = mc.mem; c = mc.cpu
    stop = 0xA36C if m["pc"] == 0xA32E else 0xA32E
    c.pc = m["pc"]
    cur = "loop"; steps = 0
    while True:
        pc = c.pc
        if pc == stop and steps:
            break
        if pc in WAITS:
            mem[0x42] = 0
        if 0xA32E <= pc < 0xA3D0:
            op = mem[pc]
            if op == 0x20:
                cur = f"jsr ${mem[pc+1] | mem[pc+2] << 8:04x} @{pc:04x}"
            elif cur.startswith("jsr") and op != 0x20:
                cur = "loop"
        b = c.processorCycles
        c.step(); steps += 1
        dc = c.processorCycles - b
        per_call[cur] += dc
        bybank[mem.bank if 0x8000 <= pc < 0xA000 else ("fix" if pc >= 0xA000 else "ram")] += dc
        tot += dc
        if steps > 3_000_000:
            raise RuntimeError(hex(pc))
    n += 1
print(f"połówek {n}, cykli CPU na obraz {tot/n:.0f}")
for k, v in per_call.most_common(30):
    print(f"  {k:24s} {v/n:8.0f}  {100*v/tot:5.1f}%")
print("banki:", {k: f"{100*v/tot:.1f}%" for k, v in bybank.most_common()})
