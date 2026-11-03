"""Test rozdarcia: dla każdej ramki odczytuje wiersz r wyświetlanego bufora tuż po jego pobraniu przez ANTIC
(linia 49 + 2r), a potem sprawdza, że ramki z tą samą display listą (ten sam obraz) mają identyczne
pobrane wiersze. Wiersz 46 (znacznik rysowany przez VBI) pomijany.
Użycie: tearcheck.py ROM N_RAMEK [SEED]"""
import sys, random
from fx import Emu, enter_flight

rom = sys.argv[1]; nfr = int(sys.argv[2]); seed = int(sys.argv[3]) if len(sys.argv) > 3 else 0
rnd = random.Random(seed)
with Emu("pal") as e:
    a = e.a
    enter_flight(a, rom, 3165)
    a.frame(170)
    periods = []; cur_dl = None; cur = []
    bad = 0; frames = 0
    for f in range(nfr):
        if seed and f % 20 == 0:
            a.joy(0, rnd.choice(["c", "n", "s", "e", "w"]), fire=rnd.random() < 0.3)
        # dojdź do linii 40 bieżącej ramki
        st = a.antic(); y = st["beam_y"]
        a.scanlines((40 - y) % 312 or 312)
        # licznik DL w linii 40: lista 1 ($316B-$320F, LMS $1070 = bufor 0) albo lista 2 ($3210-, bufor +48)
        dlp = int(a.antic()["DLIST"][1:], 16)
        dl = "DL1" if dlp < 0x3210 else "DL2"
        x0 = 0 if dl == "DL1" else 48
        rows = []
        y = a.antic()["beam_y"]
        for r in range(1, 48):
            target = 49 + 2 * r
            a.scanlines(target - y); y = target
            rows.append(bytes(a.memdump(0x1010 + 96 * r + x0 + 3, 42)) if r != 46 else b"")
        frames += 1
        if dl != cur_dl:
            if cur:
                periods.append((cur_dl, cur))
            cur_dl = dl; cur = [rows]
        else:
            if rows != cur[0]:
                diff = [r + 1 for r in range(47) if rows[r] != cur[0][r]]
                bad += 1
                if bad <= 5:
                    print(f"ramka {f}: obraz {dl} różni się od pierwszej ramki okresu w wierszach {diff[:10]}")
            cur.append(rows)
    print(f"ramek {frames}, okresów {len(periods)}, ramek z rozdarciem: {bad}")
