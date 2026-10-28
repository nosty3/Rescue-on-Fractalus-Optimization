"""Generuje src/raster5.asm = bank 5 v10.1 (nosty3, src/v10_plotter.asm) + rekurencyjne odrzucanie
zasłoniętych poddrzew na podziałach szerokości >= 6 (głębokości d0..d4).

Granica jak w cull_entry nosty3: Hmax = min(255, max(h_L, h_R) + E(w)); poddrzewo pomijane, gdy dla każdej
kolumny x..sx-1 occ[x] >= Hmax. Po pominięciu stan = jak po przerobieniu poddrzewa: X = sx, $84 = h_R,
$86 = faza_R, głębokość - 1 (dla d0 koniec odcinka: ldx $60 / jmp $9900).
Szybka ścieżka: occ[x] < h_L => occ[x] < Hmax => poddrzewo widoczne, bez liczenia granicy (79 z ~92
nieudanych prób na obraz pada na pierwszej kolumnie, 59 łapie ten test).
Specjalizacje głębokości d5-d7 nosty3 (0,08% czasu, 1,8 KB) usunięte: d4 przechodzi do ogólnej dg."""
import re, sys, os
from paths import NOSTY
SRC = f"{NOSTY}/src/v10_plotter.asm"
OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "src",
                   "raster5c.asm" if "--nolazy" in sys.argv else "raster5.asm")
DEPTHS = range(5)

lines = open(SRC).read().split("\n")
# --- usunięcie d5..d7 (od pierwszej etykiety d5_ do pierwszej dg_) i przekierowanie skoków z d4 ---
s5 = next(i for i, l in enumerate(lines) if l.startswith("d5_"))
sg = next(i for i, l in enumerate(lines) if l.startswith("dg_"))
lines = lines[:s5] + lines[sg:]
lines = [l.replace("JMP d5_986f", "JMP dg_986f").replace("JMP d5_9939", "JMP dg_9939") for l in lines]
assert not any(re.search(r"\bd[567]_", l) for l in lines)


FULL = []   # pełne części prób, wstawiane przed cull_entry


def scan4(loop, vis):
    """Skan occ[X..] >= $b5 grupami po 4 kolumny; Y = szerokość w (>= 1) na wejściu.
    Sprawdza ceil(w/4)*4 kolumn, czyli do 3 za koniec: nadmiar może tylko zablokować odrzucenie
    (zachowawczo), nigdy go wymusić. ~11,75 cykla/kolumnę zamiast 16. Niewidoczne -> dalej; widoczne -> vis."""
    return [" tya", " clc", " adc #3", " lsr", " lsr", " tay",
            loop,
            " lda $260e,x", " cmp $b5", f" bcc {vis}",
            " lda $260f,x", " cmp $b5", f" bcc {vis}",
            " lda $2610,x", " cmp $b5", f" bcc {vis}",
            " lda $2611,x", " cmp $b5", f" bcc {vis}",
            " txa", " adc #3", " tax",                           # C = 1 po ostatnim cmp: X += 4
            " dey", f" bne {loop}"]


def stub(d, cont):
    """Wejście: A = X - sx, C = 0, X = $82 = x, Y = d. Wyjście do `cont` z C = 0, X/Y bez zmian.
    W pętli tylko szybki test; reszta (FULL) poza pętlą, żeby nie psuć zasięgu gałęzi nosty3."""
    FULL.extend(full(d, cont))
    return [f"; Opus: odrzucanie poddrzewa, głębokość {d} (szybki test w pętli)",
            " lda $260e,x", " cmp $84", f" bcc {cont}",          # occ[x] < h_L: widoczne (C = 0)
            f" jmp o{d}_full"]


def full(d, cont):
    sx, sh = 0x95 + d, 0xEA + d
    return [f"o{d}_full",
            f" lda ${sx:02x}", " sec", " sbc $82", " tay",        # Y = w
            " lda $84", f" cmp ${sh:02x}", f" bcs o{d}_m", f" lda ${sh:02x}",
            f"o{d}_m", " clc", " adc cull_extra,y", f" bcc o{d}_l", " lda #$ff",
            f"o{d}_l", " sta $b5"] + scan4(f"o{d}_s", f"o{d}_v") + [
            f" ldx ${sx:02x}",                                    # po sukcesie X = sx (skan mógł wyjść dalej)
            f" jmp o{d}_hidden",
            f"o{d}_v", " ldx $82", f" ldy #{d}", " clc", f" jmp {cont}"]


def hidden(d):
    sh, sp = 0xEA + d, 0xF4 + d
    tail = [f" ldy #{d-1}", f" jmp d{d-1}_9933"] if d else [" ldx $60", " jmp $9900"]
    return [f"o{d}_hidden", f" lda ${sh:02x}", " sta $84", f" lda ${sp:02x}", " sta $86"] + tail


out = []
i = 0
done = set()
while i < len(lines):
    ln = lines[i]
    m = re.match(r"^ordinary_(\d)$", ln)
    if m and int(m.group(1)) in DEPTHS:
        d = int(m.group(1))
        out.append(ln); out += stub(d, f"o{d}_go") + [f"o{d}_go"]; done.add(d); i += 1
        continue
    m = re.match(r"^d(0)_99fa$", ln)
    if m:
        d = 0
        assert lines[i + 1].strip() == "cmp #$fd" and lines[i + 2].strip().startswith("beq") and lines[i + 3].strip() == "TXA"
        # szerokość 3 (diff $fd) zostaje na ścieżce split3; 4 i 5 bez odrzucania
        out += [ln, " cmp #$fb", " bcs o0_orig"] + stub(0, "o0_after") + [
                "o0_orig", lines[i + 1], lines[i + 2], "o0_after", lines[i + 3]]
        done.add(d); i += 4
        continue
    if ln == "cull_entry":
        out += ["; --- Opus: pełne próby odrzucania (poza pętlami) ---"] + FULL
        out.append(ln); i += 1
        continue
    if ln == "cull_scan":
        # skan nosty3 (inx/cpx $95) -> skan grupami po 4; Y = w z wejścia cull_entry nadal aktualne
        expect = [" lda $260e,x", " cmp $b5", " bcc cull_fallback", " inx", " cpx $95", " bcc cull_scan",
                  " ldx $60", " jmp $9900"]
        assert lines[i + 1:i + 9] == expect, lines[i + 1:i + 9]
        out += ["; Opus: skan grupami po 4 kolumny"] + scan4("cull_scan", "cull_fallback") + [" ldx $60", " jmp $9900"]
        i += 9
        continue
    if ln.strip() == "jmp cull_entry":
        out.append(ln)
        for d in DEPTHS:
            out += hidden(d)
        i += 1
        continue
    out.append(ln)
    i += 1
assert done == set(DEPTHS), done

# --- Opus: niebo bez kasowania (LAZY) -------------------------------------------------------------
# Każdy piksel gór: przed `LDY $3900,X` jest Y = wysokość h (po obcięciu do $97). Jeśli h >= HD[kolumna]
# (próg $0100+Y = 152 - D, D = pierwszy wiersz, od którego bufor jest wyczyszczony), w kolumnie zostało
# stare niebo ($55) w wierszach, w które ten piksel (i dalsze) trafiają: lazy5 zeruje je i podnosi próg.
LAZY = "--nolazy" not in sys.argv
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from skylib import lazy  # noqa: E402
LAZY5 = ["; Opus: leniwe zerowanie starego nieba (skylib.lazy)"] + lazy("lazy5")
PLOTCHK = ["; Opus: wariant zimny (dg, dentry): JSR w miejsce LDY $3900,X, Y = h na wejściu.",
           "plotchk", " tya", " ldy $3900,x", " cmp $0100,y", " bcc pcx", " jmp lazy5", "pcx", " rts"]
if LAZY:
    # 1) kod d4 z obszaru za $990A przenosimy do dziury przed cull_entry (końcowy obszar jest pełny)
    r3 = next(i for i, l in enumerate(out) if l.strip().startswith(":($990a-*)"))
    end3 = next(i for i in range(r3, len(out)) if out[i].strip() == "ert * > $9fff")
    cut = next(i for i in range(r3, end3) if out[i].startswith("d4_"))
    prev = next(out[j] for j in range(cut - 1, r3, -1) if out[j].startswith(" "))
    assert prev.strip().upper().startswith("JMP"), prev
    moved = out[cut:end3]
    last = next(l for l in reversed(moved) if l.startswith(" "))
    assert last.strip().upper().startswith("JMP"), last
    out = out[:cut] + out[end3:]
    ce = out.index("cull_entry")
    out = out[:ce] + ["; --- Opus: kod d4 przeniesiony z obszaru za $990A ---"] + moved + out[ce:]
    # 2) wstawki w miejscach pikseli
    text = "\n".join(out)
    res = []; n = 0; depth = None; in_w2 = False; stubs = {}
    kinds = {"v9": 0, "v6": 0, "vj": 0}
    for k, ln in enumerate(out):
        m = re.match(r"^(d\d|dg|dentry)_", ln)
        if m:
            depth = m.group(1)
        if re.match(r"^\s+BNE (d\d)_99b9$", ln):
            in_w2 = True
        if re.match(r"^d\d_99b9$", ln):
            in_w2 = False
        if ln.strip() == "LDY $3900,X":
            j = k - 1
            while not out[j].startswith(" "):           # pomiń etykiety
                lab = out[j].strip()
                # nikt nie może skakać na etykietę przy LDY (wtedy Y nie musi być wysokością)
                assert len(re.findall(rf"\b{re.escape(lab)}\b", text)) == 1, lab
                j -= 1
            assert out[j].strip() == "STA $81", out[k - 3:k + 1]
            if depth in ("dg", "dentry"):
                res += [" JSR plotchk"]; kinds["vj"] += 1
            elif in_w2:
                res += [" TYA", ln, " CMP $0100,Y", f" BCS lzs{n}", f"lzc{n}"]
                stubs.setdefault(depth, []).append(n); kinds["v6"] += 1
            else:
                res += [" TYA", ln, " CMP $0100,Y", f" BCC lzc{n}", " JSR lazy5", f"lzc{n}"]; kinds["v9"] += 1
            n += 1
            continue
        if ln == "cull_entry":
            res += LAZY5 + PLOTCHK
        res.append(ln)
    out = res
    # 3) odgałęzienia wariantu 6-bajtowego: przed głową pętli dD_9933 (za JMP $9900, poza przelotem)
    res = []
    for k, ln in enumerate(out):
        m = re.match(r"^(d\d)_9933$", ln)
        if m and m.group(1) in stubs:
            prev = next(out[j] for j in range(k - 1, 0, -1) if out[j].startswith(" "))
            assert prev.strip().upper().startswith("JMP"), prev
            for s in stubs[m.group(1)]:
                res += [f"lzs{s}", " JSR lazy5", f" JMP lzc{s}"]
        res.append(ln)
    out = res
    print("wstawki leniwego zerowania:", n, kinds)
open(OUT, "w").write("\n".join(out))
print("zapisano", OUT)
