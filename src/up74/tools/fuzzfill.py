"""Fuzzer fillu (bank 9): losowe bufory + HD + flagi na wejściu, sam fill ($930D bank 9 -> $9FF0) na dwóch ROM-ach,
porównanie całego RAM-u $0000-$7FFF (poza martwym scratchem DEAD i stosem poniżej SP), rejestrów A X Y SP i P.
Treść kolumn: (a) w pełni losowe bajty (dowolne piksele 00/01/10/11), (b) kolumny "jak z rasteryzacji"
(niebo $55 nad D, zera, grzbiet 10, ciało 00/10), z dodatkami: bajty paska VBI w wierszu 46 ($55 $D5 $F5 $FD
$FF $7F), piksele obiektów w dowolnym kolorze, wiersz 0 niezerowy, wiersz 48 różny od $FF (ścieżka >= 49).
Tablice $3A00/$3B00/$073D/$0793 bierze ze sceny (standardowe, jak w locie).
Użycie: fuzzfill.py REF.rom CAND.rom N [SEED] [SCENE.in]"""
import sys, random
from fxsim import Machine
from paths import WORK

DEAD = set([0x82, 0x84, 0x86] + list(range(0x96, 0x9F)) + list(range(0xEB, 0xF4)) + list(range(0xF5, 0xFE)))


def load(p):
    r = open(p, "rb").read()
    return r[16:] if r[:4] == b"CART" else r


ref, cand = load(sys.argv[1]), load(sys.argv[2])
N = int(sys.argv[3]); seed = int(sys.argv[4]) if len(sys.argv) > 4 else 1
base = bytearray(open(sys.argv[5] if len(sys.argv) > 5 else f"{WORK}/scenes/f_n/00000.in", "rb").read())
rnd = random.Random(seed)
VBI = [0x55, 0xD5, 0xF5, 0xFD, 0xFF, 0x7F]


def column(y, img, kind):
    """Wypełnia kolumnę bajtową y wierszy 0..48 i HD[y]."""
    HD = rnd.choice([108, 109, 151, 152] + [rnd.randint(108, 152)] * 6)
    D = 152 - HD
    if kind == "random":
        for r in range(48):
            img[0x1010 + 96 * r + y] = rnd.choice([0, 0, rnd.randint(0, 255)])
    else:
        ridge = []
        for i in range(4):
            c = rnd.random()
            if c < 0.08:
                ridge.append(48)              # brak grzbietu
            elif c < 0.2:
                ridge.append(0)               # klamra $FF -> wiersz 0
            else:
                ridge.append(rnd.randint(max(D, 1), 47))
        for r in range(48):
            v = 0
            for i in range(4):
                sh = 6 - 2 * i
                if 0 < r < D:
                    p = 1                     # niebo
                elif r < ridge[i] or (r == 0 and ridge[i] != 0):
                    p = 0
                elif r == ridge[i]:
                    p = 2
                else:
                    p = rnd.choice([0, 0, 0, 2])
                v |= p << sh
            img[0x1010 + 96 * r + y] = v
        if rnd.random() < 0.15:               # pasek VBI w wierszu 46
            img[0x1010 + 96 * 46 + y] = rnd.choice(VBI)
        for _ in range(rnd.choice([0, 0, 0, 1, 2])):   # piksele obiektów (dowolny kolor, w tym 01/11)
            r = rnd.randint(1, 47); sh = 2 * rnd.randint(0, 3)
            a = 0x1010 + 96 * r + y
            img[a] = (img[a] & ~(3 << sh) & 0xFF) | (rnd.randint(1, 3) << sh)
    img[0x2210 + y] = 0xFF if rnd.random() < 0.9 else rnd.randint(0, 255)
    if rnd.random() < 0.9:                    # wiersze 49+ (tylko ścieżka gen49)
        for r in range(49, 52):
            img[0x1010 + 96 * r + y] = rnd.randint(0, 255)
    img[0x100 + y] = HD


bad = 0; cyc = {"ref": 0, "cand": 0}
for t in range(N):
    img = bytearray(base)
    x0 = rnd.choice([3, 51])
    kind = rnd.choice(["random", "ridge", "ridge", "ridge"])
    for c in range(42):
        column(x0 + c, img, kind if rnd.random() < 0.9 else rnd.choice(["random", "ridge"]))
    img[0x4A] = rnd.choice([2, 2, 0, 1])
    for a in (0x80, 0x81, 0x95, 0x9F):
        img[a] = rnd.randint(0, 255)
    regs = {"a": rnd.randint(0, 255), "x": x0, "y": rnd.randint(0, 255), "sp": 0xF0,
            "p": 0x30 | rnd.choice([0, 1]) | (rnd.choice([0, 0x40])) | (rnd.choice([0, 0x80])) | rnd.choice([0, 2])}
    res = {}
    for name, rom in (("ref", ref), ("cand", cand)):
        mc = Machine(rom, bytearray(img), 9, regs)
        c = mc.cpu; c.pc = 0x930D; n = 0; t0 = c.processorCycles
        while not (c.pc == 0x9FF0 and mc.mem.bank == 9):
            c.step(); n += 1
            if n > 300000:
                raise RuntimeError(f"{name}: brak końca, PC={c.pc:04x}")
        cyc[name] += c.processorCycles - t0
        sp = c.sp
        ign = set(range(0x100 + sp + 1 - 8, 0x200)) | DEAD   # stos (powrót jsr itp.) poniżej/obok SP
        res[name] = (bytes(mc.mem[:0x8000]), c.a, c.x, c.y, c.sp, c.p, ign)
    a, b = res["ref"][0], res["cand"][0]
    ign = res["ref"][6] | res["cand"][6]
    diff = [i for i in range(0x8000) if a[i] != b[i] and i not in ign]
    if diff or res["ref"][1:6] != res["cand"][1:6]:
        bad += 1
        if bad <= 10:
            print(f"próba {t} ({kind}, x0={x0}): {len(diff)} B", [(hex(i), a[i], b[i]) for i in diff[:8]],
                  "rej", res["ref"][1:6], res["cand"][1:6], flush=True)
    if (t + 1) % 500 == 0:
        print(f"  {t + 1} prób, niezgodnych {bad}", flush=True)
print(f"prób {N}, niezgodnych {bad}; cykle fillu: ref {cyc['ref']/N:.0f} cand {cyc['cand']/N:.0f}")
