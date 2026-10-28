"""Generator źródeł łatek Fable (bank 2 potok rysowania + rzutowanie w banku 3).
Pisze src/fable_proj3.asm, src/fable_loop2.asm, src/fable_stub2.asm (woła go patches_fable.py przy budowie,
bo wyrównania zależą od zawartości ROM-u).

Układ:
  bank 2 $984C: jmp $8AF8 (lądowanie rzadkiej ścieżki widoczności z banku 3), $984F: lda #3 / sta $D500 (wejście
          rzutowania; pętla woła jsr $984F; następna instrukcja wykonuje się już z banku 3 pod $9854)
  bank 3 ..$9846: ścieżki rzadkie 1. współrzędnej (w zasięgu gałęzi z $9854), $9847: lda #2 / sta $D500
          (-> bank 2 $984C jmp $8AF8), $9854: główny tok rzutowania (dwa dzielenia wplecione), na końcu
          lda #2 / sta $D500 tak, by w banku 2 pod kolejnym adresem był bajt $60 (rts) - wyrównanie dobiera
          patches_fable.py; za przełącznikiem jeszcze bloki osiągane gałęziami z końca toku.
  bank 2 $85D4-$87D2 (stare rzutowanie; dzielenie $8224-$8303 też zwolnione): nowa pętla krawędzi, clipfast, kopie,
          skan końcowy; $885E: jmp $85D4.
"""
import os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def divsteps(tag):
    """8 kroków dzielenia Q = floor(256*R/D), R < D < $8000 (jak oryginał $8235-$8303, bez jsr/pha/pla).
    Wejście: A = R hi, $B0 = R lo, $AE/$AF = D. Wyjście: A = reszta hi, $B0 = reszta lo, $B2 = Q (rol co krok,
    C = bit ilorazu). Różnica wobec oryginału: młodszy bajt odejmowany od razu do $B0 (A chowane w Y), a rzadki
    nieudany krok (hi równe, lo za małe) cofany; X nietknięty (indeks punktu)."""
    out = []
    for i in range(8):
        out += [
            " asl $b0",
            " rol @",
            " cmp $af",
            f" bcc {tag}n{i}",
            " tay",
            " lda $b0",
            " sbc $ae",
            " sta $b0",
            " tya",
            " sbc $af",
            f" bcs {tag}n{i}",   # udane: C=1 -> bit 1
            " lda $b0",          # cofnięcie: lo + Dlo (C=0 po pożyczce) = stare lo
            " adc $ae",
            " sta $b0",
            " tya",
            " clc",              # bit 0
            f"{tag}n{i}",
            " rol $b2",
        ]
    return out


def gen_proj3(pad=0, rare_org=0x963A):
    """pad: liczba bajtów $FF wstawianych przed c2reload (przechodzą tam tylko jmp), tak by w banku 2 pod adresem
    ret+5 leżał bajt $60 (rts); rare_org: początek bloków rzadkich 1. współrzędnej, tak by kończyły się na $9847
    (muszą leżeć w zasięgu gałęzi z głowy rzutowania pod $9854). Oba dobiera patches_fable.py (etykiety RET, RAREEND)."""
    L = ["; Rzutowanie punktów terenu (oryginał bank 2 $85D4-$87D1 + dzielenie $8224) przeniesione do banku 3.",
         "; Generuje tools/gen_fable.py. Wejście: X = indeks punktu (0..44), bank 3 już wybrany (stub $984F w banku 2).",
         "; Wyjście jak oryginał: $2400/$242D/$245A/$2487,X; flaga $10 w $24B4,X; $9F = licznik przesunięć; $AE-$B2 jak po",
         "; oryginalnym drugim dzieleniu; $B5 scratch; X zachowany; + szybki test widoczności $8AF0 (rzadka ścieżka -> bank 2).",
         "; Powrót: lda #2 / sta $D500 -> bank 2 rts (adres dobiera patches_fable.py).",
         " opt h-",
         f" org ${rare_org:04x}",
         "; --- ścieżki rzadkie 1. współrzędnej (blisko głowy rzutowania pod $9854) ---",
         "c1ovf",            # 8 przesunięć: wynik stały ($B1 = |N1| hi już zapisane)
         " lda $22d2,x", " bmi c1ovfn", " lda #$40", " sta $242d,x", " lda #0", " sta $2400,x", " jmp c2reload",
         "c1ovfn", " lda #$c0", " sta $242d,x", " lda #0", " sta $2400,x", " jmp c2reload",
         "c1neg",            # |N1| dla N1 < 0; A = hi
         " sec", " lda #0", " sbc $22a4,x", " sta $b0", " lda #0", " sbc $22d2,x", " tay", " jmp c1cmp",
         "c1sh",             # normalizacja: D <<= 1 aż N < D; Y = hi N -> $B1, potem Y = licznik
         " sty $b1", " ldy #0",
         "c1shl", " asl $ae", " rol $af", " iny", " cpy #8", " beq c1ovf",
         " lda $b1", " cmp $af", " bcc c1divn", " bne c1shl", " lda $b0", " cmp $ae", " bcs c1shl", " lda $b1",
         "c1divn", " sty $9f", " jmp div1",
         "c1div0b", " tya", " jmp c1div0",
         "rareend",
         " ert * > $9847",
         " :($9847-*) dta $ff",
         "; $9847: rzadka ścieżka widoczności -> bank 2 $984C (jmp $8AF8); X = punkt, Y = $2276,X",
         " lda #2", " sta $d500",
         " :($984c-*) dta $ff",
         "pdisp", " jmp prolog3",                      # $984C: wejście prologu (C=1 przy jsr/jmp $984F)
         " :($984f-*) dta $ff",
         " lda #2", " sta $d500",                      # $984F: koniec prologu -> bank 2 $9854 (jmp $85D4, pętla)
         " :($9854-*) dta $ff",
         "; --- wejście: po stubie banku 2 pod $984F; C=0 rzutowanie (X = punkt), C=1 prolog $87D3 (X = $30/0) ---",
         "proj",
         " bcs pdisp",
         " lda $24b4,x", " ora #$10", " sta $24b4,x",
         " lda $2300,x", " sta $ae", " lda $232e,x", " sta $af",
         " lda $22d2,x", " bmi c1neg",
         " tay", " lda $22a4,x", " sta $b0", " tya",              # Y = hi N1 (dla c1sh/c1div0b)
         "c1cmp", " cmp $af", " bcc c1div0", " bne c1sh", " lda $b0", " cmp $ae", " bcc c1div0b", " bcs c1sh",
         "c1div0", " ldy #0", " sty $9f",
         "div1"] + divsteps("a") + [
         " ldy $9f", " bne c1yn",                     # (reszta hi z 1. dzielenia w $B1 martwa: 2. współrzędna nadpisuje)
         " lda $22d2,x", " bmi c1y0n",
         " lda $b2", " lsr @", " sec", " adc $b2", " ror @", " lsr @", " ora #$80", " sta $2400,x", " lda #0", " sta $242d,x",
         " jmp c2noreload",
         "c1yn",             # 1. współrzędna, licznik > 0: V = Q << n, wynik $80 +- 3V/8 (16 bitów)
         " lda #0",
         "c1ynl", " asl $b2", " rol @", " dey", " bne c1ynl",
         " sta $b5", " lsr @", " tay", " lda $b2", " ror @", " clc", " adc $b2", " sta $b2", " tya", " adc $b5",
         " lsr @", " ror $b2", " lsr @", " ror $b2", " sta $b5",
         " lda $22d2,x", " bmi c1ynn",
         " lda #$80", " clc", " adc $b2", " sta $2400,x", " lda $b5", " adc #0", " sta $242d,x", " jmp c2reload",
         "c1ynn", " lda #$80", " sec", " sbc $b2", " sta $2400,x", " lda #0", " sbc $b5", " sta $242d,x", " jmp c2reload",
         "c1y0n",            # 1. współrzędna, licznik 0, N < 0
         " lda $b2", " lsr @", " sec", " adc $b2", " ror @", " lsr @", " eor #$ff", " sec", " adc #$80", " sta $2400,x",
         " lda #0", " sta $242d,x", " jmp c2noreload",
         f" :{pad} dta $ff",                           # wyrównanie pod adres powrotu (tylko jmp przechodzą)
         "c2reload", " lda $2300,x", " sta $ae", " lda $232e,x", " sta $af",
         "c2noreload", " lda $2388,x", " bmi c2neg", " tay", " lda $235b,x", " sta $b0", " tya",  # Y = hi N2
         "c2cmp", " cmp $af", " bcc c2div0", " bne c2sh", " lda $b0", " cmp $ae", " bcc c2div0b", " bcs c2sh",
         "c2neg",
         " sec", " lda #0", " sbc $235b,x", " sta $b0", " lda #0", " sbc $2388,x", " tay", " jmp c2cmp",
         "c2sh",             # Y = hi N2 -> $B1 (stan jak oryginał, także po przepełnieniu), potem Y = licznik
         " sty $b1", " ldy #0",
         "c2shl", " asl $ae", " rol $af", " iny", " cpy #8", " beq c2ovf",
         " lda $b1", " cmp $af", " bcc c2divn", " bne c2shl", " lda $b0", " cmp $ae", " bcs c2shl", " lda $b1",
         "c2divn", " sty $9f", " jmp div2",
         "c2ovf",            # stan jak oryginał: $B1 = |N2| hi, $B2 bez zmian
         " lda $2388,x", " bmi c2ovfn", " lda #$40", " sta $2487,x", " lda #0", " sta $245a,x", " jmp adjust",
         "c2ovfn", " lda #$c0", " sta $2487,x", " lda #0", " sta $245a,x", " jmp adjust",
         "c2div0b", " tya",
         "c2div0", " ldy #0", " sty $9f",
         "div2"] + divsteps("b") + [
         " sta $b1",
         " ldy $9f", " beq c2y0", " jmp c2yn",
         "c2y0",
         " lda #0", " sta $2487,x", " lda $2388,x", " bmi c2y0n",
         " lda $b2", " lsr @", " sec", " adc $b2", " ror @", " lsr @", " ora #$80", " sta $245a,x",
         "adjust",                                     # oryginał $8792: poprawka Y z tabeli $270E wg X ekranu
         " lda $242d,x", " bne adjx",                  # hi X ekranu <> 0: rzadko (adjx za przełącznikiem)
         " lda $2400,x", " lsr @", " lsr @", " lsr @", " tay", " lda $270e,y", " bmi adjm",
         "adjp", " clc", " adc $245a,x", " sta $245a,x", " lda $2487,x", " adc #0", " sta $2487,x",
         "vis",                                        # oryginał $8AF0: szybki test widoczności
         " ldy $2276,x", " lda $0a00,y", " bne rare",
         "ret",
         " lda #2", " sta $d500",                      # -> bank 2: pod ret+5 musi być rts (sprawdza patches_fable.py)
         "retend",
         "; --- za przełącznikiem (bank 3; wykonanie trafia tu tylko gałęziami z c2y0/adjust/vis) ---",
         "c2y0n",
         " lda $b2", " lsr @", " sec", " adc $b2", " ror @", " lsr @", " eor #$ff", " sec", " adc #$80", " sta $245a,x",
         " jmp adjust",
         "adjx", " bmi adjneg", " lda $272d", " bmi adjm", " bpl adjp",
         "adjneg", " lda $270e", " bmi adjm", " bpl adjp",
         "adjm", " clc", " adc $245a,x", " sta $245a,x", " lda $2487,x", " adc #$ff", " sta $2487,x", " jmp vis",
         "rare", " jmp $9847",
         "c2yn",
         " lda #0",
         "c2ynl", " asl $b2", " rol @", " dey", " bne c2ynl",
         " sta $b5", " lsr @", " tay", " lda $b2", " ror @", " clc", " adc $b2", " sta $b2", " tya", " adc $b5",
         " lsr @", " ror $b2", " lsr @", " ror $b2", " sta $b5",
         " lda $2388,x", " bmi c2ynn",
         " lda #$80", " clc", " adc $b2", " sta $245a,x", " lda $b5", " adc #0", " sta $2487,x", " jmp adjust",
         "c2ynn", " lda #$80", " sec", " sbc $b2", " sta $245a,x", " lda #0", " sbc $b5", " sta $2487,x", " jmp adjust",
         "; --- prolog rysowania terenu (oryginał $87D3-$885D), wejście przez pdisp; X = $30 albo 0 ---",
         "; tabela $3920-$39D7 i $270E-$272D ($91E0) rozwinięte w banku 14 (fable_pro14.asm), wypełnienia $263A-$26E1 tu.",
         f" ert * > ${HOP - 2:04x}",
         f" :(${HOP - 2:04x}-*) dta $ff",             # wyrównanie PRZED kodem (bajty $FF to nielegalne ISC, nie wolno w nie wpaść)
         "prolog3",
         " stx $a7",
         "hop14", " lda #14", " sta $d500",            # -> bank 14 $HOP+5: jmp $9950; powrót z banku 14 pod hop14+5
         ] + [f" lda #${v:02x}" if v is not None else f" sta ${a:04x}" for v, a in fill_seq()] + [
         " lda $28", " sta $2907", " lda $29", " sta $2908",
         " lda #$80", " sta $28e7", " sta $28e8", " sta $2912", " sta $2913", " sta $2914", " sta $2915",
         " ldy $a7", " bne pro1", " sta $28ea", " sta $79",
         "pro1", " lda #0", " sta $28ed", " sta $28fb", " sta $28fc",
         " lda $6a", " bmi pro2", " inc $28fc",
         "pro2", " jmp $984f",                          # -> bank 2 $9854: jmp $85D4 (nowa pętla krawędzi)
         " ert * > $9ff0",
         ]
    return "\n".join(L) + "\n"


HOP = 0x9D80  # bank 3: lda #14 / sta $D500 (skok do banku 14); bank 14 pod HOP: powrót do banku 3, HOP+5: jmp $9950


def fill_seq():
    """Wypełnienie jak oryginał $8802-$8821: $263A-$264D i $26CE-$26E1 = $67, potem $264E-$26D1 = $6B
    (nadpisuje $26CE-$26D1) -> łącznie $263A-$264D $67, $264E-$26D1 $6B, $26D2-$26E1 $67. (wartość, None) = lda #."""
    seq = [(0x67, None)] + [(None, a) for a in range(0x263A, 0x264E)]
    seq += [(0x6B, None)] + [(None, a) for a in range(0x264E, 0x26D2)]
    seq += [(0x67, None)] + [(None, a) for a in range(0x26D2, 0x26E2)]
    return seq


def gen_pro14():
    """Bank 14 $9950-$9DFF: tabela $3920-$39D7 (46 grup po 4 bajty X0+k, jak $87D8-$87FA) i tabela perspektywy
    $270E-$272D (jak $91E0-$9213, młodszy bajt akumulatora w X zamiast $B5, na końcu $B5 jak oryginał)."""
    L = ["; Bank 14: rozwinięty prolog rysowania terenu (tabela kolumn $3920-$39D7, tabela $270E-$272D). Generuje",
         "; tools/gen_fable.py. Wejście z banku 3 (hop14) przez jmp $9950, X = $30 albo 0; powrót: jmp hop14 w banku 14 =",
         "; lda #3 / sta $D500, dalej bank 3 pod hop14+5.",
         " opt h-", " org $9950"]
    for g in range(46):
        L += [" txa"] + [f" sta ${0x3920 + 4 * g + i:04x}" for i in range(4)] + [" inx"]
    L += [" txa", " clc", " adc #$2e", " sta $b3"]
    L += [" lda $a6", " sta $271e", " ldx #0"]
    for k in range(15):
        L += [" txa", " clc", " adc $a5", " tax", f" lda ${0x271e + k:04x}", " adc $a4", f" sta ${0x271f + k:04x}"]
    L += [" ldx #0"]
    for k in range(15, -1, -1):
        L += [" txa", " sec", " sbc $a5", " tax", f" lda ${0x270f + k:04x}", " sbc $a4", f" sta ${0x270e + k:04x}"]
    L += [" stx $b5", f" jmp ${HOP:04x}",
          f" ert * > ${HOP:04x}", f" :(${HOP:04x}-*) dta $ff",
          " lda #3", " sta $d500",                      # HOP: powrót do banku 3 (hop14+5)
          " jmp $9950",                                 # HOP+5: lądowanie z banku 3
          " ert * > $9dff"]
    return "\n".join(L) + "\n"


def gen_epi2():
    """Bank 2 $8861 (stara pętla krawędzi, martwa po jmp pod $885E): pętla epilogu $89A1-$89B4 rozwinięta 4x, $271E w X."""
    L = ["; Pętla $89A1 ($28B6,Y = ($271E - $270E,Y) / 2 z zaokrągleniem, Y = 31..0) rozwinięta 4x; $89A1: jmp $8861.",
         "; Generuje tools/gen_fable.py. X wolny (po pętli nikt go nie czyta przed zapisem).",
         " opt h-", " org $8861",
         " ldx $271e", " ldy #$1f",
         "elp"]
    for _ in range(4):
        L += [" sec", " txa", " sbc $270e,y", " cmp #$80", " ror @", " adc #0", " sta $28b6,y", " dey"]
    L += [" bpl elp", " jmp $89b5", " ert * > $88e8"]
    return "\n".join(L) + "\n"


def gen_loop2():
    L = ["; Nowa pętla krawędzi terenu (oryginał bank 2 $885E-$88E7) w miejscu starego rzutowania $85D4-$87D2,",
         "; szybki clipping bez kopiowania p2 do $25B4/$25D2/$25F0/$24E2/$23E2 (czyta wprost z tablic po X = p2),",
         "; kopie tylko dla ścieżek ogólnych i na końcu dla ostatniej krawędzi, która przeszła oba testy (stan RAM jak",
         "; w oryginale). Generuje tools/gen_fable.py.",
         " opt h-",
         " org $85d4",
         "newloop",
         " ldy #0",
         " sty $28db",                                                              # 0 = jeszcze żadna para nie przeszła
         "lp",
         " ldx $9b09,y", " iny", " lda $24b4,x", " and #$a0", " bne skip1",         # p1: bit 7 albo 5 -> pomiń parę
         " ldx $9b09,y", " iny", " sty $272e", " lda $24b4,x", " cmp #$40", " bcs next",  # p2: bit 7 albo 6 -> pomiń
         " sty $28db",                                                              # indeks za p2 ostatniej pary z oboma testami
         " and #$10", " bne p2ok", " jsr $984f", " ldy $272e",                      # rzutowanie p2 (bank 3)
         "p2ok",
         " ldx $9b07,y", " lda $24b4,x", " and #$10", " bne p1ok", " clc", " jsr $984f", " ldy $272e",  # C=0: rzutowanie (p2: C=0 po bcs)
         "p1ok",
         " lda $2400,x", " sta $82", " lda $242d,x", " sta $83", " lda $245a,x", " sta $84",
         " lda $2487,x", " sta $85", " lda $23b5,x", " sta $86",
         " ldx $9b08,y", " jsr clipfast", " ldy $272e",
         " cpy #$90", " bne lp", " beq fin",
         "skip1", " iny",
         "next", " cpy #$90", " bne lp",
         "fin",
         "; ostatnia para, która przeszła oba testy -> kopie p2 jak w oryginale ($28DB = indeks za jej p2, 0 = brak);",
         "; potem $28DB = p1 ostatniej pary tablicy (oryginał pisze tam p1 każdej pary, więc na końcu zawsze 43)",
         " ldy $28db", " beq done", " ldx $9b08,y", " jsr copies",
         "done", " lda #43", " sta $28db", " jmp $88e8",
         "; clipping (oryginał jsr $9627 z X=0), wejście z pętli: X = p2, $82-$86 = p1; hi x1,y1,x2,y2 = 0 -> szybka",
         "; ścieżka bez kopii p2 do $25B4..; inaczej kopie i oryginalny kod",
         "clipfast",
         " lda $83", " ora $85", " ora $242d,x", " ora $2487,x", " bne cgen",
         " lda $82", " cmp $2400,x", " bcs crts",                                  # x1 >= x2: nic
         " ldy #$14", " sty $9f",
         " cmp #$d8", " bcs crts",                                                  # A = $82
         " lda $84", " cmp #$6c", " bcc cy1lt",
         " lda $245a,x", " cmp #$6c", " bcc c974a",
         " sta $ea", " lda $2400,x", " sta $95", " lda $23b5,x", " sta $f4",        # jak $9788
         " ldx #0", " jmp $982a",                                                   # rasteryzacja (bank 5), rts ($9907) wprost do pętli
         "cy1lt", " lda $245a,x", " cmp #$6c", " bcc crts", " jsr copies", " ldx #0", " jmp $972e",
         "c974a", " jsr copies", " ldx #0", " jmp $974a",
         "cgen",                                                                    # jak $9627: x1 < x2 (16 bitów ze znakiem), potem $83BB
         " lda $2400,x", " sta $25b4", " lda $242d,x", " sta $25d2", " lda $245a,x", " sta $25f0",
         " lda $2487,x", " sta $24e2", " lda $23b5,x", " sta $23e2",
         " lda $25d2", " eor #$80", " sta $b5", " lda $83", " eor #$80", " cmp $b5", " bne cg1",
         " lda $82", " cmp $25b4",
         "cg1", " bcs crts",
         " ldx #0", " jmp $83bb",
         "crts", " rts",
         "copies",
         " lda $2400,x", " sta $25b4", " lda $242d,x", " sta $25d2", " lda $245a,x", " sta $25f0",
         " lda $2487,x", " sta $24e2", " lda $23b5,x", " sta $23e2", " rts",
         " ert * > $87d3",
         ]
    return "\n".join(L) + "\n"


def gen_stub2():
    return "\n".join([
        "; Bank 2 $984C-$9853 (dziura FF): lądowanie rzadkiej ścieżki widoczności z banku 3 i wejście rzutowania.",
        "; Generuje tools/gen_fable.py.",
        " opt h-", " org $984c",
        " jmp $8af8",                 # $984C: po przełączeniu z banku 3 ($9847) ciąg dalszy oryginalnego $8AF0
        " lda #3", " sta $d500",      # $984F: jsr z pętli (C=0) albo jmp z $87D3 (C=1); dalej bank 3 $9854 (proj)
        " jmp $85d4",                 # $9854: koniec prologu (bank 3 $984F) -> nowa pętla krawędzi
        " ert * <> $9857",
    ]) + "\n"


if __name__ == "__main__":
    open(f"{ROOT}/src/fable_proj3.asm", "w", encoding="utf-8").write(gen_proj3())
    open(f"{ROOT}/src/fable_loop2.asm", "w", encoding="utf-8").write(gen_loop2())
    open(f"{ROOT}/src/fable_stub2.asm", "w", encoding="utf-8").write(gen_stub2())
    open(f"{ROOT}/src/fable_pro14.asm", "w", encoding="utf-8").write(gen_pro14())
    open(f"{ROOT}/src/fable_epi2.asm", "w", encoding="utf-8").write(gen_epi2())
    print("zapisano src/fable_proj3.asm, fable_loop2.asm, fable_stub2.asm, fable_pro14.asm, fable_epi2.asm")
