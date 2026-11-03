"""scene_eq8309.py REF CAND DIR [DIR...]: run `jsr $8309` (pc -> pc+3) from captured states on both ROMs; compare RAM
$0000-$7FFF (except the stack below the entry SP and the scratch list SCRATCH) and A/X/Y/SP/P. Prints cycles."""
import sys, os, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fxsim import Machine

SCRATCH = set()


def load(p):
    r = open(p, "rb").read()
    return r[16:] if r[:4] == b"CART" else r


ref, cand = load(sys.argv[1]), load(sys.argv[2])
tot = {"ref": 0, "cand": 0}; n = 0; bad = 0; scr = set()
for d in sys.argv[3:]:
    meta = json.load(open(f"{d}/meta.json"))
    for m in meta:
        img = open(f"{d}/{m['k']:05d}.in", "rb").read()
        res = {}
        for name, rom in (("ref", ref), ("cand", cand)):
            mc = Machine(rom, bytearray(img), m["bank"], m["regs"])
            tot[name] += mc.run(m["pc"], m["pc"] + 3)
            c = mc.cpu
            res[name] = (bytes(mc.mem[:0x8000]), c.a, c.x, c.y, c.sp, c.p)
        a, b = res["ref"][0], res["cand"][0]
        sp0 = m["regs"]["sp"]
        diff = [i for i in range(0x8000) if a[i] != b[i] and not (0x100 <= i <= 0x100 + sp0)]
        scr |= {i for i in diff if i in SCRATCH}
        diff = [i for i in diff if i not in SCRATCH]
        if diff or res["ref"][1:] != res["cand"][1:]:
            bad += 1
            if bad <= 10:
                print(f"{d}/{m['k']}: {len(diff)} B differ", [(hex(i), a[i], b[i]) for i in diff[:8]],
                      "regs", res["ref"][1:], res["cand"][1:])
        n += 1
print("scratch bytes that differed:", sorted(hex(i) for i in scr))
print(f"scenes {n}, mismatches {bad}; CPU cycles per jsr $8309: ref {tot['ref']/n:.0f}, cand {tot['cand']/n:.0f} "
      f"({tot['cand']-tot['ref']:+d} total, {(tot['cand']-tot['ref'])/n:+.0f}/call)")
