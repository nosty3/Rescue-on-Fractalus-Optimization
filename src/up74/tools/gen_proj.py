"""Generator s2-proj: rzutowanie punktów terenu w banku 3 (runda 2, na wierzchu proj_loop Fable z bazy v11).
Pisze src/proj3.asm (bank 3 $963A-$9D7D). Woła go tools/patches_proj.py (wyrównanie powrotu zależy od banku 2).

Kontrakt jak dotąd (Fable, gen_fable.py): wejście bank 2 `jsr $984F` (lda #3 / sta $D500) -> bank 3 $9854, X = punkt.
Wyjście: $2400/$242D/$245A/$2487,X, flaga $10 w $24B4,X, $AE-$B2 jak po oryginalnym drugim dzieleniu, $B5 jak
oryginał (tylko ścieżki z przesunięciem), X zachowany, A/Y/flagi martwe; rzadka ścieżka widoczności -> $9847.
Zmiany wobec rundy 1:
- wejście bez `bcs pdisp` (prolog $87D3 ma własne lądowanie w $9FE3/$9FE8, patches_proj.py),
- $9F (licznik przesunięć) martwy: nikt go nie czyta przed zapisem (clip $8665/$9677, fill $9312), więc ścieżki
  bez przesunięcia (n = 0, ok. 75%) mają własne kopie dzielenia i nie piszą/czytają $9F; n > 0 = wspólna kopia
  dzielenia dla obu współrzędnych, $9F = n (1. współrzędna) albo n + 8 (2.),
- krok dzielenia: udane odejmowanie przechodzi dalej (bcc do rzadkiego cofnięcia poza tokiem),
- ostatni krok 1. dzielenia tylko porównuje (reszta 1. współrzędnej martwa: 2. ładuje $B0, $B1 pisze 2. ścieżka),
- skala X/Y z tablicy T[Q] = $80 + ((Q + Q>>1 + 1) >> 2) (strona $9700); ujemne: 0 - T[Q] (= $80 - f),
- poprawka Y z $270E wplecione w zapis Y (n2 = 0): Y16 = (T[Q] albo -T[Q]) + adj w jednym dodawaniu,
- flaga $10 w $24B4,X ustawiana na końcu (przed testem widoczności), nikt jej nie czyta w trakcie,
- |N| hi zostaje w A (bez tay/tya przy ładowaniu i w pętli normalizacji).
"""
import os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

TAB = 0x9E00  # tablica T (256 B, strona) w miejscu dawnego wypełnienia occ (bank 3 $9D88-$9F82)
OVF1, OVF2 = 0x9FC4, 0x9FEB  # przepełnienie 1. / 2. współrzędnej (8 przesunięć, rzadkie): wolne FF banku 3


def tvals():
    return [0x80 + ((q + (q >> 1) + 1) >> 2) for q in range(256)]


def step(tag, i, last_cmp=False, inline=False):
    """Krok i dzielenia. last_cmp: tylko bit ilorazu (reszta martwa)."""
    if last_cmp:
        return [" asl $b0", " rol @", " cmp $af", f" bcc {tag}z{i}", f" bne {tag}z{i}",
                " lda $b0", " cmp $ae", f"{tag}z{i}", " rol $b2"]
    if inline:  # cofnięcie w toku (udane odejmowanie skacze nad nim: +1 cykl), gdy blok poza tokiem nie sięga
        return [" asl $b0", " rol @", " cmp $af", f" bcc {tag}z{i}",
                " tay", " lda $b0", " sbc $ae", " sta $b0", " tya", " sbc $af", f" bcs {tag}z{i}",
                " lda $b0", " adc $ae", " sta $b0", " tya", " clc",
                f"{tag}z{i}", " rol $b2"]
    return [" asl $b0", " rol @", " cmp $af", f" bcc {tag}z{i}",
            " tay", " lda $b0", " sbc $ae", " sta $b0", " tya", " sbc $af", f" bcc {tag}u{i}",
            f"{tag}z{i}", " rol $b2"]


def undo(tag, i):
    # po nieudanym odejmowaniu (hi równe, lo za małe): C = 0, lo + Dlo = stare lo (C wychodzi 1), bit ilorazu 0
    return [f"{tag}u{i}", " lda $b0", " adc $ae", " sta $b0", " tya", " clc", f" jmp {tag}z{i}"]


def gen_proj3(pad=0):
    T = tvals()
    RB = [  # bloki rzadkie (tylko skoki), za tablicą prologu w banku 3 $9D88-$9F82 (patrz koniec)
         # --- normalizacja 1. współrzędnej: A = |N1| hi, $B0 = lo; D <<= 1 aż N < D (najwyżej 7 razy) ---
         "c1sh", " sta $b1",   # pierwsza iteracja rozwinięta (n = 1 najczęstsze)
         " asl $ae", " rol $af", " cmp $af", " bcc c1sh1", " bne c1sh2", " lda $b0", " cmp $ae", " lda $b1",
         " bcs c1sh2",
         "c1sh1", " ldy #1", " sty $9f", " jmp nkdiv",
         "c1sh2", " ldy #1",
         "c1shl", " asl $ae", " rol $af", " iny", " cpy #8", " beq c1ovfj",
         " cmp $af", " bcc c1divn", " bne c1shl", " lda $b0", " cmp $ae", " lda $b1", " bcs c1shl",
         "c1divn", " sty $9f", " jmp nkdiv",
         "c1ovfj", " jmp c1ovf",
         # --- normalizacja 2. współrzędnej (licznik od 8) ---
         "c2sh", " sta $b1", " ldy #8",
         "c2shl", " asl $ae", " rol $af", " iny", " cpy #16", " beq c2ovfj",
         " cmp $af", " bcc c2divn", " bne c2shl", " lda $b0", " cmp $ae", " lda $b1", " bcs c2shl",
         "c2divn", " sty $9f", " jmp nkdiv",
         "c2ovfj", " jmp c2ovf",
         ]
    RB2 = [  # --- 1. współrzędna, n >= 2 (z nkdiv: jmp c1nk, Y = n - 1) ---
         "c1nk", " jsr rcalc",
         " lda $22d2,x", " bmi c1ynn",
         " lda #$80", " clc", " adc $b2", " sta $2400,x", " lda $b5", " adc #0", " sta $242d,x", " jmp c2reload",
         "c1ynn", " lda #$80", " sec", " sbc $b2", " sta $2400,x", " lda #0", " sbc $b5", " sta $242d,x",
         " jmp c2reload",
         ]
    TABL = ["; ===== T[Q] = $80 + ((Q + Q>>1 + 1) >> 2) =====", "tab"] + \
        [" dta " + ",".join(f"${v:02x}" for v in T[k:k + 16]) for k in range(0, 256, 16)]
    L = ["; s2-proj: rzutowanie punktów terenu (bank 3). Generuje tools/gen_proj.py - nie edytować ręcznie.",
         "; Bank 3 $963A-$97F0 zostaje $FF jak w masterze: kod przed lotem czyta te bajty (zmiana zmienia RAM na wejściu",
         "; do lotu, bisekcja w Altirze: s2proj/bis.py). Obszar: $97F1-$9F82 (wyspy $9847-$9853 i $9D7E-$9D84 bez zmian).",
         " opt h-",
         f"c1ovf = ${OVF1:04x}", f"c2ovf = ${OVF2:04x}",   # bloki przepełnienia w wolnych FF na końcu banku 3
         " org $97f1",
         " :($9800-*) dta $ff",
         "; ===== $9800: wejścia rzadkie 1. współrzędnej + cofnięcia kroków 0-2 (zasięg gałęzi z dzielenia) =====",
         "c1ge",              # hi >= Dhi: hi > -> normalizacja; hi = i lo < Dlo -> n = 0
         " bne c1shj", " ldy $b0", " cpy $ae", " bcs c1shj", " jmp div1",
         "c1shj", " jmp c1sh",
         "c2reload", " lda $2300,x", " sta $ae", " lda $232e,x", " sta $af", " jmp c2noreload",
         " ert * > $9847-33",
         " :($9847-33-*) dta $ff",   # bloki cofnięć jak najbliżej dzielenia
         ] + undo("a", 0) + undo("a", 1) + undo("a", 2) + [
         " ert * > $9847",
         " :($9847-*) dta $ff",
         "; $9847: rzadka ścieżka widoczności -> bank 2 $984C (jmp $8AF8); X = punkt, Y = $2276,X",
         " lda #2", " sta $d500",
         " jmp $9f86",        # $984C: s2-reorder tail3 (nieużywane od s2-proj: prolog wchodzi przez $9FE8)
         " lda #2", " sta $d500",  # $984F: koniec prologu (tail3 jmp $984F) -> bank 2 $9854 jmp $85D4
         " ert * <> $9854",
         "; ===== $9854: rzutowanie (X = punkt) =====",
         "proj",
         " lda $2300,x", " sta $ae", " lda $232e,x", " sta $af",
         " lda $22a4,x", " sta $b0", " lda $22d2,x", " bpl c1cmp",
         " lda #0", " sec", " sbc $b0", " sta $b0", " lda #0", " sbc $22d2,x",
         "c1cmp", " cmp $af", " bcs c1ge",
         "div1"]
    for i in range(7):
        L += step("a", i)
    L += step("a", 7, last_cmp=True)
    L += ["; 1. współrzędna, n = 0: X = T[Q] albo 0 - T[Q], hi 0",
          " ldy $b2", " lda $22d2,x", " bpl c1p",
          " lda #0", " sec", " sbc tab,y", " sta $2400,x", " lda #0", " sta $242d,x", " jmp c2noreload"]
    L += undo("a", 3) + undo("a", 4) + undo("a", 5) + undo("a", 6)
    L += ["c2ge",            # 2. współrzędna: hi >= Dhi
          " bne c2shj", " ldy $b0", " cpy $ae", " bcs c2shj", " jmp div2",
          "c2shj", " jmp c2sh",
          ] + undo("b", 0) + undo("b", 1) + undo("b", 2) + [
          f" :{pad} dta $ff",  # wyrównanie powrotu (patches_proj.py): bajty nieosiągalne (przeskakuje je bpl c1p)
          "c1p", " lda tab,y", " sta $2400,x", " lda #0", " sta $242d,x",
          "c2noreload", " lda $235b,x", " sta $b0", " lda $2388,x", " bpl c2cmp",
          " lda #0", " sec", " sbc $b0", " sta $b0", " lda #0", " sbc $2388,x",
          "c2cmp", " cmp $af", " bcs c2ge",
          "div2"]
    for i in range(8):
        L += step("b", i, inline=(i >= 3))
    L += ["; 2. współrzędna, n = 0: Y16 = (+-T[Q]) + adj ($270E[X >> 3]) jednym dodawaniem",
          " sta $b1",
          " lda $2388,x", " bpl c2p",
          " lda $242d,x", " bne c2nx",
          " lda $2400,x", " lsr @", " lsr @", " lsr @", " tay", " lda $270e,y", " bmi c2nm",
          " ldy $b2", " sec", " sbc tab,y", " sta $245a,x", " lda #0", " adc #0", " sta $2487,x",
          "vis",
          " lda $24b4,x", " ora #$10", " sta $24b4,x",
          " ldy $2276,x", " lda $0a00,y", " bne rare",
          "ret", " lda #2", " sta $d500",   # -> bank 2: pod ret+5 musi być rts (sprawdza patches_proj.py)
          "; ===== za przełącznikiem: tylko gałęzie i skoki =====",
          "rare", " jmp $9847",
          "c2nx", " ldy $b2", " lda #0", " sec", " sbc tab,y", " sta $245a,x", " lda #0", " sta $2487,x",
          " lda $242d,x", " jmp adjx",
          "c2nm", " ldy $b2", " sec", " sbc tab,y", " sta $245a,x", " lda #$ff", " adc #0", " sta $2487,x", " jmp vis",
          "c2p",
          " lda $242d,x", " bne c2px",
          " lda $2400,x", " lsr @", " lsr @", " lsr @", " tay", " lda $270e,y", " bmi c2pm",
          " ldy $b2", " clc", " adc tab,y", " sta $245a,x", " lda #0", " adc #0", " sta $2487,x", " jmp vis",
          "c2pm", " ldy $b2", " clc", " adc tab,y", " sta $245a,x", " lda #$ff", " adc #0", " sta $2487,x", " jmp vis",
          "c2px", " ldy $b2", " lda tab,y", " sta $245a,x", " lda #0", " sta $2487,x", " lda $242d,x", " jmp adjx",
          ]
    L += ["; ===== ogólna poprawka Y (ścieżki n > 0 i przepełnienia): jak oryginał $8792 =====",
          "adjust", " lda $242d,x", " bne adjx",
          " lda $2400,x", " lsr @", " lsr @", " lsr @", " tay", " lda $270e,y", " bmi adjm",
          "adjp", " clc", " adc $245a,x", " sta $245a,x", " lda $2487,x", " adc #0", " sta $2487,x", " jmp vis",
          "adjx", " bmi adjneg", " lda $272d", " bmi adjm", " bpl adjp",
          "adjneg", " lda $270e", " bmi adjm", " bpl adjp",
          "adjm", " clc", " adc $245a,x", " sta $245a,x", " lda $2487,x", " adc #$ff", " sta $2487,x", " jmp vis",
          ] + undo("c", 0) + undo("c", 1) + undo("c", 2) + undo("c", 3) + [
          "; ===== dzielenie z przesunięciem n > 0 (obie współrzędne); $9F = n albo n + 8 =====",
          "nkdiv"]
    for i in range(8):
        L += step("c", i)
    L += [" sta $b1",            # 1. współrzędna: martwe (2. nadpisze), 2.: reszta hi jak oryginał
          " ldy $9f", " cpy #8", " bcs c2nkj", " dey", " beq c1n1", " jmp c1nk",
          "c2nkj", " jmp c2nk",
          ] + undo("c", 4) + undo("c", 5) + undo("c", 6) + undo("c", 7) + [
          "; 1. współrzędna, n > 0: V = Q << n, r = (V + V>>1) >> 2 (16 bitów), X = $80 +- r (jak oryginał c1yn)",
          "; n = 1: r = floor(3Q/4) = (Q + Q>>1) >> 1 (suma 9-bitowa), $B5 = 0; X = $80 +- r",
          "c1n1", " lda $b2", " lsr @", " clc", " adc $b2", " ror @", " sta $b2", " sty $b5",
          " ldy $22d2,x", " bmi c1n1n",
          " clc", " adc #$80", " sta $2400,x", " lda #0", " adc #0", " sta $242d,x", " jmp c2reload",
          "c1n1n", " lda #$80", " sec", " sbc $b2", " sta $2400,x", " lda #0", " sbc #0", " sta $242d,x",
          " jmp c2reload",
          "c2nk", " cpy #9", " bne c2nkg",
          " lda $b2", " lsr @", " clc", " adc $b2", " ror @", " sta $b2", " ldy #0", " sty $b5",
          " ldy $2388,x", " bmi c2n1n",
          " clc", " adc #$80", " sta $245a,x", " lda #0", " adc #0", " sta $2487,x", " jmp adjust",
          "c2n1n", " lda #$80", " sec", " sbc $b2", " sta $245a,x", " lda #0", " sbc #0", " sta $2487,x",
          " jmp adjust",
          "c2nkg", " tya", " sbc #9", " tay", " jsr rcalc",   # C = 1 po cpy #9 (Y >= 10); Y = n - 1
          " lda $2388,x", " bmi c2ynn",
          " lda #$80", " clc", " adc $b2", " sta $245a,x", " lda $b5", " adc #0", " sta $2487,x", " jmp adjust",
          "c2ynn", " lda #$80", " sec", " sbc $b2", " sta $245a,x", " lda #0", " sbc $b5", " sta $2487,x",
          " jmp adjust",
          ]
    L += [  # --- n >= 2: r = (V + V>>1) >> 2, V = Q << n (oryginał c1yn/c2yn) = floor(3Q * 2^n / 8) dokładnie
          # (V parzyste): n = 2: Q + Q>>1 (9 bitów), n >= 3: 3Q << (n - 3). Wyjście $B5:$B2 = r (jak oryginał).
          # Wejście: Y = n - 1 (>= 1).
          "rcalc", " dey", " bne rc3",
          " lda $b2", " lsr @", " clc", " adc $b2", " sta $b2", " lda #0", " rol @", " sta $b5", " rts",
          "rc3", " lda #0", " sta $b5", " lda $b2", " asl @", " rol $b5", " adc $b2", " sta $b2", " bcc rc3a",
          " inc $b5",
          "rc3a", " dey", " beq rc3d",
          "rc3l", " asl $b2", " rol $b5", " dey", " bne rc3l",
          "rc3d", " rts",
          " ert * > $9d7e", " :($9d7e-*) dta $ff",
          "; $9D7E-$9D84 bez zmian (stary prolog3: stx $a7; hop14: lda #14 / sta $D500 -> bank 14)",
          " dta $86,$a7,$a9,$0e,$8d,$00,$d5",
          "; $9D85: powrót z banku 14 (wypełnienie occ $263A-$26E1 przeniesione do banku 14) -> koniec części tablicowej",
          " jmp $9f83",
          ] + RB + [f" ert * > ${TAB:04x}", f" :(${TAB:04x}-*) dta $ff"] + TABL + RB2 + [
          " ert * > $9f83", " :($9f83-*) dta $ff"]
    return "\n".join(L) + "\n"


FILL_CHUNKS = [(0x973E, 0x9800), (0x9D88, 0x9E00), (0x9F00, 0x9FFF)]  # wolne FF banku 14


def gen_fill14():
    """Bank 14: wypełnienie occ jak oryginał $8802-$8821 (wcześniej bank 3 $9D85-$9F82, Fable fill_seq):
    $263A-$264D $67, $264E-$26D1 $6B, $26D2-$26E1 $67; w trzech kawałkach wolnych FF, na końcu jmp $9D80 (HOP).
    Zwraca listę (org, źródło)."""
    seq = [("lda", 0x67)] + [("sta", a) for a in range(0x263A, 0x264E)]
    seq += [("lda", 0x6B)] + [("sta", a) for a in range(0x264E, 0x26D2)]
    seq += [("lda", 0x67)] + [("sta", a) for a in range(0x26D2, 0x26E2)]
    out = []; i = 0
    for k, (lo, hi) in enumerate(FILL_CHUNKS):
        L = ["; s2-proj: wypełnienie occ (prolog), bank 14. Generuje tools/gen_proj.py.", " opt h-", f" org ${lo:04x}"]
        size = 0
        while i < len(seq):
            n = 2 if seq[i][0] == "lda" else 3
            if lo + size + n + 3 > hi:
                break
            L.append(f" lda #${seq[i][1]:02x}" if seq[i][0] == "lda" else f" sta ${seq[i][1]:04x}")
            size += n; i += 1
        nxt = FILL_CHUNKS[k + 1][0] if i < len(seq) else 0x9D80
        L += [f" jmp ${nxt:04x}", f" ert * > ${hi:04x}"]
        out.append((lo, "\n".join(L) + "\n"))
        if i == len(seq):
            break
    assert i == len(seq)
    return out


def gen_prolog_stub2():
    """Bank 2 $9FE3: lądowanie prologu $87D3 (jmp $9FE3) -> bank 3 $9FE8 jmp tail3 ($9F86)."""
    return "\n".join(["; s2-proj: wejście prologu $87D3 bez `bcs` w rzutowaniu. Generuje tools/gen_proj.py.",
                      " opt h-", " org $9fe3", " lda #3", " sta $d500", " ert * <> $9fe8"]) + "\n"


def gen_ovf1(c2reload):
    """Bank 3 $9FC4-$9FD9: 1. współrzędna po 8 przesunięciach: X = $4000 / $C000 ($B1, $B2 jak oryginał)."""
    return "\n".join(["; s2-proj: przepełnienie 1. współrzędnej. Generuje tools/gen_proj.py.", " opt h-",
                      f" org ${OVF1:04x}", " lda #$40", " ldy $22d2,x", " bpl o1", " lda #$c0",
                      "o1", " sta $242d,x", " lda #0", " sta $2400,x", f" jmp ${c2reload:04x}",
                      " ert * > $9fda"]) + "\n"


def gen_prolog_stub3(adjust):
    """Bank 3 $9FE8: lądowanie prologu z banku 2 $9FE3 -> tail3; $9FEB: przepełnienie 2. współrzędnej."""
    return "\n".join(["; s2-proj: bank 3 $9FE8 (lądowanie z banku 2 $9FE3) -> tail3, $9FEB przepełnienie 2. współrzędnej.",
                      "; Generuje tools/gen_proj.py.", " opt h-", " org $9fe8", " jmp $9f86",
                      f" ert * <> ${OVF2:04x}",
                      " lda #$40", " ldy $2388,x", " bpl o2", " lda #$c0",
                      "o2", " sta $2487,x", " lda #0", " sta $245a,x", f" jmp ${adjust:04x}",
                      " ert * > $9fff"]) + "\n"


# bank 2: początek pętli (jedna strona: gałęzie bez +1); tablice par P1R/P2R (72 + 72 B, jedna strona) w martwym
# starym dzieleniu $8224-$8303 (wołane tylko przez stare rzutowanie $8719, nieużywane od proj_loop Fable), za nimi
# (FNB) rzadki koniec pętli, gdy żadna para nie przeszła obu testów
LP, TABS = 0x8600, 0x8224
FNB = TABS + 144


def gen_fnb(fdone):
    """Bank 2 $82B4: koniec pętli bez pary po obu testach. $28DB = stare $272E, $272E = $FF (żadna para)."""
    L = ["; s2-proj: rzadki koniec pętli krawędzi (żadna para po obu testach). Generuje tools/gen_proj.py.",
         " opt h-", f"P1R = ${TABS:04x}", f" org ${FNB:04x}",
         " ldy #72",                              # ostatnia para po teście p1 wśród wszystkich
         "fn", " dey", " bmi fnd",
         " ldx P1R,y", " lda $24b4,x", " and #$a0", " bne fn", " sty $272e", " beq fn",
         "fnd", " ldy $272e", " cpy #$ff", " bne fn1",
         " lda $28db", " sta $272e", " jmp fn2",  # żadna: $272E stare
         "fn1", " tya", " asl @", " eor #$ff", " sec", " adc #144", " sta $272e",
         "fn2",                                   # X jak pętla Fable: ostatni ładowany punkt (para 71: p1, p2 gdy p1 przeszło)
         f" ldx ${TABS:04x}", " lda $24b4,x", " and #$a0", " bne fn3", f" ldx ${TABS + 72:04x}",
         "fn3", " ldy #0", f" jmp ${fdone:04x}",
         " ert * > $8304"]
    return "\n".join(L) + "\n"


def gen_pairtabs(pairs):
    P1R = [pairs[71 - y][0] for y in range(72)]
    P2R = [pairs[71 - y][1] for y in range(72)]
    return "\n".join(["; s2-proj: tablice par pętli krawędzi, odwrócone (P1R[Y] = p1 pary 71 - Y). Generuje tools/gen_proj.py.",
                      " opt h-", f" org ${TABS:04x}"]
                     + [" dta " + ",".join(f"${v:02x}" for v in P1R[k:k + 12]) for k in range(0, 72, 12)]
                     + [" dta " + ",".join(f"${v:02x}" for v in P2R[k:k + 12]) for k in range(0, 72, 12)]
                     + [" ert * > $8300"]) + "\n"


def gen_loop2(pairs):
    """Bank 2 $85D4-$87D2: pętla krawędzi (zamiast pętli Fable). pairs = 72 pary (p1, p2) z tablicy $9B09.
    Indeks Y = 71..0 (dey/bpl) po tablicach odwróconych P1R/P2R (P1R[Y] = p1 pary 71 - Y). W clipie X = p2,
    Y = p1 (bez kopiowania p1 do $82-$86 na szybkiej ścieżce; kopie tylko przed ścieżkami ogólnymi).
    Stan jak pętla Fable: $272E = indeks za p2 ostatniej pary po teście p1 (2k + 2), $28DB = 43, $82-$86 jak po
    ostatniej parze po obu testach (ustalane na końcu z jej danych), kopie p2 tej pary w $25B4.., na wyjściu
    A = 43, X = p2 (albo ostatni ładowany punkt), Y = 2k + 2 (albo 0), C = 1."""
    assert len(pairs) == 72
    P1R = [pairs[71 - y][0] for y in range(72)]
    P2R = [pairs[71 - y][1] for y in range(72)]
    L = ["; s2-proj: pętla krawędzi terenu (bank 2 $85D4-$87D2). Generuje tools/gen_proj.py - nie edytować ręcznie.",
         " opt h-",
         f"P1R = ${TABS:04x}", f"P2R = ${TABS + 72:04x}",
         " org $85d4",
         " lda $272e", " pha",                   # stare $272E (zostaje, gdy żadna para nie przejdzie testu p1)
         " lda #$ff", " sta $272e",              # $272E: Y ostatniej pary po obu testach ($FF = brak)
         " ldy #71", " jmp lp",
         f" ert * > ${LP:04x}", f" :(${LP:04x}-*) dta $ff",
         "lp",
         " ldx P1R,y", " lda $24b4,x", " and #$a0", " bne next",       # p1: bit 7 albo 5 -> pomiń parę
         " ldx P2R,y", " lda $24b4,x", " cmp #$40", " bcs next",        # p2: bit 7 albo 6 -> pomiń
         " sty $272e",
         " and #$10", " bne p2ok", " jsr $984f", " ldy $272e",          # rzutowanie p2 (bank 3), X = p2 zachowany
         "p2ok",
         " lda P1R,y", " tay", " lda $24b4,y", " and #$10", " beq p1proj",
         "p1ok",                                                        # X = p2, Y = p1
         " lda $242d,y", " ora $2487,y", " ora $242d,x", " ora $2487,x", " bne cgen",
         " lda $2400,y", " cmp $2400,x", " bcs nextr",                  # x1 >= x2: nic
         " cmp #$d8", " bcs nextr",
         " lda $245a,y", " cmp #$6c", " bcc cy1lt",
         " lda $245a,x", " cmp #$6c", " bcc c974a",
         " sta $ea", " lda $2400,x", " sta $95", " lda $23b5,x", " sta $f4",   # R = p2
         " lda $2400,y", " sta $82", " lda $245a,y", " sta $84", " lda $23b5,y", " sta $86",  # L = p1
         " ldx #0", " jsr $982a",                                       # rasteryzacja (bank 5), powrót przez $9909
         "nextr", " ldy $272e",
         "next", " dey", " bpl lp",
         " jmp fin",
         "p1proj", " tya", " tax", " jsr $984f", " ldy $272e", " ldx P2R,y", " lda P1R,y", " tay", " jmp p1ok",
         "cy1lt", " lda $245a,x", " cmp #$6c", " bcc nextr", " jsr cpy12", " jsr $972e", " jmp nextr",
         "c974a", " jsr cpy12", " jsr $974a", " jmp nextr",
         "cgen",                                                        # jak $9627: x1 < x2 (16 bitów ze znakiem)
         " jsr cpy12",
         " lda $25d2", " eor #$80", " sta $b5", " lda $83", " eor #$80", " cmp $b5", " bne cg1",
         " lda $82", " cmp $25b4",
         "cg1", " bcs nextr", " jsr $83bb", " jmp nextr",
         "; p1 (Y) -> $82-$86, $9F = $14, p2 (X) -> $25B4.., X = 0 (wejście ścieżek ogólnych clipu)",
         "cpy12",
         " lda $2400,y", " sta $82", " lda $242d,y", " sta $83", " lda $245a,y", " sta $84",
         " lda $2487,y", " sta $85", " lda $23b5,y", " sta $86",
         " lda #$14", " sta $9f",
         " lda $2400,x", " sta $25b4", " lda $242d,x", " sta $25d2", " lda $245a,x", " sta $25f0",
         " lda $2487,x", " sta $24e2", " lda $23b5,x", " sta $23e2", " ldx #0", " rts",
         "; koniec: stan jak pętla Fable ($272E = 2k + 2 ostatniej pary po teście p1, X, Y, $82-$86, kopie p2)",
         "fin",
         " pla", " sta $28db",                    # stare $272E (tymczasowo; na końcu $28DB = 43)
         " ldy $272e", " cpy #$ff", " bne fb1", f" jmp ${FNB:04x}",
         "fb1", " ldx P2R,y", " lda P1R,y", " tay",   # X = p2, Y = p1 ostatniej pary po obu testach
         " lda $242d,y", " ora $2487,y", " ora $242d,x", " ora $2487,x", " bne fcp",   # ogólna: $82-$86 gotowe
         " lda $2400,y", " cmp $2400,x", " bcs frej", " cmp #$d8", " bcs frej",
         " lda $245a,y", " cmp #$6c", " bcs fy1h",
         " lda $245a,x", " cmp #$6c", " bcc frej", " bcs fcp",          # $972E: kopie były
         "fy1h", " lda $245a,x", " cmp #$6c", " bcc fcp",              # $974A: kopie były
         " lda #0", " sta $83", " sta $85", " beq fcp",                # rasteryzacja: $82/$84/$86 jej, hi = 0
         "frej", " lda $2400,y", " sta $82", " lda $245a,y", " sta $84", " lda $23b5,y", " sta $86",
         " lda #0", " sta $83", " sta $85",
         "fcp", " jsr copies",
         " txa", " pha",                          # X = p2 (wynik)
         " ldy $272e", " tya", " pha",            # Y ostatniej pary po obu testach
         # ostatnia para po teście p1 = najniższe Y <= Yb z p1 po teście (pary dalej niż Yb nic nie zmieniały)
         " sty $28db",
         "fs", " dey", " bmi fsd",
         " ldx P1R,y", " lda $24b4,x", " and #$a0", " bne fs", " sty $28db", " beq fs",
         "fsd", " lda $28db", " asl @", " eor #$ff", " sec", " adc #144", " sta $272e",   # 2k + 2 = 144 - 2Y
         " pla", " asl @", " eor #$ff", " sec", " adc #144", " tay",
         " pla", " tax",
         "fdone", " lda #43", " sta $28db", " sec", " jmp $88e8",
         "; kopie p2 (X) do $25B4/$25D2/$25F0/$24E2/$23E2 jak oryginał",
         "copies",
         " lda $2400,x", " sta $25b4", " lda $242d,x", " sta $25d2", " lda $245a,x", " sta $25f0",
         " lda $2487,x", " sta $24e2", " lda $23b5,x", " sta $23e2", " rts",
         " ert * > $87d3", " :($87d3-*) dta $ff"]
    return "\n".join(L) + "\n"


if __name__ == "__main__":
    open(f"{ROOT}/src/proj3.asm", "w", encoding="utf-8").write(gen_proj3())
    print("zapisano src/proj3.asm")
