"""Test wolnego RAM-u: dwa przebiegi z identycznym wejściem; w drugim co K ramek (od klatki PSTART) zatruwamy obszar [lo, hi]
losowymi bajtami. Porównanie RAM-u poza obszarem i zrzutów ekranu w punktach kontrolnych + czy gra pisze
w obszar (zmiana względem ostatniej trucizny). Użycie: poison.py ROM LO HI FRAMES SEED PRESSES [PSTART]"""
import sys, random, hashlib
from fx import Emu

rom = sys.argv[1]; lo = int(sys.argv[2], 0); hi = int(sys.argv[3], 0)
frames = int(sys.argv[4]); seed = int(sys.argv[5]); presses = int(sys.argv[6])
pstart = int(sys.argv[7]) if len(sys.argv) > 7 else 20   # od której klatki truć (np. 3500 = dopiero w locie)
K = 50
wf = []


def run(poison):
    rnd = random.Random(seed); prnd = random.Random(999)
    snaps = []; writes = 0; wf.clear()
    with Emu("pal") as e:
        a = e.a
        a.boot(rom)
        last = None
        total = 3100 + presses * 60 + 200 + frames
        f = 0
        while f < total:
            if f == 3100:
                for _ in range(presses):
                    a.joy(0, "n"); a.frame(30); a.joy(0, "c"); a.frame(30); f += 60
                a.consol(start=True); a.frame(100); a.consol(); f += 100
                continue
            if f > 3300 and f % 40 == 0:
                a.joy(0, rnd.choice(["c", "n", "s", "e", "w", "ne", "nw"]), fire=rnd.random() < 0.4)
            if poison and f % K == 0 and f > pstart:
                cur = bytes(a.memdump(lo, hi - lo + 1))
                if last is not None and cur != last:
                    writes += 1; wf.append(f)
                last = bytes(prnd.randrange(256) for _ in range(hi - lo + 1))
                a.memload(lo, last) if hasattr(a, "memload") else None
            a.frame(10); f += 10
            if f % 500 == 0:
                m = bytearray(a.memdump(0, 0x8000)); m[lo:hi + 1] = bytes(hi - lo + 1)
                snaps.append((f, hashlib.sha256(m).hexdigest(), hashlib.sha256(a.screenshot()).hexdigest(), m[0x4A]))
    return snaps, writes


A, _ = run(False)
B, w = run(True)
same = [x == y for x, y in zip(A, B)]
print("punkty kontrolne:", len(A), "zgodne:", sum(same), "pierwsza różnica:", next((A[i] for i, s in enumerate(same) if not s), None))
print("tryby $4A w punktach:", [x[3] for x in A])
print("razy gra zmieniła zatruty obszar:", w)
