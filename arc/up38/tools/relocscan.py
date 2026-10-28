"""Analiza pod port .xex (zamiana $4000-$7FFF <-> $8000-$BFFF): mapa instrukcji z pokrycia profilera
(covmap.py) + rozszerzenie statyczne, potem listy miejsc do relokacji.

Przestrzenie (bank ROM -> adres CPU):  0 -> $4000 (rezydentny), 1 -> $6000 (rezydentny), 2..14 -> $8000 (okno),
15 -> $A000 (stały). Klucz 'cpu' z pokrycia: $4000-$7FFF = banki 0/1, $A000-$BFFF = bank 15, reszta = kod w RAM.

Wypisuje: liczby instrukcji, operandy abs w zakresie $4000-$BFFF, stałe #$40-#$BF z kontekstem, użycia (zp),Y /
(zp,X) / JMP (ind), zapisy w $8000-$BFFF (na kartridżu bez skutku), kod w RAM poniżej $4000.
Użycie: relocscan.py ROM COV.json [--static] [--list KIND]"""
import sys, json
from collections import Counter, defaultdict
from py65.devices.mpu6502 import MPU
from py65.disassembler import Disassembler

rom = open(sys.argv[1], "rb").read()
rom = rom[16:] if rom[:4] == b"CART" else rom
cov = json.load(open(sys.argv[2]))
STATIC = "--static" in sys.argv
LIST = sys.argv[sys.argv.index("--list") + 1] if "--list" in sys.argv else None

_m = MPU(); _d = Disassembler(_m)
OPS = {}
for op in range(256):
    _m.memory[0] = op; _m.memory[1] = 0x34; _m.memory[2] = 0x12
    ln, t = _d.instruction_at(0)
    p = t.split()
    mode = "imp"
    if len(p) > 1:
        a = p[1]
        if a.startswith("#"): mode = "imm"
        elif a.startswith("(") and a.endswith(",X)"): mode = "izx"
        elif a.startswith("(") and a.endswith("),Y"): mode = "izy"
        elif a.startswith("("): mode = "ind"
        elif a.endswith(",X"): mode = "abx" if ln == 3 else "zpx"
        elif a.endswith(",Y"): mode = "aby" if ln == 3 else "zpy"
        elif ln == 3: mode = "abs"
        elif p[0].startswith("B") and p[0] != "BIT": mode = "rel"
        else: mode = "zp"
    OPS[op] = (ln, p[0], mode)

BASE = {0: 0x4000, 1: 0x6000, 15: 0xA000}


def base(b):
    return BASE.get(b, 0x8000)


def byte(b, cpu):
    return rom[b * 8192 + (cpu - base(b))]


def inside(b, cpu):
    return base(b) <= cpu < base(b) + 0x2000


# --- instrukcje z pokrycia: (bank, adres CPU) ---
ins = set()
for key, d in cov.items():
    for k in d:
        a = int(k, 16)
        if key.startswith("bank:"):
            ins.add((int(key[5:]), a))
        elif 0x4000 <= a < 0x6000:
            ins.add((0, a))
        elif 0x6000 <= a < 0x8000:
            ins.add((1, a))
        elif 0xA000 <= a < 0xC000:
            ins.add((15, a))
        else:
            ins.add(("ram", a))
dyn = set(ins)

# --- rozszerzenie statyczne: gałęzie nie wzięte, cele skoków w tej samej przestrzeni ---
if STATIC:
    work = [x for x in ins if x[0] != "ram"]
    while work:
        b, a = work.pop()
        op = byte(b, a); ln, mn, mode = OPS[op]
        if mn == "???":
            continue
        nxt = []
        if mn not in ("JMP", "RTS", "RTI", "BRK"):
            nxt.append(a + ln)
        if mode == "rel":
            off = byte(b, a + 1); nxt.append(a + 2 + (off - 256 if off > 127 else off))
        if mn in ("JMP", "JSR") and mode == "abs":
            t = byte(b, a + 1) | byte(b, a + 2) << 8
            for bb in ((b,) if inside(b, t) else [x for x in (0, 1, 15) if inside(x, t)]):
                nxt.append((bb, t))
        for n in nxt:
            key = n if isinstance(n, tuple) else (b, n)
            if inside(key[0], key[1]) and key not in ins:
                ins.add(key); work.append(key)

print("instrukcje (dynamicznie / razem):", len(dyn), "/", len(ins))
print("  wg przestrzeni:", sorted(Counter(str(x[0]) for x in ins).items()))

# --- listy ---
absops = []; imms = []; indir = []; romwrites = []; d5 = []
for (b, a) in sorted(ins, key=lambda x: (str(x[0]), x[1])):
    if b == "ram":
        continue
    op = byte(b, a); ln, mn, mode = OPS[op]
    if ln == 3:
        t = byte(b, a + 1) | byte(b, a + 2) << 8
        if 0xD500 <= t <= 0xD5FF:
            d5.append((b, a, mn))
        elif 0x4000 <= t < 0xC000 and mode in ("abs", "abx", "aby", "ind"):
            absops.append((b, a, mn, mode, t, (b, a) in dyn))
            if mn in ("STA", "STX", "STY", "INC", "DEC", "ASL", "LSR", "ROL", "ROR") and t >= 0x8000:
                romwrites.append((b, a, mn, t))
    if mode == "imm" and 0x40 <= byte(b, a + 1) < 0xC0 and mn in ("LDA", "LDX", "LDY"):
        imms.append((b, a, mn, byte(b, a + 1), (b, a) in dyn))
    if mode in ("izy", "izx") or (mn == "JMP" and mode == "ind"):
        indir.append((b, a, mn, mode, byte(b, a + 1) if mode != "ind" else byte(b, a + 1) | byte(b, a + 2) << 8))

print("operandy abs w $4000-$BFFF:", len(absops), "(z tego tylko statyczne:", sum(1 for x in absops if not x[5]), ")")
print("  cel wg obszaru:", sorted(Counter(f"${x[4] >> 12:X}xxx" for x in absops).items()))
print("stałe #$40-#$BF w LDA/LDX/LDY:", len(imms))
print("pośrednie (zp),Y / (zp,X) / JMP (ind):", len(indir), " zp:", sorted(Counter(f"${x[4]:02X}" if x[3] != "ind" else f"(${x[4]:04X})" for x in indir).items()))
print("zapisy w $8000-$BFFF:", len(romwrites))
print("dostęp do $D5xx:", len(d5), Counter(x[2] for x in d5))
ram = sorted(a for (b, a) in ins if b == "ram")
if ram:
    runs = []
    for a in ram:
        if runs and a - runs[-1][1] < 16:
            runs[-1][1] = a
        else:
            runs.append([a, a])
    print("kod w RAM:", ", ".join(f"${s:04X}-${t:04X}" for s, t in runs))

if LIST == "imm":
    for b, a, mn, v, dy in imms:
        ctx = []
        x = a
        for _ in range(4):
            op = byte(b, x); ln, m2, mode = OPS[op]
            ctx.append(" ".join(f"{byte(b, x + i):02x}" for i in range(ln)))
            x += ln
        print(f"  {b:>2} ${a:04X} {mn} #${v:02X} {'D' if dy else 's'} | " + " | ".join(ctx))
elif LIST == "romw":
    for b, a, mn, t in romwrites:
        print(f"  {b:>2} ${a:04X} {mn} ${t:04X}")
elif LIST == "indir":
    for x in indir:
        print("  ", x)
elif LIST == "static":
    for b, a, mn, mode, t, dy in absops:
        if not dy:
            print(f"  {b:>2} ${a:04X} {mn} {mode} ${t:04X}")
