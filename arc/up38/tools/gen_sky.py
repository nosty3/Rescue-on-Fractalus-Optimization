"""Niebo bez kasowania: generuje
  src/sky_b6.asm, src/sky_b8.asm - kasowanie bufora X=3 / X=51 tylko od granicy nieba w dół (łańcuch zapisów
      na kolumnę, wejście wyliczane z progu), bank 8 dodatkowo procedura stawiania piksela obiektów ($8B80),
  src/sky_b9.asm - fill nosty3 (fill_rows.asm) ze skanem od granicy i zapisem $55 tylko w pasie [D, r0).

Stan (RAM strony 1, wolny - test zatruwania i pułapki zapisu):
  $0100+y  HD[y] = 152 - D[y] dla kolumny bajtów y (z przesunięciem bufora: 3..44 bufor A, 51..92 bufor B);
           D = pierwszy wiersz, od którego bufor jest wyzerowany (rysowanie/fill); wiersze 1..D-1 = niebo $55,
           wiersz 0 = 0. Pozostałe y = $FF (nigdy nie wyzwala zerowania).
  $0160-$0165 scratch, $0167 = 1 w trakcie rysowania (od kasowania do początku fillu), $0168/$0169 ważność
  bufora A/B ($A5 = stan zgodny; poza trybem lotu $4A=2 albo po starcie gry -> pełne kasowanie).
"""
import os, re
from paths import NOSTY
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FILL_SRC = f"{NOSTY}/src/fill_rows.asm"
BOTTOM = ([0x2090 + k for k in range(5)] + [0x20BA - k for k in range(6)] + [0x20F0 + k for k in range(4)] +
          [0x211A - k for k in range(5)] + [0x2150 + k for k in range(3)] + [0x217A - k for k in range(4)] +
          [0x21B0, 0x21DA, 0x21B1, 0x21D9, 0x21D8])
UNUSED = [0, 1, 2] + list(range(45, 51)) + [93, 94, 95]
VFLAG = {3: 0x0168, 51: 0x0169}
CHAIN = 132                         # 43 x sta abs + jmp


from skylib import lazy  # noqa: E402


def obj_code():
    """Bank 8, $8B80-$8C4F: piksel obiektu (oryginał bank 2 $8B80) + niebo. Bank 2 przy $8B80 przełącza na 8."""
    # Bank 2 (łatka sky): $8B80 lda #8/sta $d500 (wejście 1, z testem zasłaniania), $8B88 sta $0166/lda #8/
    # sta $d500 (wejście 2 bez testu, wołane z $8FAC i $8FF4), lądowania: $8B90 powrót bez piksela z wejścia 1,
    # $8B9B bez piksela z wejścia 2, $8BA1 z pikselem. Tu w banku 8 kontynuacje i końcówki "lda #2/sta $d500"
    # kończące się dokładnie pod adresami lądowań.
    return [
        " :($8b85-*) dta $ff",
        " jmp obj",                                    # $8B85: kontynuacja wejścia 1
        " :($8b8b-*) dta $ff",
        "o_ret_s1", " lda #2", " sta $d500",          # $8B8B-$8B8F -> bank 2 $8B90
        " jmp obj2",                                   # $8B90: kontynuacja wejścia 2
        " :($8b96-*) dta $ff",
        "o_ret_s2", " lda #2", " sta $d500",          # $8B96-$8B9A -> bank 2 $8B9B
        " :($8b9c-*) dta $ff",
        "o_ret_p", " lda #2", " sta $d500",           # $8B9C-$8BA0 -> bank 2 $8BA1
        "; Piksel obiektu: wejście 1 tylko nad bieżącym zasłanianiem (h > occ); oba wejścia tylko h < $97.",
        "obj", " tya", " cmp $260e,x", " bcc oskip", " beq oskip", " cpy #$97", " bcs oskip", " bcc obody",
        "obj2", " cpy #$97", " bcs oskip2",
        "obody", " sty $28e2", " lda $28ca,y", " sta $80", " lda $28fa,y", " sta $81",
        " ldy $3900,x",
        " lda $28e2", " cmp $0100,y", " bcc ook",       # piksel pod granicą nieba: nic do zrobienia
        " lda $0167", " beq omark",
        " lda $28e2", " jsr lazy8", " jmp ook",         # w trakcie rysowania: wyzeruj stare niebo
        "; po fillu (strzały, obiekty): bajty nieba zostają brudne -> obniż granicę, wyczyści następne kasowanie",
        "omark", " lda $28e2", " php", " clc", " adc #1", " plp", " sta $0100,y",
        "ook", " lda $3800,x", " sta $b5", " lsr", " ora $b5", " and $58", " ora ($80),y", " sta ($80),y",
        " sta $0165", " jmp o_ret_p",
        "oskip", " jmp o_ret_s1",
        "oskip2", " jmp o_ret_s2",
    ] + [" ert * > $8c50"]


def clear_bank(x0, bank):
    L = [f"; Kasowanie bufora X={x0} od granicy nieba (bank {bank}). Generuje gen_sky.py.", " opt h-", " org $8000"]
    ch = []

    def chains(cs):
        for c in cs:
            L.append(f"ch{c}")
            L.extend(f" sta ${0x1010 + 96 * r + x0 + c:04x}" for r in range(1, 44))
            L.append(f" jmp rt{c}")
    chains(range(22))
    L.append(" ert * > $8b80")
    if bank == 8:
        L.append(" :($8b80-*) dta $ff")
        L.extend(obj_code())
    L.append(" :($8c50-*) dta $ff")
    chains(range(22, 42))
    if bank == 8:
        L += lazy("lazy8")
    L += [" ert * > $9863", " :($9863-*) dta $ff", " plp", " jmp seg1",
          " :($98f0-*) dta $ff", " php", " pha", " lda #2", " sta $d500", " ert * <> $98f7"]
    v = VFLAG[x0]
    L += ["seg1", " stx $94",
          " ldy $4a", " cpy #2", " bne full", f" ldy ${v:04x}", " cpy #$a5", " bne full", " jmp go",
          "; stan nieznany: D = 1 dla wszystkich kolumn = pełne kasowanie jak w oryginale",
          "full", " lda #151"] + [f" sta ${0x100 + x0 + c:04x}" for c in range(42)] + \
         [" lda #$ff"] + [f" sta ${0x100 + u:04x}" for u in UNUSED] + \
         ["go", " lda #0", f" sta ${v:04x}", " lda #1", " sta $0167"]
    for c in range(42):
        L += [f" ldy ${0x100 + x0 + c:04x}", f" lda #<ch{c}", " clc", " adc t3-108,y", " sta $80",
              f" lda #>ch{c}", " adc #0", " sta $81", " lda #0", " jmp ($80)", f"rt{c}"]
    L += [f" sta ${0x1010 + x0 + c:04x}" for c in range(42)]          # wiersz 0 zawsze
    L += [f" sta ${a + x0:04x}" for a in BOTTOM]                       # brzegi wierszy 44-47 jak oryginał
    L += [" ldy #0", " ldx $94", " jmp $98f0",
          "t3", " dta " + ",".join(str(3 * (151 - hd)) for hd in range(108, 152)),
          " ert * > $9fff", " :($9fff-*) dta $ff", f" dta {bank}"]
    open(f"{ROOT}/src/sky_b{bank}.asm", "w").write("\n".join(L) + "\n")


def fill_bank():
    L = open(FILL_SRC).read().split("\n")
    out = []
    first_scan_end = L.index("first_0")
    i = 0
    while i < len(L):
        ln = L[i]
        if ln == "entry":
            assert L[i + 1:i + 3] == [" txa", " tay"]
            out += [ln, " txa", " tay", " lda #0", " sta $0167"]           # koniec fazy rysowania
            i += 3; continue
        if ln == "column":
            assert L[i + 1:i + 5] == [" lda #0", " cmp $1010,y", " beq group_1", " jmp first_0"]
            out += [ln, " lda #0", " cmp $1010,y", " bne col_f0", " jmp sky_go", "col_f0", " jmp first_0"]
            i += 5; continue
        m = re.match(r"\s+cmp \$([0-9a-f]{4}),y$", ln)
        if m and i < first_scan_end:
            r = (int(m.group(1), 16) - 0x1010) // 96
            if 1 <= r <= 44:
                out.append(f"fs_{r}")
            out.append(ln); i += 1; continue
        if ln == "first_0":
            assert L[i + 1] == " lda #$55"
            out += [ln, " lda #151", " sta $0100,y"]                    # D = 1
            i += 2; continue
        m = re.match(r"^first_(\d+)$", ln)
        if m:
            r = int(m.group(1))
            assert L[i + 1] == " lda #$55", (ln, L[i + 1])
            # pas $55 w wierszach [D, r): łańcuch bk od wiersza r-1 w górę ekranu (X = D, wyjście co 4 wiersze;
            # nadmiarowe zapisy trafiają w wiersze < D, które już są $55). Potem HD := 152 - min(r, 44).
            band = ([" lda #152", " sec", " sbc $0100,y", " tax", f" cpx #{r}", f" bcs fb{r}",
                     " lda #$55", f" jsr bk{r-1}", f"fb{r}"] if r > 1 else []) +                    [f" lda #{152 - min(r, 44)}", " sta $0100,y"]
            if r <= 32:
                k = i + 2; n = 0
                while re.match(r"\s+sta \$[0-9a-f]{4},y$", L[k]):
                    n += 1; k += 1
                assert n == r - 1, (r, n)
                out += [ln] + band
                i = k; continue
            assert L[i + 2] == f" ldx #{r}" and L[i + 3] == f" jmp sky_{r-1}", L[i:i + 4]
            out += [ln] + band + [f" ldx #{r}", " jmp sky_tail"]
            i += 4; continue
        if ln == "sky_1":
            assert L[i + 1] == " sta $1070,y"
            out += [ln, L[i + 1], "sky_tail"]
            i += 2; continue
        if ln == "done":
            assert L[i + 1] == " jmp $9ff0"
            out += [ln, " php", " pha",
                    " lda $4a", " cmp #2", " bne vinv", " lda #$a5", " bne vset",
                    "vinv", " lda #0",
                    "vset", " cpy #50", " bcs vb", " sta $0168", " bcc vdone",
                    "vb", " sta $0169",
                    "vdone", " pla", " plp", " jmp $9ff0"]
            i += 2; continue
        if ln.strip() == "ert * > $930d":
            # nowe procedury przed stałym punktem $930D (miejsce po usuniętych zapisach nieba)
            out += [
                "; Opus: skan od granicy nieba D = 152 - HD (wiersze 1..D-1 to niebo bez pikseli, wiersz 0 już sprawdzony)",
                "sky_go", " lda #152", " sec", " sbc $0100,y", " tax",
                " lda fs_lo,x", " sta $80", " lda fs_hi,x", " sta $81", " lda #0", " jmp ($80)",
                "fs_lo", " dta <fs_1," + ",".join(f"<fs_{r}" for r in range(1, 45)),
                "fs_hi", " dta >fs_1," + ",".join(f">fs_{r}" for r in range(1, 45)),
                "; Opus: łańcuch $55 dla pasa nieba, wiersze 47..1, A = $55, X = D; wyjście, gdy zapisany wiersz k <= D",
            ]
            for k in range(47, 0, -1):
                out += [f"bk{k}", f" sta ${0x1010 + 96 * k:04x},y"]
                if k % 4 == 0:
                    out += [f" cpx #{k}", f" bcc bkn{k}", " rts", f"bkn{k}"]
            out += [" rts"]
            out.append(ln); i += 1; continue
        out.append(ln); i += 1
    for r in range(1, 45):
        assert f"fs_{r}" in out, r
    open(f"{ROOT}/src/sky_b9.asm", "w").write("\n".join(out))


clear_bank(3, 6)
clear_bank(51, 8)
fill_bank()
print("zapisano src/sky_b6.asm, src/sky_b8.asm, src/sky_b9.asm")
