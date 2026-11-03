"""Fuzzing pętli krawędzi (s2-proj) na PRAWDZIWYM kodzie: stan maszyny przy wejściu do pętli (bank 2 $85D4, po
prologu), losowe flagi $24B4 wszystkich 45 punktów (bity 7/6/5 z różnym nasyceniem, bit 4 = już rzutowany), losowe
współrzędne rzutowanych punktów (hi zwykle 0, czasem nie: ścieżka ogólna clipu; progi $6C i $D8, x1 >= x2),
losowe N/D nierzutowanych, fazy. Oba ROM-y od tego samego stanu do $88E8 (koniec pętli; rasteryzacja i clip
w środku na prawdziwym kodzie). Porównanie: RAM $0000-$7FFF (poza $9F: martwy, stos $0180-$01FF) + A/X/Y/SP;
P osobno (różnice tylko liczone).
Użycie: fuzzloop.py REF.rom CAND.rom SCENE_DIR N [SEED]"""
import sys, json, random
from fxsim import Machine


def load(p):
    r = open(p, "rb").read()
    return r[16:] if r[:4] == b"CART" else r


ref, cand = load(sys.argv[1]), load(sys.argv[2])
d = sys.argv[3]; N = int(sys.argv[4]); seed = int(sys.argv[5]) if len(sys.argv) > 5 else 1
rnd = random.Random(seed)

meta = json.load(open(f"{d}/meta.json"))
snaps = []
for m in meta[:: max(1, len(meta) // 8)]:
    img = bytearray(open(f"{d}/{m['k']:05d}.in", "rb").read()); img[0x42] = 0
    for y in range(0x100, 0x160):
        if img[y] == 151:
            img[y] = 152
    mc = Machine(ref, img, m["bank"], m["regs"])
    got = {}

    def tr(c):
        if not got and c.pc == 0x85D4 and mc.mem.bank == 2:
            got.update(mem=bytearray(mc.mem), regs=dict(a=c.a, x=c.x, y=c.y, sp=c.sp, p=c.p))
            raise StopIteration
    try:
        mc.run(m["pc"], 0xA340 if m["pc"] == 0xA331 else 0xA37E, trace=tr)
    except StopIteration:
        snaps.append(dict(got))
print("stanów wejścia:", len(snaps))
IGN = {0x9F} | set(range(0x180, 0x200))


def run(rom, s, mem):
    mc = Machine(rom, bytearray(mem), 2, s["regs"])
    c = mc.cpu
    c.pc = 0x85D4
    n = 0
    while not (c.pc == 0x88E8 and mc.mem.bank == 2):
        c.step(); n += 1
        if n > 4_000_000:
            raise RuntimeError("limit")
    return bytes(mc.mem[:0x8000]), (c.a, c.x, c.y, c.sp), c.p, c.processorCycles


def coord(lo_center, spread):
    v = lo_center + rnd.randint(-spread, spread)
    r = rnd.random()
    if r < 0.12:
        v = rnd.choice([-1, 1]) * rnd.randint(256, 12000) + lo_center
    elif r < 0.15:
        v = rnd.choice([0x4000, -0x4000])
    return v & 0xFFFF


bad = 0; pd = 0; pbits = {}; cyc = [0, 0]; modes = {}
for t in range(N):
    s = rnd.choice(snaps)
    mem = bytearray(s["mem"])
    mode = rnd.choice(["none", "p1only", "rand", "rand", "rand", "dense", "lastfew"])
    modes[mode] = modes.get(mode, 0) + 1
    for x in range(45):
        f = rnd.randint(0, 255)
        if mode == "none":
            f |= rnd.choice([0x80, 0x20, 0xA0])
        elif mode == "p1only":
            f = (f & 0x1F) | rnd.choice([0x40, 0xC0, 0x40, 0x00]) if rnd.random() < 0.8 else f
        elif mode == "dense":
            f &= 0x1F if rnd.random() < 0.85 else 0xFF
        elif mode == "lastfew":
            f = (f | 0x80) if x < 30 else (f & (0x1F if rnd.random() < 0.7 else 0xFF))
        else:
            f &= (0x1F if rnd.random() < 0.6 else 0xFF)
        if rnd.random() < 0.6:
            f |= 0x10
        mem[0x24B4 + x] = f
        X = coord(rnd.choice([0x30, 0x80, 0xC0, 0xD8]), 40)
        Y = coord(rnd.choice([0x6C, 0x40, 0x90, 0x6C]), 30)
        mem[0x2400 + x], mem[0x242D + x] = X & 255, X >> 8
        mem[0x245A + x], mem[0x2487 + x] = Y & 255, Y >> 8
        mem[0x23B5 + x] = rnd.randint(0, 255)
        if rnd.random() < 0.3:
            D = rnd.randint(64, 11000)
            mem[0x2300 + x], mem[0x232E + x] = D & 255, D >> 8
            for a in (0x22A4, 0x235B):
                v = rnd.randint(-D * 3, D * 3) & 0xFFFF
                mem[a + x], mem[a + 0x2E + x] = v & 255, v >> 8
    mem[0x272E] = rnd.randint(0, 255)
    a, ra, pa, ca = run(ref, s, mem)
    b, rb, pb, cb = run(cand, s, mem)
    cyc[0] += ca; cyc[1] += cb
    diff = [k for k in range(0x8000) if a[k] != b[k] and k not in IGN]
    if diff or ra != rb:
        bad += 1
        if bad <= 8:
            print("RÓŻNICA", mode, [(hex(k), a[k], b[k]) for k in diff[:8]], "rej", ra, rb)
    if pa != pb:
        pd += 1
        pbits[pa ^ pb] = pbits.get(pa ^ pb, 0) + 1
print(f"prób {N} {modes}, niezgodnych {bad}, różne P {pd} (bity xor: {pbits}); cykle ref {cyc[0]/N:.0f}, cand {cyc[1]/N:.0f}")
