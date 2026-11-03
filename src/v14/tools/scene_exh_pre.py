"""Exhaustive heading sweep for the scene prelude (scene_pre): 8192 heading combinations (all high bytes, low bytes
in steps of 8 plus a random fraction) x 2 random position/altitude draws, run from $8309 to $830F on both ROMs,
compare RAM $0000-$7FFF (except page 1 and the temporaries listed below, all rewritten later by banks 10-13).
Usage: scene_exh_pre.py REF.rom CAND.rom SCENE_DIR [INDEX]   (SCENE_DIR from scene_capture.py; default INDEX 5)"""
import sys, os, json, random
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fxsim import Machine
def load(p):
    r = open(p, "rb").read(); return r[16:] if r[:4] == b"CART" else r
ref, cand = load(sys.argv[1]), load(sys.argv[2])
D = sys.argv[3]; idx = int(sys.argv[4]) if len(sys.argv) > 4 else 5
meta = json.load(open(f"{D}/meta.json")); m = meta[min(idx, len(meta) - 1)]
base = open(f"{D}/{m['k']:05d}.in", "rb").read()
rnd = random.Random(5); bad = 0; n = 0
for hh in range(256):
    for hl in range(0, 256, 8):
        for rep in range(2):
            img = bytearray(base); img[0x2886] = hh; img[0x2885] = hl | rnd.randrange(8)
            for a in (0x2887, 0x2888, 0x2889, 0x288A, 0x33, 0x34, 0x23, 0x24, 0x28, 0x29):
                img[a] = rnd.choice([0, 255, rnd.randrange(256)])
            regs = dict(m["regs"]); regs["p"] = (regs["p"] & ~1) | rnd.randrange(2)
            res = []
            for rom in (ref, cand):
                mc = Machine(rom, bytearray(img), 2, regs)
                mc.cpu.sp -= 2   # as if called from the flight loop
                mc.run(0x8309, 0x830F)
                res.append((bytes(mc.mem[:0x8000]), mc.cpu.p & 0xC3))
            n += 1
            d = [i for i in range(0x8000) if res[0][0][i] != res[1][0][i] and not (0x100 <= i < 0x200) and i not in (0x2277, 0x2278, 0x2279, 0x22a4, 0x22d2, 0x2300, 0x232e)]
            if d:
                bad += 1
                if bad < 5: print(hh, hl, [(hex(i), res[0][0][i], res[1][0][i]) for i in d[:6]])
print("cases", n, "mismatches", bad)
