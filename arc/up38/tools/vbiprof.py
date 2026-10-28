"""Profil VBI w symulatorze: cykle CPU na VBI, per procedura (wywołania jsr śledzone stosem), per bank.
Użycie: vbiprof.py ROM DIR [DIR...]"""
import sys, json, glob
from collections import Counter, defaultdict
from vbisim import load_scene

rom = open(sys.argv[1], "rb").read()
if rom[:4] == b"CART":
    rom = rom[16:]
excl = Counter(); incl = Counter(); calls = Counter(); n = 0; tot = 0; per = []
for d in sys.argv[2:]:
    for m in json.load(open(f"{d}/meta.json")):
        mc = load_scene(d, m, rom)
        c = mc.cpu; mem = mc.mem
        stack = [("VBI", c.processorCycles)]
        c.pc = 0xB46C
        start = c.processorCycles
        steps = 0
        while c.pc != 0xE462:
            pc = c.pc; op = mem[pc]
            b = c.processorCycles
            c.step(); steps += 1
            dc = c.processorCycles - b
            excl[stack[-1][0]] += dc
            if op == 0x20:  # jsr
                tgt = mem[pc + 1] | mem[pc + 2] << 8
                stack.append((f"${tgt:04x}", c.processorCycles)); calls[f"${tgt:04x}"] += 1
            elif op == 0x60 and len(stack) > 1:  # rts
                name, t0 = stack.pop()
                incl[name] += c.processorCycles - t0
            if steps > 300000:
                raise RuntimeError(hex(c.pc))
        cyc = c.processorCycles - start
        per.append(cyc); tot += cyc; n += 1
print(f"VBI: {n}, średnio {tot/n:.0f} cykli CPU, min {min(per)}, max {max(per)}")
print("procedura        excl/VBI  incl/VBI  wywołań/VBI")
for name, v in excl.most_common(40):
    print(f"  {name:10s} {v/n:8.0f} {incl.get(name, 0)/n:8.0f} {calls.get(name, 0)/n:6.2f}")
print("parzystość:", per[:20])
