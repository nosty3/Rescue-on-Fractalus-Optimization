"""Ile pracy rasteryzacji oszczędza rekurencyjne odrzucanie poddrzew (granica E(w) nosty3)?
Wejście: pickle odcinków z modelcheck.py. Dla progu t: odrzucanie na każdym podziale o szerokości >= t.
Koszt skanu = kolumny sprawdzone do pierwszej porażki (albo wszystkie przy sukcesie)."""
import sys, pickle
from rastermodel import raster


def E(w, memo={}):
    if w <= 2:
        return 0
    if w not in memo:
        memo[w] = w // 4 + 1 + max(E(w // 2), E((w + 1) // 2))
    return memo[w]


MEMO = len(sys.argv) > 3
segs = pickle.load(open(sys.argv[1], "rb"))
nimg = int(sys.argv[2])


def run(t, entry_only=False):
    tot = dict(tests=0, splits=0, scan=0, attempts=0, culled=0, seg_culled=0)
    for s in segs:
        L, R, occ0 = s["L"], s["R"], s["occ"]
        st = {}
        # wejście całego odcinka (jak cull_entry v10)
        x0, x1 = L[0], R[0]
        if x1 > x0 and x0 >= 44 and x1 < 212:
            hmax = min(255, max(L[1], R[1]) + E(x1 - x0))
            n = 0; ok = True
            for col in range(x0, x1):
                n += 1
                if occ0[col] < hmax:
                    ok = False; break
            tot["scan"] += n; tot["attempts"] += 1
            if ok:
                tot["seg_culled"] += 1
                continue

        memo = {"x0": 0, "k": 0, "h": -1}

        def cull(xl, xr, hl, hr, w, stats):
            if entry_only or w < t:
                return False
            hmax = min(255, max(hl, hr) + E(w))
            start = xl
            if MEMO and xl >= memo["x0"] and hmax <= memo["h"] and memo["k"] > xl:
                start = memo["k"]          # kolumny xl..k-1 już spełniają occ >= h >= hmax
            n = 0
            for col in range(start, xr):
                n += 1
                if occ[col] < hmax:
                    memo.update(x0=xl, k=col, h=hmax)
                    tot["scan"] += n; tot["attempts"] += 1
                    return False
            tot["scan"] += n; tot["attempts"] += 1; tot["culled"] += 1
            return True
            for col in range(xl, xr):
                n += 1
                if occ[col] < hmax:
                    tot["scan"] += n; tot["attempts"] += 1
                    return False
            tot["scan"] += n; tot["attempts"] += 1; tot["culled"] += 1
            return True

        occ = bytearray(occ0)
        ref = bytearray(occ0)
        p1 = raster(L, R, occ, st, cull)
        p0 = raster(L, R, ref)
        assert p0 == p1 and occ == ref, "odrzucenie zmieniło wynik!"
        tot["tests"] += st.get("tests", 0); tot["splits"] += st.get("splits", 0)
    return {k: v / nimg for k, v in tot.items()}


base = run(999, entry_only=True)
print("tylko wejście (v10):", {k: round(v, 1) for k, v in base.items()})
for t in (3, 4, 6, 8, 12, 16, 24, 32):
    r = run(t)
    # model kosztu (cykle CPU): podział ~45, test liścia ~28, skan kolumny 9 (rozwinięty) + próba 25
    cost = lambda q: 45 * q["splits"] + 28 * q["tests"] + 9 * q["scan"] + 25 * q["attempts"]
    print(f"t={t:2d}:", {k: round(v, 1) for k, v in r.items()}, f" koszt~{cost(r):.0f} vs {cost(base):.0f}")
