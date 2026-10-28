"""Nagrywa obrazy pamięci na początku połówek pętli lotu ($A32E i $A36C) - do profilu całej pętli w symulatorze.
Użycie: capture_loop.py ROM OUT_DIR N SEED PRESSES"""
import sys, os, json, random
from fx import Emu

rom, out = sys.argv[1], sys.argv[2]
n_img = int(sys.argv[3]); seed = int(sys.argv[4]); presses = int(sys.argv[5])
os.makedirs(out, exist_ok=True)
rnd = random.Random(seed)
dirs = ["c", "n", "s", "e", "w", "ne", "nw", "se", "sw"]
meta = []
with Emu("pal") as e:
    a = e.a
    a.boot(rom)
    a.frame(3100 + (seed * 37) % 400)
    for _ in range(presses):
        a.joy(0, "n"); a.frame(30); a.joy(0, "c"); a.frame(30)
    a.bp_set(0xA32E); a.consol(start=True); a.frame(4000)
    a.consol(); a.bp_clear_all(); a.frame(170)
    a.bp_set(0xA32E); a.bp_set(0xA36C)
    for k in range(n_img):
        if seed and k % 2 == 0:
            a.joy(0, rnd.choice(dirs), fire=rnd.random() < 0.5)
        a.frame(400)
        r = a.regs()
        regs = {k2.lower(): int(v[1:], 16) for k2, v in r.items() if k2 in ("A", "X", "Y", "S", "P")}
        regs["sp"] = regs.pop("s")
        open(f"{out}/{k:05d}.in", "wb").write(bytes(a.memdump(0, 0x10000)))
        meta.append(dict(k=k, pc=int(r["PC"][1:], 16), regs=regs, bank=a.cart_info()["bank"], tick=a.clock()["tick"]))
json.dump(meta, open(f"{out}/meta.json", "w"))
print("captured", len(meta))
