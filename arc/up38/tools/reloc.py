"""Relokacja Fractalusa pod .xex z pamięcią rozszerzoną (PORTB, okno $4000-$7FFF).

Układ kartridża:  $4000-$7FFF kod rezydentny (kopia banków 0/1), $8000-$9FFF okno banków, $A000-$BFFF bank 15.
Układ .xex:       $4000-$5FFF okno = bank n w banku rozszerzenia, $6000-$7FFF = kopia banku 15 (w każdym banku
                  rozszerzenia), $8000-$BFFF kod rezydentny (zwykły RAM, BASIC wyłączony). OS ROM zostaje.
Mapowanie adresów: $4000-$7FFF -> +$4000, $8000-$BFFF -> -$4000 (czyli a ^ $C000). Młodsze bajty bez zmian, więc
przekroczenia stron i liczba cykli zostają takie same.

Numer banku n -> wartość PORTB v(n): bity 0,1,7 = 1 (OS ROM, bez BASIC-a, bez self-testu), bit 4 = 0 (CPU widzi
pamięć rozszerzoną), bity 2,3,5,6 = n (16 różnych banków na 320K Rambo, 576K i 1088K)."""
import json
from py65.devices.mpu6502 import MPU
from py65.disassembler import Disassembler

USED = [0, 1, 2, 3, 4, 5, 6, 8, 9, 10, 11, 12, 13, 14]
BASE = {0: 0x4000, 1: 0x6000, 15: 0xA000}


def base(b):
    return BASE.get(b, 0x8000)


def M(a):
    """Adres z układu kartridża na układ .xex."""
    return a ^ 0xC000 if 0x4000 <= a < 0xC000 else a


def Mhi(v):
    """Starszy bajt adresu po mapowaniu."""
    return v ^ 0xC0 if 0x40 <= v < 0xC0 else v


def portb(n):
    return 0x83 | (n & 3) << 2 | (n >> 2 & 3) << 5


_m = MPU(); _d = Disassembler(_m)
OPS = {}
for _op in range(256):
    _m.memory[0] = _op; _m.memory[1] = 0x34; _m.memory[2] = 0x12
    _ln, _t = _d.instruction_at(0)
    _p = _t.split()
    _mode = "imp"
    if len(_p) > 1:
        _a = _p[1]
        if _a.startswith("#"): _mode = "imm"
        elif _a.startswith("(") and _a.endswith(",X)"): _mode = "izx"
        elif _a.startswith("(") and _a.endswith("),Y"): _mode = "izy"
        elif _a.startswith("("): _mode = "ind"
        elif _a.endswith(",X"): _mode = "abx" if _ln == 3 else "zpx"
        elif _a.endswith(",Y"): _mode = "aby" if _ln == 3 else "zpy"
        elif _ln == 3: _mode = "abs"
        elif _p[0].startswith("B") and _p[0] != "BIT": _mode = "rel"
        else: _mode = "zp"
    OPS[_op] = (_ln, _p[0], _mode)


def load_rom(path):
    rom = open(path, "rb").read()
    return rom[16:] if rom[:4] == b"CART" else rom


def instructions(cov):
    """Zbiór (bank, adres CPU) początków instrukcji z pokrycia covmap.py."""
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
    return ins


def extend(rom, ins):
    """Rozszerzenie statyczne pokrycia: od każdej wykonanej instrukcji następna (poza JMP/RTS/RTI/BRK), cele gałęzi,
    cele JMP/JSR abs w tej samej przestrzeni (albo w kodzie rezydentnym / stałym banku). Zwraca nowy zbiór."""
    def inside(b, a):
        return base(b) <= a < base(b) + 0x2000

    def byte(b, a):
        return rom[b * 8192 + (a - base(b))]

    out = set(ins)
    work = [x for x in out if x[0] != 7]
    while work:
        b, a = work.pop()
        if a - base(b) > 0x1FFD:
            continue
        ln, mn, mode = OPS[byte(b, a)]
        if mn == "???":
            continue
        nxt = []
        switch = mn == "STA" and ln == 3 and byte(b, a + 2) == 0xD5      # dalej wykonanie w innym banku
        if mn not in ("JMP", "RTS", "RTI", "BRK") and not switch:
            nxt.append((b, a + ln))
        if mode == "rel":
            off = byte(b, a + 1); nxt.append((b, a + 2 + (off - 256 if off > 127 else off)))
        if mn in ("JMP", "JSR") and mode == "abs":
            t = byte(b, a + 1) | byte(b, a + 2) << 8
            if inside(b, t):
                nxt.append((b, t))
            else:
                nxt += [(x, t) for x in (0, 1, 15) if inside(x, t)]
        for key in nxt:
            if inside(*key) and key not in out:
                out.add(key); work.append(key)
    return out


def build(rom, ins, decisions):
    """Zwraca (ext, log): ext[n] = 16 KB banku rozszerzenia; log = lista zmian (bank, adres, opis).
    decisions: {"hi": [[bank, adres], ...]  stałe #imm = starszy bajt adresu,
                "bank": [[bank, adres], ...] stałe #imm = numer banku,
                "keep": [[bank, adres], ...] operand abs, którego NIE przenosić,
                "word": [[bank, adres], ...] słowo danych (lo, hi) = adres do przeniesienia,
                "hibyte": [[bank, adres], ...] bajt danych = starszy bajt adresu,
                "bankbyte": [[bank, adres], ...] bajt danych = numer banku,
                "patch": [[bank, adres, "hex"], ...] dowolne bajty po relokacji}"""
    banks = {b: bytearray(rom[b * 8192:(b + 1) * 8192]) for b in range(16)}
    log = []
    keep = {tuple(x) for x in decisions.get("keep", [])}
    for (b, a) in sorted(ins):
        if b == 7:
            continue
        blk = banks[b]; o = a - base(b)
        op = blk[o]; ln, mn, mode = OPS[op]
        if ln == 3 and o + 2 < 8192:
            t = blk[o + 1] | blk[o + 2] << 8
            if mode in ("abs", "abx", "aby", "ind") and (b, a) not in keep:
                if 0xD500 <= t < 0xD600 and mn == "STA":
                    blk[o + 1], blk[o + 2] = 0x01, 0xD3
                    log.append((b, a, "sta $d500 -> sta $d301"))
                    if o >= 2 and blk[o - 2] == 0xA9 and (b, a - 2) in ins and blk[o - 1] < 16:
                        v = blk[o - 1]; blk[o - 1] = portb(v)
                        log.append((b, a - 2, f"lda #{v} -> #${portb(v):02x} (bank)"))
                elif 0x4000 <= t < 0xC000:
                    n = M(t); blk[o + 1], blk[o + 2] = n & 0xFF, n >> 8
    for b, a in decisions.get("hi", []):
        o = a - base(b) + 1; v = banks[b][o]; banks[b][o] = Mhi(v)
        log.append((b, a, f"#${v:02x} -> #${banks[b][o]:02x} (adres)"))
    for b, a in decisions.get("bank", []):
        o = a - base(b) + 1; v = banks[b][o]; banks[b][o] = portb(v)
        log.append((b, a, f"#${v:02x} -> #${banks[b][o]:02x} (bank)"))
    for b, a in decisions.get("word", []):
        o = a - base(b); t = banks[b][o] | banks[b][o + 1] << 8; n = M(t)
        banks[b][o], banks[b][o + 1] = n & 0xFF, n >> 8
        log.append((b, a, f"slowo ${t:04x} -> ${n:04x}"))
    for b, a, n in decisions.get("wordtab", []):
        for k in range(n):
            o = a - base(b) + 2 * k; t = banks[b][o] | banks[b][o + 1] << 8
            if 0x4000 <= t < 0xC000:
                m = M(t); banks[b][o], banks[b][o + 1] = m & 0xFF, m >> 8
        log.append((b, a, f"tablica {n} slow"))
    for b, a, n in decisions.get("hitab", []):
        for k in range(n):
            o = a - base(b) + k; banks[b][o] = Mhi(banks[b][o])
        log.append((b, a, f"tablica {n} starszych bajtow"))
    for b, a in decisions.get("hibyte", []):
        o = a - base(b); v = banks[b][o]; banks[b][o] = Mhi(v)
        log.append((b, a, f"bajt ${v:02x} -> ${banks[b][o]:02x}"))
    for b, a in decisions.get("bankbyte", []):
        o = a - base(b); v = banks[b][o]; banks[b][o] = portb(v)
        log.append((b, a, f"bank ${v:02x} -> ${banks[b][o]:02x}"))
    for b, a, hx in decisions.get("patch", []):
        o = a - base(b); data = bytes.fromhex(hx)
        banks[b][o:o + len(data)] = data
        log.append((b, a, f"latka {hx}"))
    ext = {}
    for n in USED:
        ext[n] = bytes(banks[n]) + bytes(banks[15])
    return ext, log
