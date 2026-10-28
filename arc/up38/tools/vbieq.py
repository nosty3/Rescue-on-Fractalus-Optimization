"""Równoważność VBI dwóch ROM-ów na nagranych stanach: RAM $0000-$7FFF, zapisy do sprzętu ($D000-$D7FF,
kolejność i wartości; zapisy $D5xx = bank pomijane), SP, bank na wyjściu. Cykle CPU przed/po.
Użycie: vbieq.py ROM_A ROM_B DIR [DIR...] [--ignore=ADR,ADR]"""
import sys, json
from vbisim import load_scene


def rd(p):
    r = open(p, "rb").read()
    return r[16:] if r[:4] == b"CART" else r


args = [a for a in sys.argv[1:] if not a.startswith("--")]
ign = set()
for a in sys.argv[1:]:
    if a.startswith("--ignore="):
        ign = {int(x, 16) for x in a.split("=", 1)[1].split(",")}
ra, rb = rd(args[0]), rd(args[1])
bad = 0; n = 0; ca = 0; cb = 0
for d in args[2:]:
    for m in json.load(open(f"{d}/meta.json")):
        res = []
        for rom in (ra, rb):
            mc = load_scene(d, m, rom)
            cyc = mc.run_vbi()
            hw = [(a, v) for a, v in mc.mem.hw if not (0xD500 <= a < 0xD600)]
            res.append((bytes(mc.mem[0:0x8000]), hw, mc.cpu.sp, mc.mem.bank, cyc))
        A, B = res
        ca += A[4]; cb += B[4]; n += 1
        dif = [i for i in range(0x8000) if A[0][i] != B[0][i] and i not in ign]
        if dif or A[1] != B[1] or A[2] != B[2] or A[3] != B[3]:
            bad += 1
            if bad <= 10:
                print(f"{d} {m['k']}: RAM {[hex(i) for i in dif[:8]]} hw {'OK' if A[1]==B[1] else 'RÓŻNE'} "
                      f"sp {A[2]:02x}/{B[2]:02x} bank {A[3]}/{B[3]}")
print(f"stanów {n}, niezgodnych {bad}; cykle CPU/VBI: {ca/n:.1f} -> {cb/n:.1f} (różnica {(ca-cb)/n:+.1f})")
