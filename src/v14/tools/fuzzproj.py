"""Fuzzing rzutowania (s2-proj) na PRAWDZIWYM kodzie: stan maszyny zrzucony przy wywołaniu rzutowania (bank 2
$984F, C = 0, z pętli krawędzi), losowe wejścia punktu (N1, N2, D, flagi, tabela poprawki $270E-$272D, mapa
widoczności, stare $AE-$B2/$B5/$9F), oba ROM-y od tego samego stanu do powrotu (rts do wołającego).
Porównanie: RAM $0000-$7FFF (poza $9F: martwy, i stosem poniżej SP) + X + bank. A/Y/P przy powrocie martwe
(wołający: ldy $272e / ldx ...; pre: pla/tay), liczone osobno.
Użycie: fuzzproj.py REF.rom CAND.rom SCENE_DIR N [SEED]"""
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
for m in meta[:: max(1, len(meta) // 6)]:
    img = bytearray(open(f"{d}/{m['k']:05d}.in", "rb").read()); img[0x42] = 0
    for y in range(0x100, 0x160):
        if img[y] == 151:
            img[y] = 152
    mc = Machine(ref, img, m["bank"], m["regs"])
    got = []

    def tr(c):
        if c.pc == 0x984F and mc.mem.bank == 2 and not (c.p & 1) and len(got) < 3:
            ret = (mc.mem[0x100 + c.sp + 1] | mc.mem[0x100 + c.sp + 2] << 8) + 1
            got.append(dict(mem=bytearray(mc.mem), regs=dict(a=c.a, x=c.x, y=c.y, sp=c.sp, p=c.p), ret=ret))
    mc.run(m["pc"], 0xA340 if m["pc"] == 0xA331 else 0xA37E, trace=tr)
    snaps += got
print("stanów wejścia:", len(snaps))


def rnd16(D):
    r = rnd.random()
    if r < 0.30:
        v = rnd.randint(0, max(0, D - 1)) if D else 0
    elif r < 0.55:
        k = rnd.randint(0, 9)
        v = (D << k) + rnd.randint(-3, 3) if D else rnd.randint(0, 255)
    elif r < 0.75:
        v = rnd.randint(0, 0xFFFF)
    elif r < 0.85:
        v = rnd.choice([0, 1, 0x7FFF, 0x8000, 0xFFFF, D, D - 1, D + 1, 2 * D, 2 * D - 1])
    else:
        v = rnd.randint(0, 0x7FF)
    v &= 0xFFFF
    if rnd.random() < 0.5:
        v = (-v) & 0xFFFF
    return v


def rndD():
    r = rnd.random()
    if r < 0.45:
        return rnd.randint(64, 11400)
    if r < 0.65:
        return rnd.randint(0, 255)
    if r < 0.85:
        return rnd.randint(0, 0x7FFF)
    return rnd.choice([0, 1, 2, 0x100, 0xFF, 0x7FFF, 0x4000, 0x2000, 0x1FFF])


def run(rom, s, mem):
    mc = Machine(rom, bytearray(mem), 2, s["regs"])
    c = mc.cpu; ret = s["ret"]; sp0 = s["regs"]["sp"]
    c.pc = 0x984F
    n = 0
    while not (c.pc == ret and c.sp == (sp0 + 2) & 0xFF):
        c.step(); n += 1
        if n > 2_000_000:
            raise RuntimeError("limit")
    return bytes(mc.mem[:0x8000]), (c.a, c.x, c.y, c.sp, c.p), mc.mem.bank, c.processorCycles


bad = 0; regd = 0; cyc = [0, 0]; rare = 0
for t in range(N):
    s = rnd.choice(snaps)
    mem = bytearray(s["mem"])
    x = rnd.randint(0, 44) if rnd.random() < 0.7 else s["regs"]["x"]
    s = dict(s); s["regs"] = dict(s["regs"]); s["regs"]["x"] = x
    s["regs"]["p"] &= 0xFE  # C = 0 (jak wołający)
    D = rndD()
    n1, n2 = rnd16(D), rnd16(D)
    mem[0x2300 + x], mem[0x232E + x] = D & 255, D >> 8
    mem[0x22A4 + x], mem[0x22D2 + x] = n1 & 255, n1 >> 8
    mem[0x235B + x], mem[0x2388 + x] = n2 & 255, n2 >> 8
    mem[0x24B4 + x] = rnd.randint(0, 255) & 0xEF if rnd.random() < 0.8 else rnd.randint(0, 255)
    for a in (0x2400, 0x242D, 0x245A, 0x2487):
        mem[a + x] = rnd.randint(0, 255)
    for a in list(range(0xAE, 0xB3)) + [0xB5, 0x9F]:
        mem[a] = rnd.randint(0, 255)
    if rnd.random() < 0.7:
        for k in range(32):
            mem[0x270E + k] = rnd.randint(0, 255) if rnd.random() < 0.5 else rnd.randint(0, 40)
    cell = mem[0x2276 + x]
    if rnd.random() < 0.1:
        mem[0x0A00 + cell] = rnd.randint(1, 255); rare += 1
    else:
        mem[0x0A00 + cell] = 0
    a, ra, ba, ca = run(ref, s, mem)
    b, rb, bb, cb = run(cand, s, mem)
    cyc[0] += ca; cyc[1] += cb
    sp = ra[3]
    diff = [k for k in range(0x8000) if a[k] != b[k] and k != 0x9F and not (0x100 <= k <= 0x100 + sp)]
    if diff or ra[1] != rb[1] or ba != bb or ra[3] != rb[3]:
        bad += 1
        if bad <= 8:
            print("RÓŻNICA x", x, "D", hex(D), "N1", hex(n1), "N2", hex(n2), [(hex(k), a[k], b[k]) for k in diff[:8]],
                  "rej", ra, rb, "bank", ba, bb)
    elif ra != rb:
        regd += 1
print(f"prób {N}, niezgodnych {bad}, inne A/Y/P (martwe) {regd}, rzadka widoczność {rare}; "
      f"cykle ref {cyc[0]/N:.0f}, cand {cyc[1]/N:.0f}")
