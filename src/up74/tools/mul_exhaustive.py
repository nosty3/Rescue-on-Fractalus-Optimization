"""Exhaustive test of the vbi2_mul patch: original multiply $7CD6 (resident code of REF) vs new $7F4B (CAND: bank 7
tables + resident code) for all 65536 pairs (M = $6B, N = $28D6). Compares A, $6B and the bank after the return.
The machine image comes from a captured VBI state (capture_vbi.py / capture_vbi2.py); the resident code bytes in
which the two ROMs differ are written into the image from CAND (the original $7CD6 is untouched by the patch).
Usage: mul_exhaustive.py REF.rom CAND.rom VBI_SCENE_DIR"""
import sys, os, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from vbisim import VbiMachine  # noqa: E402


def load(p):
    r = open(p, "rb").read()
    return r[16:] if r[:4] == b"CART" else r


base, cand = load(sys.argv[1]), load(sys.argv[2])
d = sys.argv[3]
m = json.load(open(f"{d}/meta.json"))[0]
img = bytearray(open(f"{d}/{m['k']:05d}.in", "rb").read())
for i in range(0x4000):
    if base[i] != cand[i]:
        img[0x4000 + i] = cand[i]


def run(rom, entry, M, N):
    mc = VbiMachine(rom, bytearray(img), 2, {"a": 0x55, "x": 0x66, "y": 0x77, "sp": 0xF0, "p": 0x30})
    mem = mc.mem; c = mc.cpu
    mem[0x6B] = M; mem[0x28D6] = N
    mem[0x1F0] = 0x7C; mem[0x1EF] = 0x9D; c.sp = 0xEE   # as if called by jsr at $7C9B (rts -> $7C9E)
    c.pc = entry; c0 = c.processorCycles; n = 0
    while c.pc != 0x7C9E:
        c.step(); n += 1
        assert n < 2000
    return c.a, mem[0x6B], mem.bank, c.processorCycles - c0


bad = 0; ca = 0; cb = 0
for M in range(256):
    for N in range(256):
        a1 = run(base, 0x7CD6, M, N)
        a2 = run(cand, 0x7F4B, M, N)
        ca += a1[3]; cb += a2[3]
        if a1[:3] != a2[:3]:
            bad += 1
            if bad < 10:
                print("DIFF", M, N, a1, a2)
print("pairs 65536, mismatches", bad, "avg cycles", ca / 65536, "->", cb / 65536)
