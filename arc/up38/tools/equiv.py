"""Równoważność potoku (kasowanie + góry + fill, od `ldx` przed jsr $9214 do po fillu) dwóch ROM-ów
w symulatorze: cały RAM $0000-$7FFF po potoku musi być identyczny (poza listą IGNORE).
Wypisuje różnice i średnie cykle CPU obu wersji.
Użycie: equiv.py REF.rom CAND.rom SCENES_DIR [SCENES_DIR...]"""
import sys, json
from fxsim import Machine

IGNORE = set(range(0x100, 0x200))  # stos: martwe bajty poniżej SP mogą się różnić
IGNORE |= {0xB5}                   # scratch rasteryzacji (nosty3: martwy po rendererze)


def load(p):
    r = open(p, "rb").read()
    return r[16:] if r[:4] == b"CART" else r


# Pozostałości programowego stosu rasteryzacji po pominiętych poddrzewach: martwe (liveness.py: po potoku
# nikt ich nie czyta przed zapisem poza $9F; vbi_reads.py: VBI ich nie czyta). $9F celowo NIE na liście.
DEAD = set([0x82, 0x84, 0x86] + list(range(0x96, 0x9F)) + list(range(0xEB, 0xF4)) + list(range(0xF5, 0xFE)))
ALLDIFF = set()
ref, cand = load(sys.argv[1]), load(sys.argv[2])
tot = {"ref": 0, "cand": 0}; n = 0; bad = 0
for d in sys.argv[3:]:
    meta = json.load(open(f"{d}/meta.json"))
    for m in meta:
        img = bytearray(open(f"{d}/{m['k']:05d}.in", "rb").read()); img[0x42] = 0
        stop = 0xA340 if m["pc"] == 0xA331 else 0xA37E
        res = {}
        for name, rom in (("ref", ref), ("cand", cand)):
            mc = Machine(rom, bytearray(img), m["bank"], m["regs"])
            tot[name] += mc.run(m["pc"], stop)
            res[name] = (bytes(mc.mem[:0x8000]), mc.cpu.a, mc.cpu.x, mc.cpu.y, mc.cpu.sp)
        a, b = res["ref"][0], res["cand"][0]
        diff = [i for i in range(0x8000) if a[i] != b[i] and i not in IGNORE]
        ALLDIFF.update(diff)
        diff = [i for i in diff if i not in DEAD]
        if diff or res["ref"][1:] != res["cand"][1:]:
            bad += 1
            if bad <= 8:
                print(f"{d.split('/')[-1]}/{m['k']}: {len(diff)} bajtów różnych, np.",
                      [(hex(i), a[i], b[i]) for i in diff[:6]], "rej", res["ref"][1:], res["cand"][1:])
        n += 1
print("wszystkie różniące się adresy:", sorted(hex(a) for a in ALLDIFF))
print(f"scen {n}, niezgodnych {bad}; cykle CPU/obraz: ref {tot['ref']/n:.0f}, cand {tot['cand']/n:.0f} "
      f"({100*(tot['cand']/tot['ref']-1):+.2f}%)")
