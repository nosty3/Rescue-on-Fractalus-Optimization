"""Dokładny profil potoku w symulatorze: cykle CPU per (bank, PC), sumy per bank i per blok adresów.
Użycie: simprof.py ROM SCENES_DIR [TOP]"""
import sys, json
from paths import WORK
from collections import Counter
from fxsim import Machine

rom = open(sys.argv[1], "rb").read()
if rom[:4] == b"CART":
    rom = rom[16:]
d = sys.argv[2]
top = int(sys.argv[3]) if len(sys.argv) > 3 else 60
meta = json.load(open(f"{d}/meta.json"))
prof = Counter(); cnt = Counter(); n = 0
for m in meta:
    img = bytearray(open(f"{d}/{m['k']:05d}.in", "rb").read()); img[0x42] = 0
    mc = Machine(rom, img, m["bank"], m["regs"])
    mem = mc.mem; c = mc.cpu
    stop = 0xA340 if m["pc"] == 0xA331 else 0xA37E
    c.pc = m["pc"]
    while c.pc != stop:
        pc = c.pc
        key = (mem.bank if 0x8000 <= pc < 0xA000 else (15 if pc >= 0xA000 else -1), pc)
        before = c.processorCycles
        c.step()
        prof[key] += c.processorCycles - before
        cnt[key] += 1
    n += 1
total = sum(prof.values())
print(f"obrazów {n}, cykli CPU na obraz {total/n:.0f}")
bybank = Counter()
for (b, pc), v in prof.items():
    bybank[b] += v
print("per bank:", {b: f"{100*v/total:.1f}%" for b, v in sorted(bybank.items())})
# bloki po 64 bajty
blk = Counter()
for (b, pc), v in prof.items():
    blk[(b, pc & 0xFFC0)] += v
print("najgorętsze bloki 64 B:")
for (b, a), v in blk.most_common(40):
    print(f"  bank {b:2d} ${a:04x}-${a+63:04x} {100*v/total:5.2f}%")
print("najgorętsze instrukcje:")
for (b, pc), v in prof.most_common(top):
    print(f"  bank {b:2d} ${pc:04x} {100*v/total:5.2f}% x{cnt[(b,pc)]/n:.0f}/obraz")
json.dump({f"{b}:{pc}": [v, cnt[(b, pc)]] for (b, pc), v in prof.items()},
          open(f"{WORK}/simprof.json", "w"))
