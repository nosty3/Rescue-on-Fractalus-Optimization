"""Fuzzer of the unrolled post-pass of jsr $8309 (scene_pre: bank 2 $8055, entered from the exit of banks 10-13 at
$98E7): random classification flags $24B4+k, z bytes $2300/$232E+k, $B5, $28DB, P and A on the stack, run to $A331
on both ROMs, compare RAM $0000-$7FFF (except the stack below SP) and A/X/Y/SP/P.
Usage: scene_post_fuzz.py REF.rom CAND.rom N SCENE_DIR [INDEX]   (default INDEX 7)"""
import sys, os, json, random
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fxsim import Machine
def load(p):
    r = open(p, "rb").read(); return r[16:] if r[:4] == b"CART" else r
ref, cand = load(sys.argv[1]), load(sys.argv[2]); N = int(sys.argv[3])
D = sys.argv[4]; idx = int(sys.argv[5]) if len(sys.argv) > 5 else 7
meta = json.load(open(f"{D}/meta.json")); m = meta[min(idx, len(meta) - 1)]
base = open(f"{D}/{m['k']:05d}.in", "rb").read()
rnd = random.Random(9); bad = 0; mods = 0
for i in range(N):
    img = bytearray(base)
    for k in range(6):
        img[0x24B4 + k] = rnd.choice([0, 0x20, 0x40, 0x80, 0, 0x80])
        img[0x232E + k] = rnd.randrange(256); img[0x2300 + k] = rnd.randrange(256)
    for a in (0xB5, 0x28DB): img[a] = rnd.randrange(256)
    sp = 0xF0; P = rnd.randrange(256) | 0x30; Aval = rnd.randrange(256)
    img[0x100 + sp] = 0xA3; img[0x100 + sp - 1] = 0x30          # return -> $A331
    img[0x100 + sp - 2] = P; img[0x100 + sp - 3] = Aval          # php / pha of the exit stub
    res = []
    for rom in (ref, cand):
        mc = Machine(rom, bytearray(img), 2, dict(a=0, x=rnd.randrange(256), y=0x2D, sp=sp - 4, p=0x30))
        mc.run(0x98E7, 0xA331)
        c = mc.cpu; res.append((bytes(mc.mem[:0x8000]), c.a, c.x, c.y, c.sp, c.p))
    d = [x for x in range(0x8000) if res[0][0][x] != res[1][0][x] and not (0x100 <= x < 0x100 + sp - 3)]
    if res[0][0][0x2300:0x2306] != bytes(img[0x2300:0x2306]): mods += 1
    if d or res[0][1:] != res[1][1:]:
        bad += 1
        if bad < 5: print(i, [(hex(x), res[0][0][x], res[1][0][x]) for x in d[:6]], res[0][1:], res[1][1:])
print("cases", N, "with modifications", mods, "mismatches", bad)
