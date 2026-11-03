"""Fuzzing rasteryzacji na PRAWDZIWYM kodzie: losowe odcinki (L, R, fazy) i losowe occ na stanie maszyny
zrzuconym przy wejściu do $982A (bank 2), oba ROM-y od tego samego stanu do powrotu; porównanie RAM
$0000-$7FFF (poza martwymi bajtami jak w equiv.py) + A/X/Y/SP/P.
Użycie: fuzzseg.py REF.rom CAND.rom SCENE_DIR N [SEED] [--hd152]"""
import sys, json, random
from fxsim import Machine

args = [a for a in sys.argv[1:] if a != "--hd152"]
hd152 = "--hd152" in sys.argv


def load(p):
    r = open(p, "rb").read()
    return r[16:] if r[:4] == b"CART" else r


ref, cand = load(args[0]), load(args[1])
d = args[2]; N = int(args[3]); seed = int(args[4]) if len(args) > 4 else 1
rnd = random.Random(seed)
IGNORE = set(range(0x100, 0x160)) | set(range(0x180, 0x200)) | {0xB5}   # strona 1 poza HD/flagami: stos
DEAD = set([0x60, 0x82, 0x84, 0x86] + list(range(0x96, 0x9F)) + list(range(0xEB, 0xF4)) + list(range(0xF5, 0xFE)))

# 1. zrzuty stanów przy wejściu do $982A (kilka scen)
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
print("stanów wejścia:", len(snaps))


def run(rom, s, L, R, occ):
    mem = bytearray(s["mem"])
    mem[0x82], mem[0x84], mem[0x86] = L
    mem[0x95], mem[0xEA], mem[0xF4] = R
    mem[0x260E:0x260E + 256] = occ
    mc = Machine(rom, mem, 2, s["regs"])
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
    """Dokończenie potoku (do $A340/$A37E) od powrotu z rasteryzacji z danymi rejestrami."""
    a, x, y, sp, p = regs
    mc = Machine(rom, bytearray(mem), bank, dict(a=a, x=x, y=y, sp=sp, p=p))
    mc.run(s["ret"], s["stop"])
    c = mc.cpu
    return bytes(mc.mem[:0x8000]), (c.a, c.x, c.y, c.sp, c.p)


bad = 0; cyc = [0, 0]; regdiff = 0
for i in range(N):
    s = rnd.choice(snaps)
    base = rnd.randint(60, 220)
    occ = bytearray(256)
    for x in range(256):
        init = 0x67 if (x < 0x40 or x >= 0xC4) else 0x6B
        v = base + rnd.randint(-25, 25) if rnd.random() < 0.9 else rnd.randint(0, 255)
        if rnd.random() < 0.03:
            v = 0xFF
        occ[x] = max(init, min(255, v)) if 0x2C <= x < 0xD4 else s["mem"][0x260E + x]
    w = rnd.choice([1, 2, 3, 4, 5, 6, 8, 12, 16, 24, 32, 48, 64, 96, 128, 168, 200]) + rnd.randint(0, 7)
    x0 = rnd.randint(0, 255 - min(w, 254))
    x1 = min(255, x0 + w)
    hL = max(0, min(255, base + rnd.randint(-80, 40))); hR = max(0, min(255, base + rnd.randint(-80, 40)))
    if rnd.random() < 0.15:
        hL = rnd.randint(0, 255); hR = rnd.randint(0, 255)
    L = (x0, hL, rnd.randint(0, 255)); R = (x1, hR, rnd.randint(0, 255))
    a, ra, ca = run(ref, s, L, R, occ)
    b, rb, cb = run(cand, s, L, R, occ)
    cyc[0] += ca; cyc[1] += cb
    diff = [k for k in range(0x8000) if a[k] != b[k] and k not in IGNORE and k not in DEAD]
    if not diff and ra != rb:
        # rejestry/flagi różne przy powrocie: czy są martwe? ta sama pamięć (kandydata), dwa zestawy rejestrów
        regdiff += 1
        mem, bank = run.last
        f1 = finish(cand, s, mem, bank, ra); f2 = finish(cand, s, mem, bank, rb)
        if f1 == f2:
            continue
        print("REJESTRY ŻYWE", L, R, ra, rb)
        bad += 1
        if bad <= 6:
            print("RÓŻNICA", L, R, [(hex(k), a[k], b[k]) for k in diff[:6]], ra, rb)
print(f"odcinków {N}, niezgodnych {bad}, różne rejestry przy powrocie {regdiff} (martwe do końca potoku "
      f"= nie liczone jako niezgodne); cykle ref {cyc[0]/N:.0f}, cand {cyc[1]/N:.0f} "
      f"({100*(cyc[1]/cyc[0]-1):+.2f}%)")
