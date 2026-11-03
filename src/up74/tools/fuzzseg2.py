"""Segment fuzzer for the bank-5 rasteriser (extends tools/fuzzseg.py):
random segments through the REAL code from machine states captured at $982A, both ROMs from the same input,
compare RAM $0000-$7FFF INCLUDING the HD table and page-1 flags ($0100-$017F; fuzzseg.py ignores $0100-$015F),
only the stack below SP ($0180-$01FF), $B5 and the dead raster stack bytes are ignored; registers at the return
are checked for liveness by finishing the pipeline with both register sets (as fuzzseg.py).
Modes (mixed): base (as fuzzseg), small (w 1..13), edge (L/R near $2C and $D3/$D4), clamp (heights near $97),
lazy (HD set around the segment heights so the lazy-sky clear triggers often), wide (w 100..255).
Usage: fuzzseg2.py REF.rom CAND.rom SCENE_DIR N [SEED] [--hd152]"""
import sys, json, random
sys.path.insert(0, __import__("os").path.dirname(__import__("os").path.abspath(__file__)))
from fxsim import Machine
from collections import Counter

args = [a for a in sys.argv[1:] if not a.startswith("--")]
hd152 = "--hd152" in sys.argv


def load(p):
    r = open(p, "rb").read()
    return r[16:] if r[:4] == b"CART" else r


ref, cand = load(args[0]), load(args[1])
d = args[2]; N = int(args[3]); seed = int(args[4]) if len(args) > 4 else 1
rnd = random.Random(seed)
IGNORE = set(range(0x180, 0x200)) | {0xB5}
DEAD = set([0x60, 0x82, 0x84, 0x86] + list(range(0x96, 0x9F)) + list(range(0xEB, 0xF4)) + list(range(0xF5, 0xFE)))

meta = json.load(open(f"{d}/meta.json"))
snaps = []
for m in meta[:: max(1, len(meta) // 8)]:
    img = bytearray(open(f"{d}/{m['k']:05d}.in", "rb").read()); img[0x42] = 0
    if hd152:
        for y in range(0x100, 0x160):
            if img[y] == 151:
                img[y] = 152
    mc = Machine(ref, img, m["bank"], m["regs"])
    got = {}

    def tr(c):
        if not got and c.pc == 0x982A and mc.mem.bank == 2:
            got["mem"] = bytearray(mc.mem); got["sp"] = c.sp
            got["regs"] = dict(a=c.a, x=c.x, y=c.y, sp=c.sp, p=c.p)
            got["ret"] = (mc.mem[0x100 + c.sp + 1] | mc.mem[0x100 + c.sp + 2] << 8) + 1
            raise StopIteration
    try:
        mc.run(m["pc"], 0xA340 if m["pc"] == 0xA331 else 0xA37E, trace=tr)
    except StopIteration:
        got["stop"] = 0xA340 if m["pc"] == 0xA331 else 0xA37E
        snaps.append(got)
print("entry states:", len(snaps))


def run(rom, s, mem):
    mc = Machine(rom, bytearray(mem), 2, s["regs"])
    c = mc.cpu; ret = s["ret"]; sp0 = s["sp"]
    c.pc = 0x982A
    n = 0
    while not (c.pc == ret and c.sp == sp0 + 2):
        c.step(); n += 1
        if n > 3_000_000:
            raise RuntimeError("limit")
    run.last = (bytearray(mc.mem), mc.mem.bank)
    return bytes(mc.mem[:0x8000]), (c.a, c.x, c.y, c.sp, c.p), c.processorCycles


def finish(rom, s, mem, bank, regs):
    a, x, y, sp, p = regs
    mc = Machine(rom, bytearray(mem), bank, dict(a=a, x=x, y=y, sp=sp, p=p))
    mc.run(s["ret"], s["stop"])
    c = mc.cpu
    return bytes(mc.mem[:0x8000]), (c.a, c.x, c.y, c.sp, c.p)


def make(s):
    mode = rnd.choice(["base", "base", "small", "small", "edge", "clamp", "lazy", "lazy", "wide"])
    mem = bytearray(s["mem"])
    base = rnd.randint(60, 220) if mode != "clamp" else rnd.randint(135, 165)
    spread = 25 if mode != "clamp" else 10
    occ = bytearray(256)
    for x in range(256):
        init = 0x67 if (x < 0x40 or x >= 0xC4) else 0x6B
        v = base + rnd.randint(-spread, spread) if rnd.random() < 0.9 else rnd.randint(0, 255)
        if rnd.random() < 0.03 or (mode == "clamp" and rnd.random() < 0.1):
            v = 0xFF
        occ[x] = max(init, min(255, v)) if 0x2C <= x < 0xD4 else s["mem"][0x260E + x]
    if mode == "small":
        w = rnd.randint(1, 13)
    elif mode == "wide":
        w = rnd.randint(100, 255)
    else:
        w = rnd.choice([1, 2, 3, 4, 5, 6, 8, 12, 16, 24, 32, 48, 64, 96, 128, 168, 200]) + rnd.randint(0, 7)
    if mode == "edge":
        if rnd.random() < 0.5:
            x0 = rnd.randint(0x20, 0x34); x1 = min(255, x0 + w)
        else:
            x1 = rnd.randint(0xCC, 0xDC); x0 = max(0, x1 - w)
    else:
        x0 = rnd.randint(0, 255 - min(w, 254)); x1 = min(255, x0 + w)
    hL = max(0, min(255, base + rnd.randint(-80, 40))); hR = max(0, min(255, base + rnd.randint(-80, 40)))
    if mode == "clamp":
        hL = rnd.randint(130, 255); hR = rnd.randint(130, 255)
    elif rnd.random() < 0.15:
        hL = rnd.randint(0, 255); hR = rnd.randint(0, 255)
    mem[0x82], mem[0x84], mem[0x86] = x0, hL, rnd.randint(0, 255)
    mem[0x95], mem[0xEA], mem[0xF4] = x1, hR, rnd.randint(0, 255)
    mem[0x260E:0x260E + 256] = occ
    if mode in ("lazy", "clamp") or rnd.random() < 0.3:
        # HD (= 152 - first cleared row) around the heights: lazy clears trigger
        for y in list(range(3, 45)) + list(range(51, 93)):
            hd = base + rnd.randint(-30, 20)
            if rnd.random() < 0.1:
                hd = rnd.choice([108, 150, 151, 152])
            mem[0x100 + y] = max(108, min(152, hd))
    return mode, mem, (x0, hL, x1, hR)


bad = 0; cyc = [0, 0]; regdiff = Counter(); modes = Counter(); lazyn = 0
for i in range(N):
    s = rnd.choice(snaps)
    mode, mem, desc = make(s)
    modes[mode] += 1
    a, ra, ca = run(ref, s, mem)
    b, rb, cb = run(cand, s, mem)
    cyc[0] += ca; cyc[1] += cb
    diff = [k for k in range(0x8000) if a[k] != b[k] and k not in IGNORE and k not in DEAD]
    if diff:
        bad += 1
        if bad <= 8:
            print("DIFF", mode, desc, [(hex(k), a[k], b[k]) for k in diff[:8]], ra, rb)
        continue
    if ra != rb:
        for j, nm in enumerate("axysp"):
            if ra[j] != rb[j]:
                regdiff[nm] += 1
        m2, bank = run.last
        f1 = finish(cand, s, m2, bank, ra); f2 = finish(cand, s, m2, bank, rb)
        if f1[0] != f2[0] or f1[1] != f2[1]:
            fd = [k for k in range(0x8000) if f1[0][k] != f2[0][k] and k not in IGNORE]
            if fd or f1[1] != f2[1]:
                bad += 1
                print("LIVE REGS", mode, desc, ra, rb, [hex(k) for k in fd[:6]])
print(f"segments {N}, mismatches {bad}, modes {dict(modes)}, reg diffs at return {dict(regdiff)} (dead: "
      f"pipeline finished with both sets identical); cycles ref {cyc[0]/N:.0f} cand {cyc[1]/N:.0f} "
      f"({100*(cyc[1]/cyc[0]-1):+.2f}%)")
