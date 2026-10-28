"""Mapa użycia RAM-u w zakresie [LO, HI]: zrzut co STEP klatek przez boot, menu, START i lot z losowym sterowaniem.
Wypisuje zakresy bajtów, które się zmieniały (z trybem $4A, w którym zmiana nastąpiła po raz pierwszy),
oraz zakresy niezerowe po boocie. Użycie: ramuse.py ROM LO HI FRAMES SEED PRESSES [STEP]"""
import sys, random
from fx import Emu

rom = sys.argv[1]; lo = int(sys.argv[2], 0); hi = int(sys.argv[3], 0)
frames = int(sys.argv[4]); seed = int(sys.argv[5]); presses = int(sys.argv[6])
step = int(sys.argv[7]) if len(sys.argv) > 7 else 25
rnd = random.Random(seed)
n = hi - lo + 1
first = {}          # adres -> (klatka, tryb) pierwszej zmiany
inflight = set()    # adresy zmieniane w trakcie lotu ($4A = 2)
with Emu("pal") as e:
    a = e.a
    a.boot(rom)
    a.frame(60)
    base = bytes(a.memdump(lo, n))
    prev = base
    f = 60
    started = False
    while f < frames:
        if not started and f >= 3100:
            for _ in range(presses):
                a.joy(0, "n"); a.frame(30); a.joy(0, "c"); a.frame(30); f += 60
            a.consol(start=True); a.frame(100); a.consol(); f += 100
            started = True
        if started:
            a.joy(0, rnd.choice(["c", "n", "s", "e", "w", "ne", "nw"]), fire=rnd.random() < 0.4)
        a.frame(step); f += step
        cur = bytes(a.memdump(lo, n))
        mode = a.eval_expr("db($4a)")
        for i in range(n):
            if cur[i] != prev[i]:
                if (lo + i) not in first:
                    first[lo + i] = (f, mode)
                if mode == 2:
                    inflight.add(lo + i)
        prev = cur


def ranges(addrs):
    out = []
    for ad in sorted(addrs):
        if out and ad == out[-1][1] + 1:
            out[-1][1] = ad
        else:
            out.append([ad, ad])
    return out


print("strony (256 B): bajty zmieniane w ogóle / w trakcie lotu, pierwsza klatka zmiany")
for p in range(lo >> 8, (hi >> 8) + 1):
    inpage = [ad for ad in first if ad >> 8 == p]
    if inpage:
        fl = sum(1 for ad in inpage if ad in inflight)
        print(f"  ${p:02X}xx: {len(inpage):3d} / {fl:3d}  od klatki {min(first[ad][0] for ad in inpage)}")
print(f"zmieniane bajty: {len(first)}")
for s, t in ranges(first):
    fr, md = first[s]
    print(f"  ${s:04X}-${t:04X} ({t-s+1:5d} B) pierwsza zmiana klatka {fr} tryb {md}")
nz = [lo + i for i in range(n) if base[i] != 0]
print(f"niezerowe po boocie (klatka 60): {len(nz)}")
for s, t in ranges(nz)[:40]:
    print(f"  ${s:04X}-${t:04X} ({t-s+1:5d} B)")
