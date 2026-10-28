"""Kto czyta/pisze RAM w [LO, HI] w trakcie gry: pułapki dostępu co STEP bajtów, przebieg boot -> menu -> START
-> lot z losowym sterowaniem. Zatrzymanie pułapki = krok `cycles` niedokończony (clock: step_completed False);
wtedy ostatnia instrukcja z historii CPU to ta, która sięgnęła do pamięci (pole `ea` historii jest puste).
Wypisuje unikalne (bank, PC, deasemblacja) z liczbą trafień i trybami $4A.
Użycie: watchmap.py ROM LO HI STEP FRAMES SEED PRESSES [OD_KLATKI]"""
import sys, random
from collections import defaultdict
from fx import Emu

rom = sys.argv[1]; lo = int(sys.argv[2], 0); hi = int(sys.argv[3], 0); step = int(sys.argv[4], 0)
frames = int(sys.argv[5]); seed = int(sys.argv[6]); presses = int(sys.argv[7])
since = int(sys.argv[8]) if len(sys.argv) > 8 else 0
rnd = random.Random(seed)
hits = defaultdict(lambda: [0, set(), None])   # (bank, pc) -> [n, tryby $4A, deasemblacja]
CYC = 35568   # jedna ramka PAL w cyklach maszyny


def num(v):
    """Liczba z odpowiedzi Altirry: int albo tekst '$ffff'."""
    if v is None or isinstance(v, int):
        return v
    return int(str(v).lstrip("$"), 16)


with Emu("pal") as e:
    a = e.a
    a.config("history", "true")
    a.boot(rom)
    f = 0; armed = False; started = False; stops = 0; left = CYC
    while f < frames:
        if not started and f >= 3100:
            for _ in range(presses):
                a.joy(0, "n"); a.frame(30); a.joy(0, "c"); a.frame(30); f += 60
            a.consol(start=True); a.frame(100); a.consol(); f += 100
            started = True
            continue
        if not armed and f >= since:
            for ad in range(lo, hi + 1, step):
                a.watch_set(ad, "rw")
            armed = True
        if started and f % 40 == 0 and left == CYC:
            a.joy(0, rnd.choice(["c", "n", "s", "e", "w", "ne", "nw"]), fire=rnd.random() < 0.4)
        a.cycles(left)
        c = a.clock()
        if not c.get("step_completed", True):
            stops += 1
            left = max(1, left - c.get("step_elapsed", 0))
            h = a.history(1)[-1]
            pc = num(h["pc"])
            bank = a.cart_info().get("bank") if 0x8000 <= pc < 0xA000 else -1
            r = hits[(bank, pc)]; r[0] += 1; r[1].add(a.eval_expr("db($4a)"))
            if r[2] is None:
                r[2] = a.disasm(pc, 1)
            if stops > 30000:
                break
            continue
        left = CYC; f += 1

print(f"zatrzymań: {stops}; unikalnych instrukcji: {len(hits)}")
for (b, pc), (n, modes, dis) in sorted(hits.items()):
    print(f"  bank {b:2} ${pc:04X} x{n:6d}  tryby $4A {sorted(modes)}  {dis}")
