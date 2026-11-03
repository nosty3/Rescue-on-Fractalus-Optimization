"""Równoważność VBI dwóch ROM-ów na nagranych stanach: RAM $0000-$7FFF, zapisy do sprzętu ($D000-$D7FF,
kolejność i wartości; zapisy $D5xx = bank pomijane), SP, bank na wyjściu. Cykle CPU przed/po.
Stos poniżej SP (martwe bajty po jsr/rts) pomijany. Flagi P na wyjściu też (XITVBV zdejmuje je ze stosu).
--poison=SEED: przed odtworzeniem oba ROM-y dostają te same losowe bajty w martwych miejscach (stos poniżej SP,
$0160-$017F, $6B i $28D6 - operandy mnożenia zapisywane przed każdym użyciem) - test, że kod ich nie czyta.
Użycie: vbieq.py ROM_A ROM_B DIR [DIR...] [--ignore=ADR,ADR] [--poison=SEED]"""
import sys, json, random
from vbisim import load_scene


def rd(p):
    r = open(p, "rb").read()
    return r[16:] if r[:4] == b"CART" else r


args = [a for a in sys.argv[1:] if not a.startswith("--")]
ign = set(); poison = None
for a in sys.argv[1:]:
    if a.startswith("--ignore="):
        ign = {int(x, 16) for x in a.split("=", 1)[1].split(",")}
    if a.startswith("--poison="):
        poison = random.Random(int(a.split("=", 1)[1]))
ra, rb = rd(args[0]), rd(args[1])
# kod rezydentny (banki 0/1 -> RAM $4000-$7FFF) jest w nagranym obrazie: bajty, którymi ROM-y się tam różnią,
# wpisujemy do obrazu każdego ROM-u z jego wersji (łatki kodu rezydentnego, nie stan samomodyfikacji)
# Zakresy = ciągi różniących się bajtów scalone, gdy przerwa <= 16 (łatka może mieć bajty równe oryginałowi,
# np. operand samomodyfikacji, który w ROM-ie ma tę samą wartość początkową co w nowym kodzie - w obrazie jest
# wartość z czasu nagrania, więc kopiujemy całe zakresy łatek; stan samomodyfikacji w nich musi być martwy).
_dif = [i for i in range(0x4000) if ra[i] != rb[i]]
resranges = []
for i in _dif:
    if resranges and i - resranges[-1][1] <= 16:
        resranges[-1][1] = i
    else:
        resranges.append([i, i])
resdiff = [i for s_, e_ in resranges for i in range(s_, e_ + 1)]
if resranges:
    print("kod rezydentny, zakresy łatek (pomijane w porównaniu RAM-u):",
          ", ".join(f"${0x4000 + s_:04x}-${0x4000 + e_:04x}" for s_, e_ in resranges))
    ign |= {0x4000 + i for i in resdiff}
bad = 0; n = 0; ca = 0; cb = 0
for d in args[2:]:
    n0, ca0, cb0 = n, ca, cb
    for m in json.load(open(f"{d}/meta.json")):
        res = []
        if poison is not None:
            sp = m["regs"]["sp"]
            spots = list(range(0x100, 0x101 + sp)) + list(range(0x160, 0x180)) + [0x6B, 0x28D6]
            pz = [(a, poison.randrange(256)) for a in spots]
        for rom in (ra, rb):
            mc = load_scene(d, m, rom)
            for i in resdiff:
                mc.mem[0x4000 + i] = rom[i]
            if poison is not None:
                for a, v in pz:
                    mc.mem[a] = v
            cyc = mc.run_vbi()
            hw = [(a, v) for a, v in mc.mem.hw if not (0xD500 <= a < 0xD600)]
            res.append((bytes(mc.mem[0:0x8000]), hw, mc.cpu.sp, mc.mem.bank, cyc))
        A, B = res
        ca += A[4]; cb += B[4]; n += 1
        dead = set(range(0x100, 0x101 + A[2]))   # stos poniżej SP
        dif = [i for i in range(0x8000) if A[0][i] != B[0][i] and i not in ign and i not in dead]
        if dif or A[1] != B[1] or A[2] != B[2] or A[3] != B[3]:
            bad += 1
            if bad <= 10:
                print(f"{d} {m['k']}: RAM {[hex(i) for i in dif[:8]]} hw {'OK' if A[1]==B[1] else 'RÓŻNE'} "
                      f"sp {A[2]:02x}/{B[2]:02x} bank {A[3]}/{B[3]}")
    print(f"  {d}: stanów {n - n0}, cykle CPU/VBI {(ca - ca0) / (n - n0):.1f} -> {(cb - cb0) / (n - n0):.1f}")
print(f"stanów {n}, niezgodnych {bad}; cykle CPU/VBI: {ca/n:.1f} -> {cb/n:.1f} (różnica {(ca-cb)/n:+.1f})")
