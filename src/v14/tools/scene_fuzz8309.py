"""scene_fuzz8309.py REF CAND DIR N [SEED]: random inputs to jsr $8309 on captured states: heading $2885/$2886, position
$2887-$288A, altitude $33/$34 (incl. 0, $3F.., >= $40), heightmap page $0900, and $9f/$b4-$b6/$80/$81/carry.
Compares RAM $0000-$7FFF (except stack below SP and scratch) + A/X/Y/SP/P. Reports banks (variants) covered."""
import sys, os, json, random, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fxsim import Machine

SCRATCH = set()


def load(p):
    r = open(p, "rb").read()
    return r[16:] if r[:4] == b"CART" else r


ref, cand = load(sys.argv[1]), load(sys.argv[2])
d = sys.argv[3]; N = int(sys.argv[4]); rnd = random.Random(int(sys.argv[5]) if len(sys.argv) > 5 else 1)
meta = json.load(open(f"{d}/meta.json"))
imgs = {}
bad = 0; banks = collections.Counter(); cyc = [0, 0]
for i in range(N):
    m = rnd.choice(meta)
    if m["k"] not in imgs:
        imgs[m["k"]] = open(f"{d}/{m['k']:05d}.in", "rb").read()
    img = bytearray(imgs[m["k"]])
    for a in (0x2885, 0x2886, 0x2887, 0x2888, 0x2889, 0x288A):
        img[a] = rnd.randrange(256)
    r = rnd.random()
    if r < 0.15:
        img[0x33], img[0x34] = rnd.choice([0, 0x40, 0x80, 0xC0]), 0          # $8b = 0 cases
    elif r < 0.3:
        img[0x33], img[0x34] = rnd.randrange(256), rnd.randrange(0x40, 0x100)  # $8c = $ff
    elif r < 0.4:
        img[0x33], img[0x34] = 0, 0
    else:
        img[0x33], img[0x34] = rnd.randrange(256), rnd.randrange(0x40)
    if rnd.random() < 0.5:
        for a in range(0x900, 0xA00):
            img[a] = rnd.randrange(256)
    for a in (0x9F, 0xB4, 0xB5, 0xB6):
        if rnd.random() < 0.3:
            img[a] = rnd.randrange(256)
    regs = dict(m["regs"]); regs["p"] = (regs["p"] & ~1) | rnd.randrange(2)
    res = {}
    for j, (name, rom) in enumerate((("ref", ref), ("cand", cand))):
        mc = Machine(rom, bytearray(img), m["bank"], regs)
        seen = []
        cyc[j] += mc.run(m["pc"], m["pc"] + 3, trace=(lambda c, mc=mc, seen=seen: seen.append(mc.mem.bank) if c.pc == 0x9893 else None))
        c = mc.cpu
        res[name] = (bytes(mc.mem[:0x8000]), c.a, c.x, c.y, c.sp, c.p)
        if name == "ref":
            banks[tuple(seen)] += 1
    a, b = res["ref"][0], res["cand"][0]
    sp0 = regs["sp"]
    diff = [x for x in range(0x8000) if a[x] != b[x] and not (0x100 <= x <= 0x100 + sp0) and x not in SCRATCH]
    if diff or res["ref"][1:] != res["cand"][1:]:
        bad += 1
        if bad <= 10:
            print(f"case {i} scene {m['k']}: {len(diff)} B", [(hex(x), a[x], b[x]) for x in diff[:8]],
                  res["ref"][1:], res["cand"][1:], "alt", img[0x33], img[0x34])
print("variants (bank at $9893):", dict(banks))
print(f"cases {N}, mismatches {bad}; cycles ref {cyc[0]/N:.0f} cand {cyc[1]/N:.0f}")
