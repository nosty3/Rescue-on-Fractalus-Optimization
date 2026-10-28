"""Wstępne decyzje relokacji (heurystyka) do xex/decisions.json, zachowując wpisy dodane ręcznie (pole "manual").
Stała LDA/LDX/LDY #$40-#$BF jest starszym bajtem adresu, gdy następna instrukcja zapisuje ten sam rejestr:
  - do zp, które jest starszym bajtem wskaźnika używanego w (zp),Y / (zp,X) / JMP (zp) w kodzie z pokrycia,
  - do wektora OS ($0200-$023F, starsze bajty) albo
  - X przed JSR SETVBV ($E45C) z LDY/LDA pomiędzy.
Użycie: autodec.py ROM COV.json DECISIONS.json"""
import sys, json
from reloc import load_rom, instructions, extend, OPS, base

rom = load_rom(sys.argv[1])
ins = extend(rom, instructions(json.load(open(sys.argv[2]))))
out = sys.argv[3]
old = json.load(open(out))
manual = old.get("manual", {})


def byte(b, a):
    return rom[b * 8192 + (a - base(b))]


ptr_hi = set(); ptr_lo = set()
for (b, a) in ins:
    op = byte(b, a); ln, mn, mode = OPS[op]
    if mode in ("izy", "izx"):
        ptr_hi.add((byte(b, a + 1) + 1) & 0xFF); ptr_lo.add(byte(b, a + 1))
    if mn == "JMP" and mode == "ind":
        t = byte(b, a + 1) | byte(b, a + 2) << 8
        ptr_hi.add(t + 1)
VECT = {0x0200 + i for i in range(1, 0x40, 2)}


def pair_store(b, a):
    """Jeśli pod (b, a) jest para LDx #imm / STx zp|abs, zwraca adres zapisu, inaczej None."""
    if (b, a) not in ins:
        return None
    ln, mn, mode = OPS[byte(b, a)]
    if mode != "imm" or mn not in ("LDA", "LDX", "LDY"):
        return None
    n = a + 2
    if (b, n) not in ins:
        return None
    ln2, mn2, mode2 = OPS[byte(b, n)]
    if mn2 != {"LDA": "STA", "LDX": "STX", "LDY": "STY"}[mn]:
        return None
    if mode2 == "zp":
        return byte(b, n + 1)
    if mode2 == "abs":
        return byte(b, n + 1) | byte(b, n + 2) << 8
    return None
STORE = {"LDA": "STA", "LDX": "STX", "LDY": "STY"}

hi = []
for (b, a) in sorted(ins, key=lambda x: (x[0], x[1])):
    op = byte(b, a); ln, mn, mode = OPS[op]
    if mode != "imm" or mn not in STORE or not 0x40 <= byte(b, a + 1) < 0xC0:
        continue
    n = a + 2
    if (b, n) not in ins:
        continue
    op2 = byte(b, n); ln2, mn2, mode2 = OPS[op2]
    if mn == "LDA" and mn2 == "ADC" and mode2 == "imm" and (b, n + 2) in ins:
        # lda #hi / adc #c / sta P: starszy bajt, gdy chwilę wcześniej zapisano P-1 (lda ... / sta P-1)
        ln3, mn3, mode3 = OPS[byte(b, n + 2)]
        if mn3 == "STA" and mode3 == "zp":
            p = byte(b, n + 3)
            before = rom[b * 8192 + (a - base(b)) - 6: b * 8192 + (a - base(b))]
            if bytes([0x85, (p - 1) & 0xFF]) in before:
                hi.append([b, a])
        continue
    tgt = None
    if mn2 == STORE[mn] and mode2 == "zp":
        tgt = byte(b, n + 1)
    elif mn2 == STORE[mn] and mode2 == "abs":
        tgt = byte(b, n + 1) | byte(b, n + 2) << 8
    if tgt is not None and mode2 == "abs" and tgt < 0x4000 and tgt not in VECT \
            and pair_store(b, a - (3 + 2)) == tgt - 1:
        hi.append([b, a]); continue          # lda #lo / sta W / lda #hi / sta W+1: słowo-adres w RAM
    if tgt is not None and (tgt in ptr_hi or tgt in VECT):
        # łańcuch par LDx #/STx pod kolejne adresy: (S, S+1), (S+2, S+3)...; P - S nieparzyste = starszy bajt
        s, x = tgt, a
        while pair_store(b, x - 4) == s - 1:
            s -= 1; x -= 4
        nxt = pair_store(b, a + 2 + OPS[op2][0]) == tgt + 1
        if s != tgt or nxt:
            if (tgt - s) % 2 == 1:
                hi.append([b, a])
            continue
        if tgt in VECT:
            hi.append([b, a])
        continue                 # bez kontekstu pary: nie zgadujemy, przeoczenie złapie symulator w kroku
    if mn == "LDX":
        x = n
        for _ in range(3):
            if (b, x) not in ins:
                break
            o3 = byte(b, x); l3, m3, md3 = OPS[o3]
            if m3 == "JSR" and (byte(b, x + 1) | byte(b, x + 2) << 8) == 0xE45C:
                hi.append([b, a]); break
            if m3 not in ("LDY", "LDA"):
                break
            x += l3

# numery banków podawane w A do wspólnego STA $D500 (cel skoku, przed którym nie stoi LDA #)
targets = {a for (b, a) in ins if b != 7 and byte(b, a) == 0x8D and byte(b, a + 1) == 0 and byte(b, a + 2) == 0xD5
           and not (byte(b, a - 2) == 0xA9 and (b, a - 2) in ins)}
bank = []
for (b, a) in sorted(ins, key=lambda x: (x[0], x[1])):
    if b == 7:
        continue
    ln, mn, mode = OPS[byte(b, a)]
    if mn in ("JMP", "JSR") and mode == "abs" and (byte(b, a + 1) | byte(b, a + 2) << 8) in targets:
        if byte(b, a - 2) == 0xA9 and (b, a - 2) in ins and byte(b, a - 1) < 16:
            bank.append([b, a - 2])
        else:
            print(f"UWAGA: skok do wspólnego STA $D500 bez LDA # przed: bank {b} ${a:04X}")

dec = {k: [] for k in ("hi", "bank", "keep", "word", "hibyte", "bankbyte", "patch")}
dec["hi"] = hi
dec["bank"] = bank
for k, v in manual.items():
    dec[k] = dec.get(k, []) + v
dec["manual"] = manual
json.dump(dec, open(out, "w"), indent=0)
print(f"wskaźniki (starsze bajty zp/abs): {sorted(hex(x) for x in ptr_hi)}")
print(f"stałe-adresy z heurystyki: {len(hi)}; ręczne: { {k: len(v) for k, v in manual.items()} }")
