"""Równoważność potoku z pracą w czasie czekania na promień (s2-reorder): jak equiv.py (okno od `ldx` przed
jsr $9214 do po fillu, cały RAM $0000-$7FFF + A/X/Y/SP/P), ale kandydat startuje z obrazem jeszcze NIE gotowym
($42 = 2, VCOUNT $D40B = 0 < 74), więc pętla czekania w `pre` (bank 2) wykonuje kroki pracy (rzutowanie par
krawędzi). Po N przejściach przez początek pętli (`wl`) symulator zeruje $42 (jak VBI, które przełącza obraz) i
pętla kończy się. Dla każdej sceny kandydat liczony dla wielu N (0 = gotowe od razu ... dużo = cała lista par),
REF raz (oryginalny wait_beam z $42 = 0; jego wynik nie zależy od długości czekania: pętla tylko czyta).
Okno zaczyna się przed jsr $9214, więc obejmuje cały przeniesiony kod (prolog tablic, rzutowanie w czekaniu).
Użycie: equivwait.py [--hd152] [--n=0,1,2,...] REF.rom CAND.rom SCENES_DIR [SCENES_DIR...]"""
import sys, json, collections
from fxsim import Machine

# jak equiv.py (tam liczone przy imporcie, więc kopia): pozostałości programowego stosu rasteryzacji, martwe
DEAD = set([0x82, 0x84, 0x86] + list(range(0x96, 0x9F)) + list(range(0xEB, 0xF4)) + list(range(0xF5, 0xFE)))
WL, TRY_PROJ, RARE = 0x87E9, 0x8838, 0x883E


def load(p):
    r = open(p, "rb").read()
    return r[16:] if r[:4] == b"CART" else r


def run(rom, img, m, stop, n_ready=None):
    mc = Machine(rom, bytearray(img), m["bank"], m["regs"])
    mem = mc.mem; c = mc.cpu; step = c.step
    stats = collections.Counter()
    if n_ready is None:
        mem[0x42] = 0
        cyc = mc.run(m["pc"], stop)
    else:
        mem[0x42] = 2
        bytearray.__setitem__(mem, 0xD40B, 0)
        c.pc = m["pc"]; start = c.processorCycles; k = 0
        while c.pc != stop:
            pc = c.pc
            if mem.bank == 2:
                if pc == WL:
                    k += 1
                    if k > n_ready:
                        mem[0x42] = 0
                elif pc == TRY_PROJ:
                    stats["proj"] += 1
                elif pc == RARE:
                    stats["rare"] += 1
            step()
            stats["steps"] += 1
            if stats["steps"] > 5_000_000:
                raise RuntimeError("limit")
        cyc = c.processorCycles - start
        stats["wl"] = k
    return (bytes(mem[:0x8000]), c.a, c.x, c.y, c.sp, c.p), cyc, stats


def main():
    args = sys.argv[1:]
    hd152 = "--hd152" in args
    ns = [0, 1, 2, 3, 4, 6, 8, 12, 16, 24, 32, 48, 72, 200]
    for a in args:
        if a.startswith("--n="):
            ns = [int(x) for x in a[4:].split(",")]
    args = [a for a in args if not a.startswith("--")]
    ignore = set(range(0x180, 0x200)) | {0xB5}
    ref, cand = load(args[0]), load(args[1])
    n = bad = runs = 0; tot = collections.Counter(); alldiff = set()
    for d in args[2:]:
        for m in json.load(open(f"{d}/meta.json")):
            img = bytearray(open(f"{d}/{m['k']:05d}.in", "rb").read())
            if hd152:
                for y in range(0x100, 0x160):
                    if img[y] == 151:
                        img[y] = 152
            stop = 0xA340 if m["pc"] == 0xA331 else 0xA37E
            r, _, _ = run(ref, img, m, stop)
            maxproj = 0
            for nr in ns:
                c, _, st = run(cand, img, m, stop, nr)
                tot["proj"] += st["proj"]; tot["rare"] += st["rare"]; maxproj = max(maxproj, st["proj"])
                diff = [i for i in range(0x8000) if r[0][i] != c[0][i] and i not in ignore]
                alldiff.update(diff)
                diff = [i for i in diff if i not in DEAD]
                runs += 1
                if diff or r[1:] != c[1:]:
                    bad += 1
                    if bad <= 10:
                        print(f"{d.split('/')[-1]}/{m['k']} N={nr}: {len(diff)} B, np.",
                              [(hex(i), r[0][i], c[0][i]) for i in diff[:6]], "rej", r[1:], c[1:], dict(st))
            tot["maxproj"] += maxproj
            n += 1
    print("różniące się adresy (z martwymi):", sorted(hex(a) for a in alldiff))
    print(f"scen {n}, przebiegów kandydata {runs}, niezgodnych {bad}; rzutowań w czekaniu {tot['proj']}, "
          f"zatrzymań na rzadkiej ścieżce {tot['rare']}, średnio rzutowań przy pełnej liście {tot['maxproj']/max(n,1):.1f}")


if __name__ == "__main__":
    main()
