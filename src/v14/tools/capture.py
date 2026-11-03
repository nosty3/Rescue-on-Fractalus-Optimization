"""Nagrywa sceny z prawdziwego lotu w Altirrze: pełny obraz pamięci (64 KB) + rejestry + bank na wejściu
każdej połówki pętli lotu (przed `ldx` kasowania: $A331 i $A36F) i bufor po fillu ($A340/$A37E).
Użycie: capture.py ROM OUT_DIR N_OBRAZÓW SEED PRESSES
  SEED 0 = neutralny lot (jak benchmark), inaczej losowe sterowanie + strzelanie; PRESSES = poziom w menu."""
import sys, os, json, random
from fx import Emu

rom, out = sys.argv[1], sys.argv[2]
n_img = int(sys.argv[3]); seed = int(sys.argv[4]); presses = int(sys.argv[5])
skip = int(sys.argv[6]) if len(sys.argv) > 6 else 0
menu = int(sys.argv[7]) if len(sys.argv) > 7 else None
os.makedirs(out, exist_ok=True)
rnd = random.Random(seed)
dirs = ["c", "n", "s", "e", "w", "ne", "nw", "se", "sw"]
meta = []
with Emu("pal") as e:
    a = e.a
    a.boot(rom)
    a.frame(menu if menu else 3100 + (seed * 37) % 400)
    for _ in range(presses):
        a.joy(0, "n"); a.frame(30); a.joy(0, "c"); a.frame(30)
    a.bp_set(0xA32E); a.consol(start=True); a.frame(4000)
    assert a.regs()["PC"] == "$a32e", a.regs()
    a.consol(); a.bp_clear_all()
    a.frame(170 + skip)
    for bp in (0xA331, 0xA36F, 0xA340, 0xA37E):
        a.bp_set(bp)
    k = 0; pending = None; stops = 0
    while k < n_img and stops < n_img * 4:
        stops += 1
        if seed and stops % 6 == 0:
            a.joy(0, rnd.choice(dirs), fire=rnd.random() < 0.5)
        a.frame(400)
        r = a.regs()
        pc = int(r["PC"][1:], 16)
        if pc in (0xA331, 0xA36F):
            img = bytes(a.memdump(0, 0x10000))
            regs = {k2.lower(): int(v[1:], 16) for k2, v in r.items() if k2 in ("A", "X", "Y", "S", "P")}
            regs["sp"] = regs.pop("s")
            pending = dict(k=k, pc=pc, regs=regs, bank=a.cart_info()["bank"], mode=img[0x4A],
                           tick=a.clock()["tick"])
            open(f"{out}/{k:05d}.in", "wb").write(img)
        elif pending and pc == (0xA340 if pending["pc"] == 0xA331 else 0xA37E):
            open(f"{out}/{k:05d}.buf", "wb").write(bytes(a.memdump(0x1010, 96 * 48)))
            meta.append(pending); pending = None; k += 1
json.dump(meta, open(f"{out}/meta.json", "w"), indent=0)
print("captured", k)
